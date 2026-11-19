# InterviewRecall — Project Explanation and Presentation Guide

## What the project does

InterviewRecall is a personal coding interview revision tracker. It helps students remember **how to solve problems**, rather than only counting accepted submissions.

A student saves a solved problem and its approach, receives a revision date, attempts to recall the approach before revealing notes, and grades the attempt. The next revision date adapts to that grade. A dashboard, analytics screen, and mistake notebook help the student decide what to practise next.

**One-line introduction:**

> InterviewRecall helps students turn solved coding problems into approaches they can remember, using active recall and explainable spaced repetition.

## Team

| Member | Registration number |
| --- | --- |
| Bhanu Prakash Kusha | RA2311003011898 |
| Poorna Chandra Varri | RA2311003011910 |
| Pranav Pathak | RA2311003011900 |

## Presentation account

| Field | Value |
| --- | --- |
| Website on this Mac | http://127.0.0.1:5173 |
| Email | `demo@interviewrecall.test` |
| Password | `Recall@123456` |
| Display name | Bhanu Prakash Kusha |
| Timezone | Asia/Kolkata |
| Daily goal | 5 revisions |

This is an intentionally shared **local presentation account**, with an ordinary BCrypt password and normal authenticated API access. It is not an authentication bypass.

It initially contains **12 coding problems**, approaches, mistake notes, **41 illustrative historical revisions**, and a mixture of due, overdue, and future review dates. The history is sample data for demonstrating the screens, not a claim about any student's real study activity.

The account is created only when the backend starts with the `presentation` profile and the demo email does not already exist. Restarting does not replace its password, notes, problems, preferences, or revision history. A clean service restart was verified with the same account, 12 problems, and 41 revisions. Other accounts are unaffected.

The hosted private URL from the earlier build is a separate browser-local demo. These account credentials work with the **local Java backend**, not with that static hosted preview.

## Start the presentation

Open a terminal in the project directory:

```sh
cd /Users/bhanuprakashkusha/fsd_project/interviewrecall
npm run present
```

Wait for **“InterviewRecall presentation is ready”**, then open http://127.0.0.1:5173. Click **Connect your account**, enter the credentials above, and sign in.

The startup command:

1. Uses the installed MySQL server binaries to start a separate project database on **127.0.0.1:3307**.
2. Stores its database files under `.local/mysql`, which is excluded from Git.
3. Starts Spring Boot on **127.0.0.1:8080** with the `presentation` profile.
4. Creates the demo account and fixtures once.
5. Starts Vite on **127.0.0.1:5173**, or reuses an already running frontend.

The MySQL service on port 3306, if present, is left alone. If native MySQL binaries are unavailable, the command falls back to the existing Docker Compose setup on port 3306; Docker must be running. `MYSQL_BIN` can point to another directory containing `mysql` and `mysqld`. `PRESENTATION_DB_PORT` changes the project-local native port. An explicit `DB_URL`, `DB_USER`, and `DB_PASSWORD` selects a database you have configured yourself.

Keep the terminal running during the presentation. **Ctrl+C** stops the native database, backend, and frontend processes started by this command; existing services are not stopped. Database files remain for the next presentation. The Docker fallback runs detached and can be stopped separately with `docker compose down`.

On a fresh checkout, install dependencies with `npm ci` first. Node 22.12+, Java 17+, Maven, and either native MySQL or Docker Compose are required.

## Five-minute demonstration

### 1. Explain the problem — 30 seconds

“Students solve problems across coding platforms, but a solved count does not tell them whether they still remember the approach. Bookmarks and notes also do not tell them what to revise today. InterviewRecall connects the problem, the explanation, the mistake, and the next review date.”

### 2. Show the overview — 45 seconds

After signing in, explain:

- The daily revision action opens the next due problem.
- The goal ring shows today's completed revisions against the chosen daily goal.
- The queue includes due and overdue problems.
- Recall rate counts Good and Easy grades as successful recall.
- The focus card points to a low-confidence problem's topic.
- The activity grid and streak summarize stored revision activity.

State that the preloaded history is illustrative presentation data.

### 3. Demonstrate the central revision workflow — 90 seconds

1. Open **Revision queue** or **Start today's revision**.
2. Explain the problem's approach out loud before revealing notes.
3. Select **Reveal my approach** and compare it with the saved explanation and lesson.
4. Point out the interval shown under each recall grade.
5. Select **Good** or **Easy**.
6. Show the confirmation, changed due date, queue, and history.

“The Java service calculates the new date. It saves the attempt and the updated problem schedule in the same database transaction.”

Counts and intervals will change as you demonstrate the account; this is expected.

### 4. Add and edit a problem — 60 seconds

Use these example values:

| Field | Example |
| --- | --- |
| Title | Maximum Subarray |
| URL | https://leetcode.com/problems/maximum-subarray/ |
| Platform | LeetCode |
| Difficulty | Medium |
| Topic | Dynamic Programming |
| Approach | Kadane's algorithm: at each index, choose between starting a new subarray and extending the previous one. Track the largest sum. Time O(n), space O(1). |
| Lesson | Initialize from the first element so an all-negative array is handled correctly. |

Show that a new problem is due tomorrow. Search for it in **My problems**, open its details, and demonstrate **Edit**. Editing the explanation preserves the existing schedule.

### 5. Show supporting features — 45 seconds

- **Mistake notebook:** brings saved traps and lessons together.
- **Analytics:** shows recall grades, topic confidence, recent history, and 7/30-day views.
- **Settings:** changes daily goal and timezone and exports records as JSON.

### 6. Finish with architecture — 30 seconds

“The frontend is React with TypeScript and Vite. Spring Boot provides a REST API and session security. JPA maps three entities to MySQL. The scheduler is a small deterministic Java function, so its behavior is explainable and testable.”

## Technology stack

| Layer | Technologies | Responsibility |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite | Screens, state, forms, navigation |
| Styling | Tailwind CSS, shared CSS, Lucide icons | Responsive glass UI, palette, controls |
| Backend | Java 17, Spring Boot, Spring Web | REST endpoints and application workflow |
| Security | Spring Security, BCrypt, sessions, CSRF | Login, private records, protected mutations |
| Persistence | Spring Data JPA, Hibernate, MySQL | Problems, accounts, revision history |
| Testing | JUnit, Spring MockMvc, H2, Node tests, Playwright | Scheduler, accounts, persistence, browser workflows |

The installed native MySQL version on this Mac is **9.5.0**. The Docker Compose alternative uses **MySQL 8.4**. The project backend declares **Spring Boot 3.4.5** and targets **Java 17**.

## Architecture and request flow

```text
Browser: React / Vite, port 5173
       |
       | same-origin /api requests through the Vite proxy
       v
Spring Security -> Controller -> ProblemService -> JPA Repository
                                      |
                                      +-> Scheduler.next(...)
                                      |
                                      v
                              MySQL, port 3307
```

For a completed revision:

1. The browser submits the problem ID, grade, session cookie, and CSRF header.
2. Spring Security verifies access and the mutation security check.
3. The controller validates the grade.
4. The service resolves the signed-in account and locks its owned problem.
5. The scheduler calculates the new interval and due date.
6. The transaction stores a revision row and updates the problem's current state.
7. A response DTO returns the new state to React.

## Main screens

| Screen | Purpose |
| --- | --- |
| Overview | What to revise today and how preparation is progressing |
| My problems | Search, filter, add, view, edit, delete, and export problems |
| Revision queue | Due and overdue problems; focused recall sessions |
| Analytics | Recall performance, period activity, topic confidence, and history |
| Mistake notebook | Reusable lessons associated with problems |
| Settings | Name, goal, timezone, export, and logout |

## Database design

There are three application tables:

| Table | Important data | Relationships |
| --- | --- | --- |
| `users` | Email, BCrypt password hash, name, daily goal, timezone | One account owns many problems and revisions |
| `problems` | Title, URL, topic, difficulty, approach, notes, confidence, interval, ease, repetition count, next date | Each problem belongs to an account |
| `revisions` | Problem, owner, grade, UTC review time, former due date, resulting interval | Each attempt belongs to a problem and its owner |

The stored `password_hash` is not returned to the browser. The server obtains the owner from the authenticated session rather than accepting an owner ID from the client.

## Spaced-repetition algorithm

The scheduler is **SM-2-inspired**, with a simpler four-grade interface. It is not a machine-learning model or an exact implementation of the original SM-2 formula.

- A newly added problem is first due **tomorrow**.
- `repetitions` counts successful reviews.
- `ease` controls interval growth; new problems start at **2.5**.
- Intervals stay between **1 and 365 days**.
- Dates are calculated from today in the account's timezone, including overdue reviews.

| Grade | Scheduling behavior |
| --- | --- |
| Again | 1 day; reset repetitions; lower ease by 0.20, with a 1.30 floor |
| Hard | Round previous interval × 1.20; keep repetitions; lower ease by 0.15 |
| Good | First success: 1 day; second: 6 days; later: previous interval × ease |
| Easy | First success: 4 days; later: max(previous + 1, previous × (ease + 0.30)); increase ease by 0.15 up to 3.00 |

Example: previous interval **6 days**, successful repetitions **2**, ease **2.5**:

| Choice | Next interval |
| --- | --- |
| Again | 1 day |
| Hard | 7 days |
| Good | 15 days |
| Easy | 17 days |

Confidence values map the latest recall grade to **20%, 45%, 75%, or 95%**. They are self-reported indicators, not probabilities of interview success. Problem difficulty is stored, but it is not an extra scheduling multiplier in this version.

## Security explanation

- **BCrypt:** passwords are hashed before storage and checked by Spring Security.
- **Sessions:** the backend stores authentication in the HTTP session; the browser uses an HttpOnly cookie.
- **CSRF:** unsafe requests require a session token obtained from `/api/auth/csrf`.
- **Owner scoping:** every private problem query checks the signed-in account. Another user's ID does not grant access.
- **DTO validation:** input lengths, required fields, URLs, grades, difficulty, and preferences are constrained.
- **Transactions and locking:** review history and current schedule change together; a row lock serializes concurrent review updates.

The presentation account uses this same security flow. It is seeded data, not a hardcoded login shortcut.

## Important files to explain during evaluation

| File | What to explain |
| --- | --- |
| `src/main.tsx` | Application screens, state, forms, and user workflows |
| `src/api.ts` | JSON transport, same-origin sessions, CSRF handling, errors |
| `src/model.ts` | Frontend types, date helpers, browser-demo data and scheduler |
| `src/components/ProblemTable.tsx` | Reusable library/queue table |
| `backend/.../ProblemController.java` | Problem and revision REST endpoints |
| `backend/.../ProblemService.java` | Ownership, transactions, persistence, review updates |
| `backend/.../Scheduler.java` | Pure interval calculation; good file for a code walkthrough |
| `backend/.../Models.java` | Account, problem, and revision JPA entities |
| `backend/.../Repositories.java` | Account-scoped database selection and write lock |
| `backend/.../AuthController.java` | Registration, session login, current user, preferences |
| `backend/.../SecurityConfig.java` | Authentication, sessions, CSRF, route protection |
| `backend/.../PresentationData.java` | Opt-in, idempotent presentation account fixture |
| `scripts/present.mjs` | Local presentation startup and process management |

The `backend/.../` paths above refer to `backend/src/main/java/com/interviewrecall/`.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/auth/csrf` | Obtain the request security token |
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Authenticate a session |
| POST | `/api/auth/logout` | End the session |
| GET | `/api/auth/me` | Read the signed-in account |
| PUT | `/api/auth/preferences` | Save name, goal, and timezone |
| GET / POST | `/api/problems` | List owned problems / create a problem |
| PUT / DELETE | `/api/problems/{id}` | Edit / remove an owned problem |
| POST | `/api/problems/{id}/reviews` | Grade recall and reschedule |
| GET | `/api/revisions` | Read owned revision history |

## Verification commands

```sh
# From the project directory
npm test
npm run build

# Backend tests use an isolated H2 database, not the presentation database
cd backend
mvn test
```

**Current automated result: 15 tests passed** — 7 Java scheduler tests, 3 API integration tests, 1 presentation-fixture integration test, and 4 frontend scheduler tests. The presentation-fixture test checks that the seeded account can sign in and that running the fixture again preserves edits without duplicating its records. Browser checks cover adding, revealing, grading, reload persistence, searching, editing, deletion, navigation, and responsive bounds.

The local account was also verified through Chrome against real MySQL 9.5.0, including login, the seeded dataset, storing large approach/note fields, a review transaction, reload persistence, temporary-record cleanup, and logout. The real-MySQL check found and fixed an initial row-size issue by mapping long notes and approaches to `TEXT`; DTO validation still limits each field to 10,000 characters.

To repeat that specific smoke check while the presentation services are running:

```sh
node tests/presentation-check.mjs
```

It expects the initial 12-problem/41-revision dataset and cleans up only the temporary problem it creates. After you use or edit the demo account, those exact fixture counts can change.

## Common presentation questions

**Why use spaced repetition?**

It provides a practical rule for deciding when to revisit an approach, with shorter intervals after forgetting and longer intervals after successful recall. The project demonstrates the workflow; it does not claim experimentally measured retention improvement.

**Why Java instead of an AI service?**

The schedule is small and deterministic. Java keeps the backend within the project's stack, and a pure function makes the behavior easy to explain and test without paid services or training data.

**Why keep the scheduler on the backend?**

It prevents a client-provided date from becoming authoritative and lets history and the new schedule be persisted reliably in one transaction.

**How is one user's data separated from another's?**

The backend resolves the session identity and passes the account ID into repository queries. Cross-account operations are tested, including review, edit, and delete attempts.

**Why are there both a browser demo and a demo account?**

The browser demo allows UI exploration without a server. The presentation account demonstrates real authentication and MySQL persistence through the Java backend.

**What makes this more useful than a CRUD tracker?**

The main workflow connects recall-before-reveal, adaptive dates, preserved mistake notes, interval previews, and progress derived from review history. CRUD is the supporting foundation.

**What is future work?**

Email verification and recovery, rate limiting, durable sessions, production migrations and deployment, broader accessibility/performance checks, related-pattern connections, and interview countdown planning.

## Troubleshooting

- **The login says the Java backend is unavailable:** start `npm run present` and inspect `.local/backend.log`.
- **Port 3307 is occupied:** choose another port, for example `PRESENTATION_DB_PORT=3310 npm run present`.
- **The account is missing when reusing a backend:** stop that backend through its own terminal and run the presentation command, or start Java with `-Dspring-boot.run.profiles=presentation` against the presentation database.
- **The app still shows Alex Morgan and a local-demo label:** you have not signed in to the presentation account yet.
- **A mutation fails its session security check:** refresh the page and sign in again.
- **You want to preserve preparation work:** keep `.local/mysql`. Do not delete the directory or run destructive database-reset commands.
- **The published static preview rejects these credentials:** that preview has no Java account service; use http://127.0.0.1:5173 for the presentation account.
