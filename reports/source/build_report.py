"""Rebuild InterviewRecall against the corrected 45-page sample, retaining its PDF geometry.
Run from project root: PYTHONPATH=/private/tmp/ir-report-libs python3 reports/source/build_report.py
Dependencies: PyMuPDF, ReportLab, Pillow. Source template: ../../sample_report.pdf.
"""
from pathlib import Path
from collections import Counter
from xml.sax.saxutils import escape
import io,json,re,math
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT,TA_CENTER,TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports';A=OUT/'assets'
M=json.loads((OUT/'source/reference-metrics.json').read_text())
W,H=595.2,841.92;FONTS=Path('/System/Library/Fonts/Supplemental')
for name,file in [('TNR','Times New Roman.ttf'),('TNRB','Times New Roman Bold.ttf'),('TNRI','Times New Roman Italic.ttf'),('TNRBI','Times New Roman Bold Italic.ttf'),('CN','Courier New.ttf')]:pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNRB',italic='TNRI',boldItalic='TNRBI')
FIG={
'1.1':'Release plan of InterviewRecall',
'2.1':'Revision scheduling pipeline and account update flow',
'2.2':'Recall request and response contract',
'2.3':'Recorded backend scheduler results (7 passed)',
'2.4':'Student journey and revision flow',
'2.5':'Authentication screens: (a) login and (b) registration',
'2.6':'Preparation overview and daily revision entry point',
'2.7':'Focused recall before the approach is revealed',
'2.8':'Personal problem library and confidence summaries',
'2.9':'Revision reminder panel',
'2.10':'Daily revision queue',
'2.11':'Recall performance and topic confidence',
'2.12':'Account preferences and data export',
'2.13':'Mistake notebook',
'2.14':'Problem capture and approach notes',
'2.15':'Automated frontend scheduler tests (4 passed)',
'2.16':'System architecture diagram of InterviewRecall',
'2.17':'Entity-relationship diagram of the account database',
'2.18':'JPA schema mapping configured for MySQL',
'2.19':'Sequence of review completion and rescheduling',
'2.20':'Private demo hosting and local account architecture',
'2.21':'Preparation dashboard with due problems and focus topic',
'2.22':'Preparation analytics and recall history',
'2.23':'Recorded backend results: 10 tests, 0 failures',
'3.1':'Implemented story coverage by review work package',
'B.1':'Source evidence: owner-scoped problem selection',
'B.2':'Source evidence: review history and schedule update'}
TAB={'1.1':'Project objectives','1.2':'Product vision summary','1.3':'Product backlog of InterviewRecall','1.4':'Team roles and responsibilities','2.1':'Detailed user stories of Sprint 1','2.2':'Sprint 1 task breakdown and ownership','2.3':'Access level authorization matrix of the revision service','2.4':'Request and response fields of the review endpoint','2.5':'Detailed functional test cases of Sprint 1','2.6':'Sprint 1 progress review checklist','2.7':'Sprint 1 retrospective','2.8':'Detailed user stories of Sprint 2','2.9':'Sprint 2 task breakdown and ownership','2.10':'Recall grades and revision intervals','2.11':'Design tokens used in the user interface','2.12':'Detailed functional test cases of Sprint 2','2.13':'Sprint 2 progress review checklist','2.14':'Sprint 2 retrospective','2.15':'Detailed user stories of Sprint 3','2.16':'Sprint 3 task breakdown and ownership','2.17':'Authorization matrix of the InterviewRecall backend','2.18':'Mapping between browser grades and scheduling state','2.19':'Detailed functional test cases of Sprint 3','2.20':'Sprint 3 progress review checklist','2.21':'Sprint 3 retrospective','3.1':'Objectives versus outcomes','3.2':'Deterministic scheduling examples and bounds','3.3':'Summary of automated and browser checks','3.4':'Sprint-wise implementation scope summary'}
REPL={'PrePlate':'InterviewRecall','AI Forecasting Service':'Revision Scheduling Service','Forecasting Model Results':'Revision Scheduling Results','forecasting service':'revision service','Stand-up log':'Progress review checklist','MySQL Workbench showing the preplate_db schema':'JPA schema mapping configured for MySQL','B.1 Forecasting service (FastAPI): request contract and validation':'B.1 Revision service: request contract and validation','B.2 Frontend: student home page (StudentHomePage.jsx)':'B.2 Frontend: preparation overview and queue selection','B.3 Frontend: admin dashboard page (AdminDashboardPage.jsx)':'B.3 Frontend: focused recall and review submission','B.5 Backend: schedule service and notification scheduler':'B.5 Backend: deterministic revision scheduler','B.6 Backend: forecast service with ML client and fallback':'B.6 Backend: transactional review service','B.7 Backend: heuristic fallback forecaster':'B.7 Backend: session authentication and ownership','B.9 Database evidence: stored meals and forecasts':'B.9 Persistence evidence: repository and transaction source'}

def replace(t):
 if t.strip() in REPL:return REPL[t.strip()]
 for a,b in REPL.items():t=t.replace(a,b)
 return t

def fontname(s):
 f=s['font'];return 'CN' if 'Courier' in f else 'TNRBI' if 'BoldItalic' in f else 'TNRB' if 'Bold' in f else 'TNRI' if 'Italic' in f else 'TNR'

def original_text_lines(page):
 return [l for b in M['layout'][page-1]['blocks'] for l in b['lines'] if any(s['text'].strip() for s in l['spans'])]

BUF=io.BytesIO();c=canvas.Canvas(BUF,pagesize=(W,H));FAIL=[];CHECK=[]
def text_at(t,x,y,size=12,font='TNR',center=False):
 c.setFont(font,size)
 if center:c.drawCentredString(x,H-y,t)
 else:c.drawString(x,H-y,t)

def paragraph(t,x,y,width,maxheight,size=12,leading=18.6,font='TNR',align=TA_JUSTIFY,key=''):
 # y is the first baseline, measured from the top, as in the original Word PDF.
 style=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,alignment=align,splitLongWords=False)
 p=Paragraph(t,style);_,h=p.wrap(width,2000)
 lines=len(p.blPara.lines)
 if h>maxheight+.8:FAIL.append({'key':key,'height':round(h,1),'allowed':round(maxheight,1),'lines':lines,'text':t[:100]})
 p.drawOn(c,x,H-(y-size)-h)
 CHECK.append({'key':key,'x':round(x,2),'first_baseline':round(y,2),'font_size':size,'leading':round(leading,2),'height':round(h,2)})

def copy_line(l,t=None,center=False):
 ss=[s for s in l['spans'] if s['text'].strip()]
 if not ss:return
 s=ss[0];t=t if t is not None else ''.join(v['text'] for v in l['spans']).strip()
 if t:text_at(t,299.1 if center else s['origin'][0],s['origin'][1],s['size'],fontname(s),center)

def caption(t):
 m=re.match(r'^(Figure|Table)\s+([A-Z0-9]+\.\d+)',t)
 return f'{m[1]} {m[2]} '+(FIG if m[1]=='Figure' else TAB).get(m[2],'') if m else replace(t)

STORIES=[
'Define the recall state, four grades, and explainable scheduling rules.',
'Implement calendar-day helpers and account timezone handling.',
'Implement Again reset behavior and the minimum ease factor.',
'Implement Good learning steps and adaptive interval growth.',
'Implement Hard and Easy adjustments with interval bounds.',
'Expose review completion through a validated Java API.',
'Test scheduling boundaries and preserve atomic review history.',
'Create the reference-based visual system and reusable components.',
'Provide account registration and login dialogs with validation.',
'Build the overview, daily goal, due preview, and focus card.',
'Provide a searchable problem library and editable approach notes.',
'Build the hidden-note recall session and interval previews.',
'Provide analytics, revision reminders, and a mistake notebook.',
'Provide settings, JSON export, and responsive navigation.',
'Define account, problem, and revision entities with JPA mappings.',
'Implement session authentication, BCrypt, logout, and CSRF.',
'Enforce account ownership on all private problem operations.',
'Validate problem fields and return consistent API errors.',
'Persist preferences and return owner-scoped revision history.',
'Connect the browser API adapter, local proxy, and demo boundary.',
'Run recorded checks, publish the private static demo, and document setup.']
T={}
def table(page,index,rows):T[(page,index)]=rows
# Each table uses the original cell rectangles, borders, column widths, and row heights.
table(8,0,[['ACRONYM','ABBREVIATION']]+[[a,b] for a,b in [('API','Application Programming Interface'),('BCrypt','Adaptive password hashing algorithm'),('CSRF','Cross-Site Request Forgery'),('CRUD','Create, Read, Update, Delete'),('DB','Database'),('ER','Entity-Relationship'),('HTTP(S)','Hypertext Transfer Protocol (Secure)'),('JDBC','Java Database Connectivity'),('JSON','JavaScript Object Notation'),('JPA','Jakarta Persistence API'),('DTO','Data Transfer Object'),('MVP','Minimum Viable Product'),('MoSCoW','Must, Should, Could, and Won’t have'),('REST','Representational State Transfer'),('SM-2','SuperMemo 2 scheduling algorithm'),('SDG','Sustainable Development Goal'),('SPA','Single Page Application'),('SQL','Structured Query Language'),('TC','Test Case'),('UI','User Interface'),('US','User Story')]])
table(10,0,[['No.','Objective','Success indicator'],['O1','Support personal registration and session login.','Private account data; invalid credentials return 401.'],['O2','Capture problem links, approaches, and mistake notes.','Library supports search, edit, delete, and export.'],['O3','Bring back due and overdue learning items.','Queue prioritizes earlier due dates and weak confidence.'],['O4','Calculate explainable adaptive review intervals.','Four grades produce bounded deterministic dates.'],['O5','Promote recall before reading saved notes.','Approach stays hidden until the reveal control.'],['O6','Show progress and topic confidence.','Analytics and notebook derive from stored records.'],['O7','Deliver a tested and documented prototype.','Build, 14 tests, browser checks, private static demo.']])
table(11,0,[['Audience','Primary: students preparing for coding interviews. Secondary: academic reviewers and developers inspecting the learning workflow and Java architecture.'],['Needs','A quick way to save solved problems; a clear daily queue; active recall before notes; understandable scheduling; a mistake notebook; and useful preparation analytics.'],['Products','React/Vite application, Spring Boot account API, JPA/MySQL configuration, scheduler tests, private browser-local demo, and setup documentation.'],['Values','Sustained recall with limited daily effort. Differentiators: four-grade interval previews, mistake-centered notes, transparent account ownership, and explicit demo boundaries.']])
backlog=[['S.No','User story','Sprint','Priority','Pts']]+[[f'US {i+1}',STORIES[i],str(i//7+1),'Must','—'] for i in range(21)]
table(12,0,backlog[:19]);table(13,0,[backlog[0]]+backlog[19:])
table(13,1,[['Area','Student 1 (Bhanu)','Student 2 (Poorna)','Student 3 (Pranav)'],['Role','Backend and scheduler review.','Frontend and workflow review.','Integration and report review.'],['Focus','Accounts, security, scheduling.','Screens, notes, analytics.','API integration and evidence.'],['Verification','Java tests and owner isolation.','Browser checks and figures.','Setup and report layout.'],['Shared','Source and limitations.','Names and references.','Submission evidence.']])
for page,start in [(14,0),(20,7),(28,14)]:table(page,0 if page!=28 else 1,[['S.No','Detailed user story','Owner','Pts']]+[[f'US {j+1}',STORIES[j],{0:'Bhanu',7:'Poorna',14:'Pranav'}[start],'—'] for j in range(start,start+7)])
table(14,1,[['Task','Owner','Est. (days)','Status']]+[[x,'Bhanu','—','Done'] for x in ['Define four recall grades and schedule state','Separate pure scheduling from persistence','Implement Again reset and ease floor','Implement Good one-day and six-day steps','Implement Hard and Easy adjustments','Handle timezone dates and overdue work','Add service transaction and history mapping','Review scheduler boundary tests']])
table(16,0,[['Caller','Access level'],['Authenticated account','May review only a problem owned by that account.'],['Unauthenticated caller','Private API access is rejected with HTTP 401.'],['Other account','An unrelated problem is not found; ownership cannot be supplied by the client.']])
table(17,0,[['Direction','Field','Description'],['Request','problem ID','Identifies the owned problem in the endpoint path.'],['Request','grade: 0, 1, 2, or 3','Again, Hard, Good, or Easy recall assessment.'],['Request','session cookie and CSRF token','Authenticate the account and protect the mutation.'],['State','intervalDays, repetitions, ease','Current scheduling values loaded by the service.'],['Response','nextReviewOn, intervalDays','New due date and bounded interval in days.'],['Response','repetitions, ease','Updated successful attempts and ease factor.'],['Response','confidence','Latest grade mapped to a user-reported indicator.'],['History','reviewedAt and scheduledOn','UTC attempt time and former calendar due date.']])
table(18,0,[['TC ID','Story','Test scenario and input','Expected result','Status'],['TC-1.1','US 3','Again after a long successful interval.','One day; repetitions reset; ease floor.','Pass'],['TC-1.2','US 4','Good on first and second success.','Learning intervals of one and six days.','Pass'],['TC-1.3','US 4','Good after six days at ease 2.5.','Next interval is fifteen days.','Pass'],['TC-1.4','US 5','Hard with prior repetitions.','Count preserved; ease never below 1.3.','Pass'],['TC-1.5','US 5','Easy with a large previous interval.','Ease and interval obey upper bounds.','Pass'],['TC-1.6','US 2','Review across a year boundary.','Correct future calendar date.','Pass'],['TC-1.7','US 2','Timezone differs from UTC date.','Use the account-local calendar day.','Pass'],['TC-1.8','US 6','Grade outside the accepted range.','Invalid grade is rejected.','Pass']])
for page,idx,n in [(19,0,1),(27,1,2),(35,0,3)]:
 scope={1:['State and grades','Date boundaries','Again behavior','Good progression','Hard/Easy limits','Scheduler tests'],2:['Design tokens','Account dialogs','Overview and queue','Library and focus','Analytics and notes','Responsive review'],3:['Entity mappings','Session and CSRF','Owner isolation','Browser API adapter','Build and checks','Private publication']}[n]
 table(page,idx,[['Review','Bhanu (backend)','Poorna (frontend)','Pranav']]+[[str(k+1),f'Review {v.lower()}.',f'Check visible {v.lower()}.','Review evidence.'] for k,v in enumerate(scope)])
table(19,1,[['What went well','What did not go well','Action items for Sprint 2'],['Pure scheduling rules are easy to inspect and test. Calendar days avoid elapsed-time ambiguity.','Self-reported grades are not calibrated retention probabilities. Live MySQL remains unverified.','Keep grade labels explicit. Show interval previews. Preserve hidden notes until the student reveals them.']])
table(20,1,[['Task','Owner','Est. (days)','Status']]+[[x,'Poorna','—','Done'] for x in ['Set palette, Archivo type, and glass surfaces','Build desktop sidebar and mobile drawer','Create overview and daily goal cards','Build problem capture and library controls','Implement reveal-first recall workflow','Implement analytics and activity grid','Create notebook and account settings','Add export and clear empty/error states','Check responsive bounds in Chrome']])
table(21,0,[['Grade','Recall meaning','Next interval','Confidence'],['Again','Approach forgotten','1 day','20%'],['Hard','Recall with effort','Previous × 1.2','45%'],['Good','Approach recalled','1, 6, then × ease','75%'],['Easy','Confident recall','4 initially; then grow','95%']])
table(22,0,[['Token','Value','Use'],['Forest green','#0E2E28','Main text, primary actions, and hero background.'],['Lime','#CDFA8A','Primary revision action and restrained emphasis.'],['Mint','#E6F0ED','Calm supporting surfaces and subtle depth.'],['Pale background','#F4F9F8','Workspace background and translucent cards.'],['Error red','#B71C1C','Actionable form and API errors.'],['Typeface','Archivo','Application typography; report keeps the sample’s Times New Roman.']])
f2=[['TC ID','Story','Test scenario and input','Expected result','Status'],['TC-2.1','US 11','Add a title, URL, approach, and lesson.','Problem appears in the library.','Pass'],['TC-2.2','US 11','Search for the newly saved title.','Only the matching record remains.','Pass'],['TC-2.3','US 12','Open focus mode before reveal.','Saved approach is hidden.','Pass'],['TC-2.4','US 12','Select Reveal my approach.','Saved explanation becomes visible.','Pass'],['TC-2.5','US 12','Grade a new problem Easy.','Four-day interval is confirmed.','Pass'],['TC-2.6','US 11','Reload and edit the saved approach.','Change persists; interval stays four days.','Pass'],['TC-2.7','US 11','Delete the matching problem.','The record disappears from search.','Pass'],['TC-2.8','US 14','Open the mobile navigation drawer.','Revision queue is reachable.','Pass'],['TC-2.9','US 13','Navigate analytics and notebook.','Corresponding screens render.','Pass'],['TC-2.10','US 14','Check widths 375/768/1024/1440.','No document horizontal overflow.','Pass']]
table(26,0,f2[:8]);table(27,0,[f2[0]]+f2[8:])
table(28,0,[['What went well','What did not go well','Action items for Sprint 3'],['One design system connects all screens. The explicit demo label makes persistence limits visible.','A hidden table label caused tablet overflow during development and was corrected.','Verify owner scoping and CSRF. Preserve schedules during editing. Test the browser-to-server contract.']])
table(28,2,[['Task','Owner','Est. (days)','Status']]+[[x,'Pranav','—','Done'] for x in ['Create account/problem/revision JPA entities','Implement BCrypt registration and login','Protect sessions and CSRF mutations','Scope queries to the authenticated owner','Validate DTOs and centralize error messages','Persist review history in one transaction','Connect frontend transport and local proxy','Document database setup and demo limits']])
table(29,0,[['Task','Owner','Est. (days)','Status'],['Build, tests, private static publication, and README','All three','—','Done']])
table(29,1,[['Operation','Guest','Account'],['Register, login, CSRF token','Yes','Yes'],['Read personal problems and history','No','Own only'],['Create, edit, or delete problems','No','Own only'],['Complete a revision','No','Own only'],['Read or update preferences','No','Own only'],['Explore the browser-local demo','Yes','Separate mode']])
table(32,0,[['Browser value','Service interpretation','Note'],['Again / 0','Reset successful repetitions','One-day return.'],['Hard / 1','Preserve repetitions; lower ease','Interval grows slowly.'],['Good / 2','Advance successful learning steps','1 day, 6 days, then multiply.'],['Easy / 3','Advance and increase ease','Four days initially.'],['Date and history','Account zone / UTC instant','Calendar schedule, timestamp history.']])
table(34,0,[['TC ID','Story','Test scenario and input','Expected result','Status'],['TC-3.1','US 16','Register and log in to an account.','Account returned; valid session.','Pass'],['TC-3.2','US 16','Submit incorrect credentials.','HTTP 401; generic login error.','Pass'],['TC-3.3','US 17','Read a second account’s library.','No first-account problems are returned.','Pass'],['TC-3.4','US 17','Review another account’s problem.','HTTP 404; no state change.','Pass'],['TC-3.5','US 17','Update another account’s problem.','HTTP 404; no update.','Pass'],['TC-3.6','US 17','Delete another account’s problem.','HTTP 404; no deletion.','Pass'],['TC-3.7','US 18','Submit a grade outside 0–3.','HTTP 400 validation error.','Pass'],['TC-3.8','US 16','Mutate without a CSRF token.','HTTP 403; request forbidden.','Pass'],['TC-3.9','US 19','Review and retrieve attempt history.','New interval and stored revision.','Pass'],['TC-3.10','US 16','Sign out through the logout endpoint.','Session invalidated; HTTP 204.','Pass']])
table(35,1,[['What went well','What did not go well','Action items (future work)'],['DTO boundaries and owner queries make behavior inspectable. Review history and schedule share one transaction.','Live MySQL and public full-stack hosting were not exercised. Session persistence remains local.','Add migrations, durable sessions, recovery, rate limits, and broader database and browser validation.']])
table(36,0,[['Objective','Outcome achieved','Evidence'],['O1 Personal account','Session registration/login, BCrypt, CSRF and private record access.','Figure 2.5; API tests'],['O2 Problem library','Saved approaches, lessons, search, filters, edit, delete, and export.','Figures 2.8, 2.14'],['O3 Daily queue','Due and overdue problems with direct revision entry.','Figures 2.6, 2.10'],['O4 Adaptive dates','Bounded four-grade schedule with deterministic steps.','Figures 2.1–2.3'],['O5 Active recall','Saved explanation stays hidden until revealed.','Figure 2.7'],['O6 Progress and lessons','Recall analytics, topic indicators, and mistake notebook.','Figures 2.11, 2.13'],['O7 Reviewable result','14 tests, browser checks, production build, and private demo.','Figures 2.15, 2.23']])
table(37,0,[['Starting state','Grade','Interval','Repeats','Ease','Limit'],['New: 1 day / r=0','Again','1 day','0','2.30','≥ 1.3'],['New: 1 day / r=0','Good','1 day','1','2.50','≤ 365'],['1 day / r=1','Good','6 days','2','2.50','≤ 365'],['6 days / r=2','Good','15 days','3','2.50','≤ 365'],['6 days / r=2','Easy','17 days','3','2.65','≤ 3.0']])
table(37,1,[['Level','Tools','Scope','Result'],['Frontend','Node test runner','Reset, steps, bounds, date helpers.','4 passed'],['Scheduler','JUnit 5','Calendar and grading rules.','7 passed'],['Integration','Spring MockMvc, H2','Accounts, ownership, persistence, CSRF.','3 passed'],['Browser','Playwright, Chrome','Core workflows and four widths.','Passed']])
table(38,0,[['Sprint','Stories\nreviewed','Stories\ndelivered','Points\nplanned','Points\nrecorded'],['1: Scheduler','7','7','—','—'],['2: Frontend','7','7','—','—'],['3: Integration','7','7','—','—'],['Total','21','21','—','—']])
table(41,0,[['1. Title of the invention','System and method for adaptive coding-problem revision using recall grades and personal learning records.'],['2. Inventor(s)','Bhanu Prakash Kusha (RA2311003011898); Poorna Chandra Varri (RA2311003011910); Pranav Pathak (RA2311003011900).'],['3. Field of the invention','Educational productivity software; coding interview preparation; full-stack web applications and spaced repetition.'],['4. Problem addressed','Solved problems and scattered notes do not identify which approaches a student can still recall. A daily review queue and stored lessons close that gap.'],['5. Brief description','The student saves a problem and approach, attempts recall before revealing notes, selects one of four grades, and receives an updated review date. The backend stores account-scoped problems and review history.'],['6. Novelty / differentiation','A practical combination of coding-pattern notes, mistake reflection, interval previews, and a task-first interface. This is a project description, not a claim of patentable novelty or an exclusive invention.'],['7. Applications / advantages','Personal interview preparation, regular recall practice, reviewable topic indicators, and undergraduate demonstration of secure Java/React integration.'],['8. Stage of development','Working academic prototype; private static demo published. Java account service runs separately; live MySQL verification remains future work.'],['9. Disclosure to others','Private demo: https://interview-recall-studio.cloudlessboat4.chatgpt.site . AI-assisted development and report preparation; frameworks and design references are acknowledged.']])
# Narrative text is fitted into the original Word paragraph frames without changing font size.
N={
9:[
'InterviewRecall is a full-stack web application that helps students remember the reasoning behind coding problems they have already solved. An accepted submission records a result, but it does not show whether its algorithm can be reconstructed several days later. The application connects a personal problem library to a daily revision queue, an explainable scheduler, and a history of recall attempts. Its aim is to make a small amount of regular review easier to sustain.',
'The application serves students preparing for software engineering interviews. Students save a problem title, platform link, difficulty, topic, approach, and optional mistake note. They revisit due problems in a focused workspace where their explanation is initially hidden, then grade their recall as Again, Hard, Good, or Easy. Each grade produces a new review interval and a visible confirmation. Analytics summarize stored activity and topic confidence. Technically, InterviewRecall combines a React and Vite frontend with a Java 17 Spring Boot backend and JPA/MySQL configuration. A separately labeled browser-local demo lets a reviewer explore the interface without running the account service.',
'Students commonly practise on several coding platforms and keep links or explanations in separate places. A long list of solved problems can encourage new submissions while leaving earlier patterns unpractised. A structured recall workflow asks a more useful question: can the student still explain the approach without immediately reading the answer? The scheduler makes that question part of a repeatable daily routine.',
'In a typical preparation workflow, the student must decide what to review, find the original notes, and maintain a separate reminder. Problems that feel difficult may be postponed, while familiar ones are repeatedly chosen. InterviewRecall brings the saved approach, the lesson, and the next review date into the same record. Earlier due dates receive attention first, and the next interval is shown beside each recall grade. This reduces manual organization without claiming to know whether a solution is correct. The student remains responsible for honest self-assessment and for checking the algorithm, complexity, and edge cases.'
],
10:[
'Coding interview preparation needs a reliable connection between solving a problem once and remembering its approach later. Scattered bookmarks and notes do not show which explanations are becoming difficult to retrieve, which topics need attention, or what should be revised today. A solved count measures activity rather than recall. InterviewRecall addresses this with four connected capabilities that remain practical for an undergraduate full-stack project:',
'• <b>Structured learning records.</b> A problem stores its URL, topic, difficulty, approach, and optional mistake note, making the reasoning easier to retrieve.<br/>• <b>Adaptive review dates.</b> Again, Hard, Good, and Easy change a bounded interval using clear rules rather than an opaque prediction model.<br/>• <b>Recall before reveal.</b> The focus session asks the student to reconstruct the solution before reading the saved explanation.<br/>• <b>Progress and reflection.</b> The queue, activity grid, confidence summaries, and mistake notebook describe the stored preparation history.<br/>The objectives derived from this workflow are listed in table 1.1.',
'InterviewRecall has a conceptual relationship to Sustainable Development Goal 4, Quality Education, through support for regular practice and access to structured learning tools [1]. Its features encourage students to organize explanations and reflect on mistakes. This educational relationship is a design motivation rather than evidence of a measured SDG outcome.'
],
11:[
'The application supports a student’s existing preparation routine by making earlier work easier to revisit. It does not provide a formal course, assess examination performance, or replace instruction. The delivered metrics describe the records in the workspace; they are not proof of improved learning or access.',
'The project can also be discussed in the context of practical software education. Its implementation connects interface design, authentication, Java services, relational modeling, and testable business rules. No reduction in resource use or quantified educational improvement has been measured, and such claims are kept outside the report.',
'For students who solve coding problems but struggle to remember the approach later, InterviewRecall is a personal revision application that organizes explanations and schedules focused recall. Unlike an ordinary bookmark collection, it combines due dates, a four-grade self-assessment, mistake notes, and preparation history. Its design favors clear daily actions and explainable behavior over complex integrations.',
'The goal of InterviewRecall is to make a sustainable review loop available to a student: capture what was learned, revisit it without immediately reading the answer, assess recall honestly, and understand the next review date. The first version emphasizes the complete problem-to-revision workflow, a small account-scoped data model, and useful feedback from stored activity. Future work can connect related patterns or plan a bounded workload before an interview, after the existing account and database deployment has been evaluated more broadly.',
'The backlog below organizes the current implementation into twenty-one reviewable stories. It is a report-level scope model derived from the product brief and source, rather than a recovered historical Agile board.'
],
12:[
'The stories are grouped into three work packages: revision scheduling, frontend design, and backend integration. Each group contains seven delivered capabilities. The sample’s story-point column is retained for formatting, but a dash is used because no recorded estimates or sprint-velocity data are available. Table 1.3 presents the resulting scope without inventing planning history.'
],
13:[
'The release organization follows three implementation work packages, each producing a reviewable part of the application (figure 1.1). The first establishes deterministic scheduling, the second provides the student interface, and the third connects accounts, persistence, tests, and publication. The responsibility table is a suggested review allocation for the three team members; it does not claim undocumented authorship or dated sprint meetings.'
],
14:[
'The first work package establishes the revision engine: define the state and grades, calculate future calendar dates, handle forgotten and overdue problems, and make the rules independently testable. The engine remains a small Java function used by the account service. Its browser mirror supports demo mode and interval previews. Seven stories describe the delivered behavior; historical duration and point estimates are not asserted.'
],
15:[
'InterviewRecall is a coding revision companion. Its scheduler is the component that translates a recall grade and existing learning state into the next useful review date. It receives an interval, repetition count, ease factor, grade, and current calendar date. It returns a bounded interval and updated state without reading a database or depending on an external prediction service.',
'• Keep the schedule understandable to a student.<br/>• Bring forgotten approaches back promptly.<br/>• Extend intervals after successful recall while preserving clear bounds.<br/>• Make date and grade edge cases straightforward to test.',
'The direct consumer is the Java ProblemService, which owns the account transaction. The end user is a student preparing for coding interviews through repeated problem practice. The interface can also be explored as a browser-local demonstration. It does not assume that all students follow the same platform, timetable, or daily problem count, and the daily goal can be personalized.',
'• <b>Capture.</b> A newly saved problem receives its first revision date for tomorrow.<br/>• <b>Recall.</b> The student attempts the algorithm before revealing saved notes.<br/>• <b>Grade.</b> The service applies one of four deterministic scheduling branches.<br/>• <b>Persist.</b> A review record and the new problem state are saved together.<br/>• <b>Return.</b> The interface shows the next interval and updates its queue and history.',
'• Feature 1: Again resets the successful sequence and returns in one day.<br/>• Feature 2: Good uses one-day, six-day, and multiplied learning steps.<br/>• Feature 3: Hard and Easy adapt the interval and ease factor.<br/>• Feature 4: Intervals remain between one and 365 days, using account-local dates.'
],
16:[
'• Recall grades are self-assessments, not automatic solution judgments.<br/>• The account timezone determines the current calendar day.<br/>• The Java service is authoritative for account data; the browser algorithm is used for demo mode and previews.',
'The scheduler is part of the Spring Boot monolith, rather than a separate AI service. A pure Java function was chosen because the rules are small, explainable, and practical to test. ProblemService retrieves the owned problem, locks it for a review update, calls Scheduler.next, saves history, and changes the current schedule within a transaction. The function itself has no dependency on HTTP, JPA, or a system clock supplied implicitly, so tests can provide a fixed date and exact input values.',
'The scheduling state contains intervalDays, repetitions, and ease. A new item starts with a one-day interval, zero successful repetitions, and ease 2.50. The request supplies a grade from zero to three. The current date comes from the account’s IANA timezone, while the completed review receives a UTC timestamp for its historical record.'
],
17:[
'Again returns the item tomorrow and resets its successful repetitions. Hard keeps the sequence but lowers ease; Good and Easy advance it. Difficulty is stored as context and is not an additional scheduling multiplier in this version. The algorithm is inspired by SM-2, with its own four-grade adjustments [2].',
'The browser and backend exchange JSON through the review endpoint. The path identifies the problem, and the request body contains only its recall grade. The session supplies identity, and the CSRF header protects the mutation. The service does not accept a client-supplied owner or authoritative next due date. Table 2.4 summarizes the contract.',
'For a six-day interval, two successful repetitions, and ease 2.50, Good returns fifteen days, Hard returns seven days, Again returns one day, and Easy returns seventeen days. The maximum interval is 365 days. These examples describe deterministic arithmetic, not a prediction of how long a particular student will remember the algorithm.',
'The revision engine has no independent screen. Its visible interface is the focused recall dialog, where grade buttons display the interval that each branch would produce. Figure 2.2 records an illustrative request and response contract for review; it is not a claim that a Swagger documentation service is implemented.'
],
18:[
'The scheduler is covered by seven recorded Java tests. The cases below map the implemented checks to the story scope; multiple assertions may belong to the same test method. The recorded results are shown in figure 2.3.'
],
19:[
'No dated stand-up log is available. The table is a progress review checklist for Bhanu, Poorna, and Pranav, not a record of invented meetings or completed personal activities.',
'The first work package contains seven implemented scheduling capabilities in the report’s scope model. No recorded historical story-point commitment or measured velocity is available, so those quantities are not inferred. Section 3.2 compares the same review scope across all three work packages.',
'The second work package builds the student interface: a coherent design system, account dialogs, a daily overview, library management, focused recall, analytics, a mistake notebook, and settings. It prioritizes a complete problem-to-review journey and explicit demo labeling rather than a large collection of disconnected screens.'
],
20:[
'The frontend scope is presented as seven delivered stories in table 2.8. Review ownership is suggested for the submitting team; the point and duration columns remain unestimated because no historical planning record is supplied.',
'The interface turns the revision concept into a small number of actions a student can use daily. It highlights what is due, keeps the approach hidden during recall, and confirms the next interval after grading. Search, filters, notes, and export support the surrounding library workflow. Sample demo data remains clearly distinct from a signed-in account collection.',
'• <b>Registration and login.</b> The student provides account details, receives validation feedback, and connects to the Java session service. A real account starts with an empty problem library.'
],
21:[
'• <b>Problem capture.</b> Save a title, platform URL, difficulty, topic, approach, and optional lesson.<br/>• <b>Daily queue.</b> Inspect due and overdue problems and enter a focused session directly.<br/>• <b>Recall grading.</b> Reconstruct the algorithm, reveal notes when needed, and choose a grade with its interval preview.<br/>• <b>Reflection.</b> Inspect topic confidence, recent attempts, and reusable mistake notes.<br/>• <b>Preferences.</b> Set a daily goal and timezone, and export preparation records as JSON.',
'• Feature 5: Account dialogs with visible labels and actionable errors.<br/>• Feature 6: Overview with daily goal, due preview, streak, and focus card.<br/>• Feature 7: Searchable problem library with preserved schedules during editing.<br/>• Feature 8: Hidden-note recall session and interval previews.<br/>• Feature 9: Analytics and mistake notebook.<br/>• Feature 10: Settings, export, and responsive navigation.',
'• The account backend owns schedules and personal record access.<br/>• The browser-local demo is a separate persistence mode.<br/>• The interface does not execute code or determine solution correctness.<br/>• Layout checks cover representative desktop, tablet, and phone widths.',
'The frontend is a React single page application built with Vite and TypeScript. React state coordinates the screens and dialogs; hash navigation preserves the selected main page. A small API adapter handles JSON, session requests, CSRF, and errors. Reusable Metric, Activity, and ProblemTable components share the same design language, while model.ts contains types, date helpers, and demo behavior.'
],
22:[
'The interface provides explicit empty states and action errors. Account forms show request progress, while the independent demo stays usable when the Java backend is unavailable.',
'Figure 2.4 follows the student from a saved problem through recall and grading to a new review date. The mistake note and analytics feed back into the next preparation decision.',
'All screens use the supplied forest, lime, and mint visual direction, Archivo type, and restrained glass surfaces. The account dialogs distinguish a real backend connection from the hosted local demo. The report itself retains the sample’s Times New Roman typography.'
],
23:[
'The overview (figure 2.6) greets the student and combines today’s revision entry point with a daily goal, due count, recall summary, and library preview. A low-confidence focus card suggests a problem to revisit. Selecting a revision opens the focus dialog (figure 2.7), where the saved approach remains hidden until the student deliberately reveals it. No code is executed or automatically graded in this step.'
],
24:[
'The library lists the saved problems with their difficulty, topic, confidence, and next review status (figure 2.8). Search and topic filters narrow the collection. The reminder panel (figure 2.9) links back to due work; it is an in-app queue summary, not an external push notification service.',
'The revision queue (figure 2.10) brings together due and overdue items. Analytics (figure 2.11) summarizes recorded grades and topics over a selected period, while preferences and export are available in Settings (figure 2.12).'
],
25:[
'The mistake notebook (figure 2.13) gathers the optional lessons saved with problems, such as an edge case or pointer update that previously caused an error. Each card opens the associated problem so that reflection remains connected to the explanation. The problem form (figure 2.14) captures the original URL, topic, difficulty, approach, and lesson. Editing a record preserves its existing schedule instead of silently treating it as a new learning item.'
],
26:[
'The frontend has four recorded scheduler tests and representative Chrome workflow checks. The table lists browser scenarios verified during implementation; figure 2.15 shows the scheduler test output. These are not a claim of complete cross-browser coverage.'
],
27:[
'The frontend work package contains seven delivered stories in the review scope. Historical story-point estimates were not recorded. The implementation and its representative checks are summarized again in section 3.2.'
],
28:[
'The third work package connects the Java account service to the interface and makes the complete prototype reviewable. It covers the data model, secure session workflow, owner-scoped CRUD and history, validated errors, transactional review updates, browser transport, documented startup, and private static publication. The scope is separated from a future public full-stack rollout.'
],
29:[
'The backend completes the personal study loop. A signed-in student owns a collection of problems, reviews an item, and receives an updated due date and history record. The browser displays those returned values rather than supplying an authoritative schedule. Demo mode follows the same visible journey locally and is labeled separately.',
'• <b>Identity.</b> Registration stores a BCrypt password hash; login creates a server-side session.<br/>• <b>Ownership.</b> Private reads and mutations resolve the session account and scope repository queries to its identifier.<br/>• <b>Validation.</b> DTO constraints bound text, URLs, difficulty, grades, and goals; API errors use clear JSON messages.<br/>• <b>Review persistence.</b> A write lock serializes review updates to an owned problem, and a transaction saves history and schedule together.<br/>• <b>Preferences.</b> The account stores its name, daily goal, and IANA timezone.<br/>• <b>Deletion.</b> Removing a problem also removes its review rows through the service.<br/>• <b>Browser transport.</b> Same-origin requests use the session cookie and CSRF header rather than a token in localStorage.',
'• The Java service and MySQL are required for real account persistence.<br/>• The private static preview runs only the browser-local demo.<br/>• Automated persistence checks use H2 in MySQL compatibility mode.<br/>• Production deployment needs HTTPS, migrations, and durable sessions.'
],
30:[
'The backend is a Spring Boot monolith with a small number of clear boundaries. Controllers receive validated DTOs, ProblemService owns business transactions, repositories select persistent records, and Scheduler contains the pure interval rules. SecurityConfig handles account authentication, session context, CSRF, and private route protection. Java 17 and Spring Boot 3.4.5 are declared in the project. The frontend reaches /api through the Vite development proxy, keeping account requests on the same browser origin.',
'The configured MySQL database has three application entities: accounts in users, saved learning items in problems, and attempts in revisions. Account ownership links the records; compound indexes support due-date and history access.',
'', '', '', '', '',
'The model uses associations rather than introducing an artificial student/admin inheritance hierarchy. DTO records keep password hashes and the persistence graph out of responses. JPA schema update is configured for local development, not as a substitute for production migrations. Figure 2.17 presents the entity relationships, and figure 2.18 shows the corresponding mapping source rather than an unverified live database screenshot.'
],
31:[
'• Browser and backend exchange JSON through the /api proxy. Mutations include a CSRF header and use the HttpOnly session cookie.<br/>• The service retrieves problems and history under the authenticated account identifier; the client cannot choose another owner.<br/>• Review dates use the account-local calendar day, while the history timestamp is a UTC instant.<br/>• The backend returns the new state, and the browser updates its owned collection after success.'
],
32:[
'The browser’s four labels map to the numeric grades and state transitions in table 2.18. Figure 2.19 shows the service path from a valid review request to stored history and an updated problem.',
'The published preview is an owner-private static site. It serves the compiled React frontend and keeps demo records in browser storage. Real account mode runs locally with the Spring Boot service and a configured MySQL database. The README describes that setup and the Vite proxy. A future full-stack deployment should place the frontend and API behind one HTTPS reverse proxy, use secure cookies and durable sessions, and validate the actual MySQL service. The present report does not claim that Java is hosted by the static site.'
],
33:[
'The overview (figure 2.21) combines due work, daily progress, and a low-confidence focus suggestion. The analytics page (figure 2.22) summarizes recent recall, topic confidence, and activity from stored records. In demo mode these values include seeded sample history and are labeled accordingly. They are not proof that any team member completed those sessions or achieved a particular learning outcome. Good and Easy count as successful recall in the displayed rate.'
],
34:[
'The recorded backend suite contains ten passing tests: seven scheduler tests and three integration tests using Spring MockMvc and H2. The integration methods contain several assertions, so the functional scenarios below are not ten additional independent test methods. Figure 2.23 shows the stored test-result summaries.'
],
35:[
'The third work package contains seven delivered capabilities in the report’s review scope. The table and chart in section 3.2 use that scope; unrecorded historical estimates and velocity figures are not invented.'
],
36:[
'Table 3.1 relates the seven project objectives to the inspected implementation and recorded evidence. The result is a working academic prototype with a complete study loop, rather than a claim that all production and educational evaluation work has been completed.',
'The revision engine is evaluated through deterministic input/output cases and boundary tests, not through trained forecasting models. Table 3.2 uses fixed example states to make the rule behavior easy to check. The Good learning steps are one day and six days before multiplication by ease. Again resets successful repetitions, Hard grows slowly, and Easy advances the interval more strongly. The global day and ease bounds prevent runaway values. These checks establish arithmetic behavior rather than long-term retention accuracy.'
],
37:[
'Calendar checks include a year boundary and a case where the account-local date differs from UTC. Together with grade validation, the examples show the scheduler’s intended behavior without reporting unrelated prediction metrics.',
'<b>Important limitation.</b> These results are deterministic software checks. Confidence is mapped from self-reported recall, and no longitudinal study has established memory improvement or interview readiness. A live MySQL database has also not been exercised in the recorded environment; integration tests use H2 compatibility mode.',
'The static demo is privately published at interview-recall-studio.cloudlessboat4.chatgpt.site. It demonstrates the interface and local persistence. The Java account service and MySQL are started separately through the README instructions. Source files, verification summaries, test commands, and database settings are included for review. No public performance benchmark or full-stack cloud operation is claimed.'
],
38:[
'Figure 3.1 and table 3.4 summarize implemented story coverage by work package. Each contains seven review stories mapped to the delivered code. The points columns remain unestimated; this scope comparison is not a historical burn-down chart or a measured sprint velocity.',
'• <b>Self-assessed recall.</b> Grades and confidence are useful prompts but are not calibrated predictions of interview performance.<br/>• <b>Database evaluation.</b> Recorded integration uses H2 compatibility mode; actual MySQL, migrations, and recovery need validation.<br/>• <b>Deployment boundary.</b> The published static demo does not host the Java account service.<br/>• <b>Account lifecycle.</b> Email verification, recovery, rate limits, and durable sessions remain future work.<br/>• <b>Broader evaluation.</b> More browsers, assistive technologies, realistic workloads, and longitudinal learning observations are needed.'
],
39:[
'InterviewRecall demonstrates how a small full-stack application can connect solved coding problems with future recall practice. The student saves an approach and a mistake note, revisits the item without immediately reading the answer, grades recall, and receives a new review date. A daily queue and focused workspace make that loop practical, while analytics and the notebook support reflection. The interface follows the supplied forest, lime, and mint direction with restrained glass surfaces, and the account service remains primarily Java-based.',
'The architecture keeps the revision rules independent and testable while making the backend authoritative for account schedules. Session security, owner-scoped queries, DTO boundaries, and transactional review history establish a useful prototype foundation. Recorded checks include fourteen passing scheduler and integration tests, a production build, and representative browser workflows. The private static demo makes the interface reviewable without misrepresenting its browser storage as a hosted MySQL account service. The next work should strengthen deployment and evaluation before adding complexity.',
'• <b>Validate deployment.</b> Exercise a real MySQL service, add migrations and backups, and evaluate restart behavior.<br/>• <b>Strengthen accounts.</b> Add recovery, verification, rate limits, HTTPS-only cookies, and durable sessions.<br/>• <b>Connect patterns.</b> Link related problems through explicit techniques and lessons.<br/>• <b>Plan bounded workloads.</b> Support an interview countdown without overwhelming overdue queues.<br/>• <b>Evaluate recall.</b> Collect consented observations and compare outcomes over time.<br/>• <b>Broaden quality checks.</b> Review accessibility, devices, browsers, concurrency, and realistic performance.'
]
}
ABSTRACT='InterviewRecall is a full-stack web application that helps students retain the approaches behind coding problems they have solved. Platform histories and scattered notes record activity but do not identify what should be revised today or whether an explanation can still be recalled. Students save problem links, difficulty, topics, approaches, and mistake notes, then revisit due items in a focused workspace. The explanation remains hidden until it is deliberately revealed, after which the student grades recall as Again, Hard, Good, or Easy. A deterministic Java scheduler uses the grade and previous state to calculate the next interval. The account service stores the revision history and updated problem schedule in one transaction. The system combines a React single page application built with Vite and TypeScript, a Spring Boot backend, Spring Security, Spring Data JPA, and MySQL configuration. Session authentication, BCrypt password hashing, CSRF protection, and owner-scoped queries protect personal records. Calendar dates use the account timezone, while review history stores UTC timestamps. The interface follows the supplied forest, lime, and mint palette with restrained glassmorphism and provides an overview, library, revision queue, analytics, mistake notebook, and settings. Recorded verification includes seven backend scheduler tests, three integration tests, four frontend scheduler tests, a production build, and Chrome workflow checks at four widths. Integration persistence was tested with H2 in MySQL compatibility mode; live MySQL and production hardening remain future work. The private static preview is an explicitly labeled browser-local demo. The project supports structured practice and reflection without claiming experimentally measured learning gains.'
REFS=[
'[1] United Nations, “Goal 4: Quality Education,” Department of Economic and Social Affairs. [Online]. Available: https://sdgs.un.org/goals/goal4',
'[2] P. A. Wozniak, “SuperMemo 2: Application of a computer to improve the SuperMemo method,” 1990. [Online]. Available: https://super-memory.com/english/ol/sm2.htm',
'[3] Spring, “Spring Boot Reference Documentation.” [Online]. Available: https://docs.spring.io/spring-boot/index.html',
'[4] Spring Data, “JPA Transactionality.” [Online]. Available: https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html',
'[5] Spring Security, “Cross Site Request Forgery.” [Online]. Available: https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html',
'[6] React, “Quick Start.” [Online]. Available: https://react.dev/learn',
'[7] Vite, “Getting Started.” [Online]. Available: https://vite.dev/guide/',
'[8] Microsoft, “TypeScript Documentation.” [Online]. Available: https://www.typescriptlang.org/docs/',
'[9] Oracle, “MySQL Reference Manual.” [Online]. Available: https://dev.mysql.com/doc/',
'[10] Tailwind Labs, “Tailwind CSS Documentation.” [Online]. Available: https://tailwindcss.com/docs',
'[11] NextLevelBuilder, “UI UX Pro Max.” [Online]. Available: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill',
'[12] Microsoft, “Playwright Documentation.” [Online]. Available: https://playwright.dev/docs/intro',
'[13] Node.js, “Test runner.” [Online]. Available: https://nodejs.org/api/test.html',
'[14] JUnit Team, “JUnit User Guide.” [Online]. Available: https://junit.org/junit5/docs/current/user-guide/',
'[15] InterviewRecall, local source code, README.md, PRODUCT.md, VERIFICATION.md, test summaries, and browser verification artifacts, November 2026.',
'[16] Supplied original PrePlate report, sample_report.pdf. Used for report organization, institutional details, formatting, and layout. Project-specific evidence was not reused.',
'[17] InterviewRecall development disclosure. AI assistance supported implementation and document preparation; the submitting team is responsible for review and verification. Supplied UI assets and external design guidance are acknowledged.',
'[18] InterviewRecall private static demonstration. [Online]. Available: https://interview-recall-studio.cloudlessboat4.chatgpt.site',
'[19] Software versions and test totals in this report follow inspected local configuration and recorded project evidence. Documentation links are references, not claims that the latest software versions were used.'
]
CODE={
42:[(197.57,8.3,'''// Review DTO: the path supplies the problem ID.
record Grade(@Min(0) @Max(3) int grade) {}
// Problem input is validated separately.
record ProblemInput(
    @NotBlank @Size(max=180) String title,
    @NotBlank @Size(max=2048) String url,
    @NotBlank String platform,
    @NotNull String difficulty,
    @NotBlank String topic,
    @NotBlank @Size(max=10000) String approach) {}'''),(318.1,8.3,'''// Due items are derived from the loaded owned library.
const date = today(user.zoneId);
const due = problems
  .filter(problem => problem.nextReviewOn <= date)
  .sort((a, b) =>
    a.nextReviewOn.localeCompare(b.nextReviewOn)
      || a.confidence - b.confidence);
// A new problem receives a first review tomorrow.
const nextReviewOn = plusDays(date, 1);
// The full component also renders goals and activity.'''),(501.5,8.3,'''// Account mode uses the returned Java schedule.
const updated = await api<Problem>(
  `/problems/${selected.id}/reviews`,
  "POST", { grade }
);
setProblems(items => items.map(problem =>
  problem.id === updated.id ? updated : problem
));
setReviews(await api<Review[]>("/revisions"));
// Demo mode uses the browser scheduler separately.'''),(681.0,8.3,'''interface ProblemRepository
    extends JpaRepository<Problem, Long> {
  List<Problem> findAllByOwnerIdOrderByNextReviewOnAsc(Long id);
  Optional<Problem> findByIdAndOwnerId(Long id, Long ownerId);
  // Owned write lock and other setup omitted.
}''')],
43:[(78.5,8.3,'''// Repository excerpts: all private selections include account scope.
interface AccountRepository extends JpaRepository<Account, Long> {
  Optional<Account> findByEmail(String email);
}
interface RevisionRepository extends JpaRepository<Revision, Long> {
  List<Revision> findAllByOwnerIdOrderByReviewedAtDesc(Long id);
  void deleteAllByProblemId(Long id);
}

@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select p from Problem p where p.id=:id "
     + "and p.owner.id=:ownerId")
Optional<Problem> lockOwned(Long id, Long ownerId);

// Account identity is resolved from the authenticated principal.
Account account(String email) {
  return accounts.findByEmail(email)
    .orElseThrow(() -> new ResponseStatusException(
      UNAUTHORIZED, "Please sign in"));
}
// Complete imports, constructors, and mapping are in the source.'''),(311.6,8.3,'''public static Result next(int previous, int repetitions,
    double ease, int grade, LocalDate today) {
  if (grade < 0 || grade > 3)
    throw new IllegalArgumentException("Invalid recall grade");
  int days;
  if (grade == 0) {
    days = 1; repetitions = 0;
    ease = Math.max(1.3, ease - .2);
  } else if (grade == 1) {
    days = Math.max(1, (int)Math.round(previous * 1.2));
    ease = Math.max(1.3, ease - .15);
  } else if (grade == 2) {
    days = repetitions == 0 ? 1 : repetitions == 1 ? 6
        : (int)Math.round(previous * ease);
    repetitions++;
  } else {
    days = repetitions == 0 ? 4 : Math.max(previous + 1,
        (int)Math.round(previous * (ease + .3)));
    ease = Math.min(3, ease + .15); repetitions++;
  }
  days = Math.min(365, Math.max(1, days));
  return new Result(days, repetitions, ease, today.plusDays(days));
}'''),(561.8,8.3,'''// Excerpt from ProblemService.review, inside its transaction.
Account a = account(email);
Problem p = problems.lockOwned(id, a.id)
    .orElseThrow(() -> new ResponseStatusException(
        NOT_FOUND, "Problem not found"));
LocalDate today = LocalDate.now(ZoneId.of(a.zoneId));
var result = Scheduler.next(p.intervalDays,
    p.repetitions, p.ease, grade, today);
Revision r = new Revision();
r.owner = a; r.problem = p; r.grade = grade;
r.reviewedAt = Instant.now();
r.scheduledOn = p.nextReviewOn;
r.intervalDays = result.intervalDays();
revisions.save(r);
p.intervalDays = result.intervalDays();
p.repetitions = result.repetitions();
p.ease = result.ease();
p.nextReviewOn = result.nextReviewOn();
p.confidence = new int[] {20, 45, 75, 95}[grade];''')],
44:[(99.62,8.3,'''// Authentication and ownership excerpts; configuration omitted.
var auth = manager.authenticate(
    UsernamePasswordAuthenticationToken.unauthenticated(
        d.email().trim().toLowerCase(Locale.ROOT),
        d.password()));
sessions.onAuthentication(auth, request, response);
var context = SecurityContextHolder.createEmptyContext();
context.setAuthentication(auth);
SecurityContextHolder.setContext(context);
contexts.saveContext(context, request, response);

Problem owned(Long id, Account a) {
  return problems.findByIdAndOwnerId(id, a.id)
      .orElseThrow(() -> new ResponseStatusException(
          NOT_FOUND, "Problem not found"));
}
// Passwords are hashed using BCrypt at account registration.
// Private mutation requests are protected by session CSRF.
// A foreign owner identifier from the client is never trusted.'''),(320.0,8.3,'''spring.application.name=InterviewRecall
spring.datasource.url=${DB_URL:jdbc:mysql://localhost:3306/interviewrecall}
spring.datasource.username=${DB_USER:interviewrecall}
spring.datasource.password=${DB_PASSWORD:local-development-only}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.open-in-view=false
spring.jpa.properties.hibernate.jdbc.time_zone=UTC
server.servlet.session.cookie.http-only=true
server.servlet.session.cookie.same-site=lax
server.servlet.session.cookie.secure=${COOKIE_SECURE:false}
server.servlet.session.timeout=8h''')]
}

def table_spans(page,rect):
 return [s for l in original_text_lines(page) for s in l['spans'] if s['text'].strip() and fitz.Rect(rect).contains(fitz.Rect(s['bbox']))]

def render_table(page,index,values):
 spec=next(v for v in M['tables'] if v['page']==page and v['table']==index)
 raw=spec['rows'];start=2 if page in [37,38] and index==0 else 1
 columns=[v['rect'] for v in raw[start] if v['text'].strip()]
 # Normal rows have one rectangle per semantic column; extra header padding cells are ignored.
 if page==8:columns=[v['rect'] for v in raw[1]]
 if (page,index)==(13,1):
  # Add the third team member within the sample's existing table frame.
  left,split,right=columns[0][0],columns[0][2],columns[-1][2]
  top=min(v['rect'][1] for v in raw[0]);bottom=max(v['rect'][3] for v in raw[-1])
  edges=[left]+[split+(right-split)*i/3 for i in range(4)]
  columns=[[a,top,b,bottom] for a,b in zip(edges,edges[1:])]
  c.saveState();c.setFillColor('white');c.rect(left,H-bottom,right-left,bottom-top,fill=1,stroke=0)
  header_bottom=max(v['rect'][3] for v in raw[0])
  c.setFillColor('#e7e6e6');c.rect(left,H-header_bottom,right-left,header_bottom-top,fill=1,stroke=0)
  c.setStrokeColor('black');c.setLineWidth(.5)
  for x in edges:c.line(x,H-top,x,H-bottom)
  for y in [top]+[max(v['rect'][3] for v in row) for row in raw]:c.line(left,H-y,right,H-y)
  c.restoreState()
 if len(columns)!=len(values[0]):raise ValueError((page,index,len(columns),len(values[0])))
 for ri,row in enumerate(values):
  if page==41:src=raw[ri]
  elif start==2 and ri>0:src=raw[ri+1]
  else:src=raw[ri]
  y0=min(v['rect'][1] for v in src);y1=max(v['rect'][3] for v in src)
  if start==2 and ri==0:y1=max(v['rect'][3] for v in raw[1])
  for ci,value in enumerate(row):
   x0,x1=columns[ci][0],columns[ci][2]
   ss=table_spans(page,[x0,y0,x1,y1]);fs=Counter(round(s['size'],2) for s in ss).most_common(1)[0][0] if ss else 10.08
   fs=fs if fs>=7 else 10.08
   bold=ri==0 and page!=41 or page==41 and ci==0
   align=TA_CENTER if ri==0 or (page not in [11,41] and (x1-x0<105 or str(value) in ['Pass','Done','—'])) else TA_LEFT
   style=ParagraphStyle('cell',fontName='TNRB' if bold else 'TNR',fontSize=fs,leading=12.24,alignment=align,splitLongWords=False)
   par=Paragraph(escape(str(value)).replace('\n','<br/>'),style);_,hh=par.wrap(x1-x0-8.16,2000)
   if hh>y1-y0+1:FAIL.append({'key':f'table {page}.{index} row {ri} col {ci}','height':hh,'allowed':y1-y0,'text':str(value)})
   top=y0+(y1-y0-hh)/2
   par.drawOn(c,x0+4.08,H-top-hh)

# Figure primitives follow the corrected sample's restrained pastel boxes and thin arrows.
def diagram(rect,kind):
 x0,y0,x1,y1=rect;c.saveState();c.translate(x0,H-y1);c.scale((x1-x0)/1000,(y1-y0)/400)
 def box(x,y,w,h,title,lines=(),fill='#FFF3A1'):
  c.setFillColor(fill);c.setStrokeColor('#777777');c.setLineWidth(1);c.rect(x,400-y-h,w,h,stroke=1,fill=1)
  c.setFillColor('black');c.setFont('TNRB',24);c.drawCentredString(x+w/2,400-y-32,title)
  c.setFont('TNR',20)
  for j,line in enumerate(lines):c.drawCentredString(x+w/2,400-y-60-j*25,line)
 def ar(xa,ya,xb,yb,label=''):
  c.setStrokeColor('#777777');c.setLineWidth(1.2);c.line(xa,400-ya,xb,400-yb)
  angle=math.atan2(yb-ya,xb-xa)
  for off in [-.4,.4]:c.line(xb,400-yb,xb-10*math.cos(angle+off),400-(yb-10*math.sin(angle+off)))
  if label:c.setFont('TNR',17);c.setFillColor('black');c.drawCentredString((xa+xb)/2,(800-ya-yb)/2+9,label)
 if kind=='release':
  for x,title,lines,col in [(10,'Sprint 1',['Revision scheduling','Rules, dates, tests'],'#FFBE85'),(350,'Sprint 2',['Frontend workflow','Library, recall, analytics'],'#FFF3A1'),(690,'Sprint 3',['Accounts and integration','Security, persistence, demo'],'#AFC89A')]:box(x,80,300,230,title,lines,col)
  ar(310,195,350,195);ar(650,195,690,195)
 elif kind in ['flow','schedule']:
  labels=[('Save problem',['Approach and lesson']),('Daily queue',['Due and overdue']),('Recall',['Notes initially hidden']),('Grade',['Again / Hard / Good / Easy']),('Next review',['History and new date'])]
  for j,(title,lines) in enumerate(labels):box(5+j*200,145,185,110,title,lines,'#FFF3A1' if j<3 else '#C7DBB2')
  for j in range(4):ar(190+j*200,200,205+j*200,200)
 elif kind=='architecture':
  box(0,130,250,150,'React + Vite',['Personal workspace','TypeScript / Tailwind'],'#FFF3A1');box(375,75,250,250,'Spring Boot',['Session and CSRF','Controllers and DTOs','Services and scheduler','JPA repositories'],'#FFBE85');box(750,130,250,150,'MySQL',['users / problems','revisions'],'#C7DBB2');ar(250,200,375,200,'JSON /api');ar(625,200,750,200,'JDBC')
 elif kind=='er':
  box(350,0,300,115,'users',['id, email, password_hash','name, daily_goal, zone_id'],'#AFC89A');box(0,225,430,160,'problems',['id, owner_id, title, url, topic','approach, notes, confidence','interval_days, next_review_on'],'#FFF3A1');box(570,225,430,160,'revisions',['id, owner_id, problem_id','grade, reviewed_at','scheduled_on, interval_days'],'#FFBE85');ar(400,115,215,225,'1 to many');ar(600,115,785,225,'1 to many');ar(430,310,570,310,'1 to many')
 elif kind=='sequence':
  for x,label in zip([80,350,650,920],['Browser','Controller','Service','Database']):
   box(x-70,0,140,60,label,[]);c.setDash(5,5);c.line(x,330,x,10);c.setDash()
  for xa,xb,y,label in [(80,350,100,'POST grade + CSRF'),(350,650,150,'Validate / delegate'),(650,920,200,'Lock owned problem'),(650,920,250,'Save history + schedule'),(650,350,300,'Updated problem DTO'),(350,80,350,'Next review date')]:ar(xa,y,xb,y,label)
 elif kind=='deployment':
  box(0,20,300,130,'Browser',['Static demo / local account UI'],'#FFBE85');box(650,20,350,130,'Private static host',['Compiled React demo only'],'#FFF3A1');box(0,250,300,130,'Local Spring Boot',['Real account service'],'#FFBE85');box(650,250,350,130,'Local MySQL',['Configured account database'],'#C7DBB2');ar(300,80,650,80,'Static files');ar(150,150,150,250,'/api proxy');ar(300,315,650,315,'JPA / JDBC')
 elif kind=='coverage':
  for y in [80,160,240,320]:c.setStrokeColor('#dddddd');c.line(60,y,990,y)
  for j,label in enumerate(['Scheduler','Frontend','Integration']):
   for off,col in [(-35,'#FFF3A1'),(35,'#AFC89A')]:c.setFillColor(col);c.rect(220+j*300+off,70,55,250,fill=1,stroke=0)
   c.setFillColor('black');c.setFont('TNR',22);c.drawCentredString(250+j*300,32,label);c.drawCentredString(250+j*300,340,'7 / 7 stories')
  c.setFont('TNR',18);c.drawString(70,375,'Review scope');c.drawString(640,375,'Recorded story points: not estimated')
 c.restoreState()

def image_in(rect,path):
 im=ImageReader(str(path));iw,ih=im.getSize();x0,y0,x1,y1=rect;scale=min((x1-x0)/iw,(y1-y0)/ih);ww,hh=iw*scale,ih*scale
 c.drawImage(im,x0+(x1-x0-ww)/2,H-y0-(y1-y0-hh)/2-hh,width=ww,height=hh)

def panel(rect,text,fontsize=8.2):
 x0,y0,x1,y1=rect;c.saveState();c.setFillColor('#f5f5f2');c.rect(x0,H-y1,x1-x0,y1-y0,fill=1,stroke=0);c.setFillColor('black')
 lines=text.splitlines();size=min(fontsize,(y1-y0-10)/max(1,len(lines))/1.22,(x1-x0-14)/max(1,max(len(l) for l in lines))/.6)
 for j,line in enumerate(lines):text_at(line,x0+7,y0+7+size+j*size*1.22,size,'CN')
 c.restoreState()

SOURCES={
'contract':'Illustrative review contract (not live API output)\nPOST /api/problems/{id}/reviews\nContent-Type: application/json\nX-CSRF-TOKEN: <session token>\n{"grade": 2}\n\nResponse: intervalDays, nextReviewOn, repetitions, ease, confidence',
'jpa':'JPA mapping source - configured MySQL schema\n@Entity @Table(name="users")\nclass Account { Long id; String email; String passwordHash; }\n@Entity @Table(name="problems")\nclass Problem { @ManyToOne Account owner; LocalDate nextReviewOn; }\n@Entity @Table(name="revisions")\nclass Revision { @ManyToOne Account owner; @ManyToOne Problem problem; }',
'repository':'Actual repository selection excerpt\n@Lock(LockModeType.PESSIMISTIC_WRITE)\n@Query("select p from Problem p where p.id=:id "\n     + "and p.owner.id=:ownerId")\nOptional<Problem> lockOwned(Long id, Long ownerId);',
'persist':'Actual review transaction excerpt\nRevision r = new Revision();\nr.owner = a; r.problem = p; r.grade = grade;\nr.reviewedAt = Instant.now();\nr.scheduledOn = p.nextReviewOn;\nr.intervalDays = result.intervalDays();\nrevisions.save(r);\np.nextReviewOn = result.nextReviewOn();'}
# Compose the two real account-dialog captures into the original paired figure slot.
ims=[Image.open(A/n).convert('RGB') for n in ['auth-login.png','auth-register.png']]
paired=Image.new('RGB',(1200,560),'white')
for j,im in enumerate(ims):
 im.thumbnail((570,540));paired.paste(im,(j*600+(600-im.width)//2,(560-im.height)//2))
paired.save(A/'authentication-pair.png')
IMAGE_CONTENT={13:[('diagram','release')],16:[('diagram','schedule')],18:[('panel','contract'),('scheduler-test',None)],22:[('diagram','flow')],23:[('image','authentication-pair.png'),('image','overview-wide.png'),('image','recall-hidden.png')],24:[('image','library-wide.png'),('image','notifications-wide.png')],25:[('image','queue-wide.png'),('image','analytics-wide.png'),('image','settings-wide.png')],26:[('image','notebook-wide.png'),('image','add-problem.png')],27:[('frontend-test',None)],30:[('diagram','architecture')],31:[('diagram','er'),('panel','jpa')],32:[('diagram','sequence')],33:[('diagram','deployment'),('image','overview-wide.png'),('image','analytics-wide.png')],34:[('backend-test',None)],38:[('diagram','coverage')],44:[('panel','repository'),('panel','persist')]}

def render_images(page):
 for info,(kind,value) in zip(M['layout'][page-1]['images'],IMAGE_CONTENT.get(page,[])):
  rect=info['bbox']
  if kind=='image':image_in(rect,A/value)
  elif kind=='diagram':diagram(rect,value)
  elif kind=='panel':panel(rect,SOURCES[value])
  elif kind=='scheduler-test':panel(rect,'Recorded SchedulerTest summary\nTests run: 7, Failures: 0, Errors: 0, Skipped: 0\nSource: backend/target/surefire-reports/\n       com.interviewrecall.SchedulerTest.txt')
  elif kind=='backend-test':panel(rect,Path('/private/tmp/interviewrecall-report-backend-tests.log').read_text().replace('-------------------------------------------------------------------------------','------------------------------'))
  elif kind=='frontend-test':
   t=Path('/private/tmp/interviewrecall-report-frontend-tests.log').read_text();t=re.sub(r'\x1b\[[0-9;]*m','',t);t=t.replace('✔','PASS ').replace('ℹ','');panel(rect,t)

# Final copy edits keep the sample's original type sizes and fixed frame heights.
N[11][0]='The application makes earlier work easier to revisit. It does not replace teaching or assess examination performance. Workspace metrics describe preparation records, rather than proving improved learning or access.'
N[11][4]='The twenty-one stories organize the inspected implementation into reviewable scope. They do not reconstruct an unrecorded historical Agile board.'
N[12][0]='The stories form three work packages: scheduling, frontend design, and backend integration, with seven capabilities each. The original point column is retained with dashes because no estimates or velocity records are available. Table 1.3 describes the implementation without inventing planning history.'
N[17][0]='Again returns tomorrow and resets repetitions. Hard lowers ease; Good and Easy advance the sequence. Difficulty is descriptive rather than a multiplier. The rules are inspired by SM-2, with four-grade adjustments [2].'
N[18][0]='Seven recorded Java tests cover the scheduler. The table maps their assertions to the review stories; figure 2.3 shows the stored test summary.'
N[19][1]='Seven scheduling capabilities are implemented in the review scope. Historical story points and measured velocity are not recorded and are not inferred. Section 3.2 compares the same scope across all three work packages.'
N[20][0]='Table 2.8 contains seven delivered frontend stories. Review ownership is suggested; historical points and duration estimates are not recorded.'
N[20][2]='• <b>Registration and login.</b> Account dialogs validate entries and connect to the Java session service. New accounts begin with an empty library.'
N[24][0]='The library shows difficulty, topic, confidence, and review status (figure 2.8). Search and filters narrow the collection. The reminder panel (figure 2.9) links to due work; it is an in-app queue summary rather than external push delivery.'
N[26][0]='Four frontend scheduler tests and representative Chrome checks are recorded. The table lists verified browser scenarios; figure 2.15 shows scheduler output.'
N[27][0]='Seven frontend stories are delivered in the review scope. Historical story points are not recorded. Section 3.2 summarizes the same implementation scope.'
N[30][1]='The configured MySQL model has three entities: accounts in users, learning items in problems, and attempts in revisions. Owner links and compound indexes support personal due-date and history queries. Associations express the domain without an artificial student/admin inheritance hierarchy. DTO records keep password hashes and the persistence graph out of responses. JPA schema update is configured for local development, rather than production migrations. Figure 2.17 shows the relationships, and figure 2.18 presents the mapping source instead of an unverified live database screenshot.'
N[30][7]=''
N[31][0]='• Browser requests use JSON through /api, a CSRF header, and the HttpOnly session cookie.<br/>• The service scopes private records to the account; the client cannot choose another owner.<br/>• Due dates use the account calendar day; history uses UTC instants.<br/>• Successful responses return the new schedule for the browser collection.'
N[32][0]='Table 2.18 maps browser labels to scheduling state. Figure 2.19 follows a review request through saved history and the updated problem.'
N[34][0]='The backend has ten recorded passing tests: seven scheduler and three MockMvc/H2 integration tests. Each integration method contains several assertions, so the scenarios below are not additional test methods. Figure 2.23 shows the stored summaries.'
N[35][0]='Seven integration capabilities are delivered in the review scope. Section 3.2 summarizes them without inventing historical points or velocity.'
N[36][0]='Table 3.1 links seven objectives to the source and recorded checks. The prototype still needs production and educational evaluation.'
N[37][0]='Calendar checks cover year rollover and account dates differing from UTC. The examples describe deterministic software behavior rather than unrelated prediction metrics.'
N[38][0]='Figure 3.1 and table 3.4 show seven implemented review stories per work package. Points remain unestimated; the scope comparison is not a historical burn-down chart or measured sprint velocity.'
N[38][1]='• <b>Recall.</b> Self-assessed grades are not calibrated interview predictions.<br/>• <b>Database.</b> Actual MySQL, migrations, and recovery need validation beyond H2 tests.<br/>• <b>Hosting.</b> The static demo does not host the Java account service.<br/>• <b>Accounts.</b> Verification, recovery, rate limits, and durable sessions remain future work.<br/>• <b>Evaluation.</b> More browsers, assistive technologies, realistic workloads, and learning observations are needed.'
T[(18,0)][4][3]='Count kept; ease >= 1.3.'
T[(22,0)][6][2]='All application text and controls.'
T[(37,1)][4][2]='Main flows; four widths.'
T[(41,0)][7][1]='Academic prototype; private demo and separate local account service.'
T[(41,0)][8][1]='Private demo: interview-recall-studio.cloudlessboat4.chatgpt.site . AI-assisted development and report preparation.'

# Clone the supplied PDF first. Its vector rules, table fills, logo, margins and footer locations survive.
doc=fitz.open(ROOT.parent/'sample_report.pdf')
for pi,page in enumerate(doc):
 for link in page.get_links():page.delete_link(link)
 if pi<3:continue
 page.add_redact_annot(fitz.Rect(0,0,W,785),fill=False)
 page.apply_redactions(images=0,graphics=0)
 for image in list(page.get_images(full=True)):
  try:page.delete_image(image[0])
  except ValueError:pass
# Targeted front-matter edits retain all institutional wording and its original layout.
front_regions={0:[(60,75,535,165),(60,215,535,284)],1:[(70,222,527,300),(77,611,523,655)],2:[(70,240,528,400)]}
for pi,rects in front_regions.items():
 for rect in rects:doc[pi].add_redact_annot(fitz.Rect(rect),fill=False)
 doc[pi].apply_redactions(images=0,graphics=0)

for page in range(1,46):
 if page==1:
  for y,t in [(96.74,'INTERVIEWRECALL: A SMART CODING'),(127.49,'REVISION TRACKER FOR CODING'),(158.21,'INTERVIEW PREPARATION')]:text_at(t,299.1,y,16.08,'TNRB',True)
  text_at('Submitted by',299.1,224.23,13.92,'TNRI',True)
  for y,name in [(244.91,'BHANU PRAKASH KUSHA (RA2311003011898)'),(262.91,'POORNA CHANDRA VARRI (RA2311003011910)'),(280.91,'PRANAV PATHAK (RA2311003011900)')]:text_at(name,299.1,y,13.92,'TNRB',True)
 elif page==2:
  text_at('Students / Reg. No.',72.02,235.67,11.04,'TNRB')
  for y,value in [(235.67,': Bhanu Prakash Kusha (RA2311003011898)'),(253.67,'  Poorna Chandra Varri (RA2311003011910)'),(271.67,'  Pranav Pathak (RA2311003011900)')]:text_at(value,192.1,y,11.04)
  text_at('Title of Work',72.02,291.19,11.04,'TNRB')
  text_at(': InterviewRecall: A Smart Coding Revision Tracker',192.1,291.19,11.04)
  for x,name,reg in [(78.5,'Bhanu Prakash Kusha','RA2311003011898'),(226.5,'Poorna Chandra Varri','RA2311003011910'),(374.5,'Pranav Pathak','RA2311003011900')]:
   text_at('Signature: _____________',x,620.78,10.08)
   text_at(name,x,636.38,10.08)
   text_at(f'{reg}  Date: ____',x,651.98,10.08)
 elif page==3:
  paragraph('Certified that 21CSE354T – Full Stack and Web Development report titled “<b>INTERVIEWRECALL: A SMART CODING REVISION TRACKER</b>” is the bonafide work of “<b>BHANU PRAKASH KUSHA (RA2311003011898)</b>”, “<b>POORNA CHANDRA VARRI (RA2311003011910)</b>” and “<b>PRANAV PATHAK (RA2311003011900)</b>” who carried out the project work under my supervision. Certified further, that to the best of my knowledge the work reported herein does not form any other project report or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.',72.02,254.95,454.3,207,12,23.0,key='certificate')
 else:
  # Keep every heading and caption baseline from the original PDF.
  for head in M['heads'][page-1]:
   t=head['text'];line={'spans':head['spans']}
   if re.match(r'^(Figure|Table)\s+[A-Z0-9]+\.\d+',t):copy_line(line,caption(t),True)
   else:copy_line(line,replace(t),bool(re.match(r'^(CHAPTER|APPENDIX|[A-Z ]{8,}$)',t)))
  if page==4:
   paragraph(ABSTRACT,72.02,111.01,454.3,20*20.67,12,20.67,key='abstract')
  elif page in [5,6,7]:
   for l in original_text_lines(page):
    ss=[s for s in l['spans'] if s['text'].strip()];s=ss[0];t=''.join(v['text'] for v in l['spans']).strip()
    if s['bbox'][1]<95 or s['bbox'][1]>780:continue
    if page in [6,7] and re.match(r'^(Figure|Table)\s+',t):
     kind='Figure' if page==6 else 'Table';m=re.search(r'([A-Z0-9]+\.\d+)',t)
     if m:
      title=f'{kind} {m[1]} '+(FIG if page==6 else TAB).get(m[1],'')
      # Keep the sample's narrow list font and original left baseline.
      text_at(title,s['origin'][0],s['origin'][1],s['size'],fontname(s))
    elif page in [6,7] and not re.match(r'^(\d+|FIGURE|TABLE|PAGE)',t):continue
    else:copy_line(l,replace(t))
  elif page==40:
   y=109.0
   for ref in REFS:
    style=ParagraphStyle('ref',fontName='TNR',fontSize=12,leading=13.2,alignment=TA_JUSTIFY,splitLongWords=False)
    pp=Paragraph(escape(ref),style);_,hh=pp.wrap(454.3,1000);pp.drawOn(c,72.02,H-(y-12)-hh);y+=hh+4
   if y>770:FAIL.append({'key':'references','height':y,'allowed':770})
  elif page==41:
   text_at('Draft prepared from the project, for review with the guide.',72.02,125.09,12,'TNRI')
  elif page in [42,43,44]:
   if page==42:paragraph('Representative excerpts from the application, grouped by layer. Imports and unrelated members are omitted, and long lines are wrapped for print. The complete source and AI-assistance disclosure are included with the project.',72.02,125.09,454.3,48,12,15.84,key='code introduction')
   for baseline,leading,code in CODE[page]:
    for j,line in enumerate(code.splitlines()):text_at(line,78.02,baseline+j*leading,7.92,'CN')
  elif page==45:
   rect=M['layout'][44]['images'][0]['bbox']
   paragraph('The similarity-checker report for InterviewRecall has not been generated or attached. This space is reserved for the institution-approved result for this report. The sample’s unrelated percentage, matched sources, author details, and checker image have not been reused.',rect[0]+12,rect[1]+28,rect[2]-rect[0]-24,100,12,18.6,key='similarity appendix')
  elif page in N:
   slots=M['slots'][page-1]
   if len(N[page])!=len(slots):raise ValueError(('slot count',page,len(N[page]),len(slots)))
   for j,(slot,t) in enumerate(zip(slots,N[page])):
    if not t:continue
    fs=slot['font_size'];lead=slot['leading'] if len(slot['lines'])>1 else 18.6
    x=slot['rect'][0];width=526.32-x
    paragraph(t,x,slot['origin'][1],width,(7*18.6 if page==30 and j==1 else len(slot['lines'])*lead+.6),fs,lead,key=f'page {page} slot {j}')
  for (p,idx),rows in T.items():
   if p==page:render_table(page,idx,rows)
  render_images(page)
 c.showPage()
c.save()
overlay=fitz.open(stream=BUF.getvalue(),filetype='pdf')
for i,p in enumerate(doc):p.show_pdf_page(p.rect,overlay,i)
doc.set_metadata({'title':'InterviewRecall - Smart Coding Revision Tracker Project Report','author':'Bhanu Prakash Kusha; Poorna Chandra Varri; Pranav Pathak','subject':'21CSE354T – Full Stack Web Development','creator':'InterviewRecall report using the corrected original sample'})
doc.set_toc([[1,'Front matter',2],[1,'1 Introduction',9],[1,'2 Sprint Planning and Execution',14],[2,'2.1 Revision Scheduling Service',14],[2,'2.2 Frontend Design and Development',19],[2,'2.3 Backend and System Integration',28],[1,'3 Results and Discussion',36],[1,'4 Conclusion and Future Enhancements',39],[1,'References',40],[1,'Appendices',41]])
output=OUT/'InterviewRecall_Project_Report.pdf'
doc.save(output,garbage=4,deflate=True)
(OUT/'source/layout-checks.json').write_text(json.dumps({'template_pages':45,'paragraphs':CHECK,'fit_issues':FAIL},indent=2))
print('Created',output,'with',len(doc),'pages')
print(json.dumps(FAIL,indent=2))
