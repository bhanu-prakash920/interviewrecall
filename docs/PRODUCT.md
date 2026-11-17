# InterviewRecall — product and implementation plan

## Product direction
A quiet daily cockpit for students who have solved problems but lose the reasoning over time. The main promise is “Keep the approach, not just the acceptance.” The dashboard answers what to revise, how recall is improving, and where to focus. Primary workflow: register → capture a solved problem → receive a first due date → recall without notes → grade recall → see the next due date and updated progress.

## MVP
Personal accounts; problem title/URL/platform/difficulty/topic/approach/mistake notes; search and topic filters; daily due queue; hidden notes in focus mode; four recall grades; persisted revision history; topic confidence and activity analytics; account preferences. A clearly labeled local demo allows evaluation without a database. Demo data stays in the browser and is separate from authenticated API data.

## Ranked enhancements
| Rank | Enhancement | Value | Effort | Stage |
|---|---|---|---|---|
| 1 | Explain why each problem is due and show next-interval previews | High | Low | MVP |
| 2 | Mistake notebook: capture the trap, not just the solution | High | Low | MVP |
| 3 | Weak-topic lens, derived from actual recall grades | High | Medium | MVP |
| 4 | Pattern connections between problems sharing techniques | Medium | Medium | Later |
| 5 | Interview countdown with bounded daily workload | Medium | Medium | Later |

## Design system
Reference palette: forest #0E2E28, lime #CDFA8A, mint #E6F0ED, background #F4F9F8, border #D5E0DE; warning #8D6E00 and error #B71C1C. Archivo typography, restrained letter spacing, 8px spacing rhythm, 20–28px card corners. White translucent panels, thin white borders, soft shadows and backdrop blur convey glass without sacrificing text contrast. Fixed desktop sidebar, responsive drawer on mobile; generous main content width and a task-first dashboard. Supplied standalone SVG illustrations are used as accents; exported SVGs depending on missing sprite symbols are excluded. Buttons use SVG icons, visible focus, 44px targets, and reduced-motion support. The external UI UX Pro Max guidance informs accessibility and responsive behavior while the supplied palette remains authoritative.

## Architecture
React + Vite + TypeScript + Tailwind frontend. A small API adapter handles session/CSRF, DTOs and HTTP errors. Local demo uses browser storage; it must never be represented as server persistence. Java 17 Spring Boot monolith with Web, Security, Data JPA, validation and MySQL. Controllers own HTTP, services own scheduling and transactions, repositories own owner-scoped queries. Frontend hosted preview is a browser-local demo; Java server is run separately for real accounts.

## Relational model
users(id, email unique, password_hash, name, daily_goal, zone_id); problems(id, user_id FK, title, url, platform, difficulty, topic, notes, approach, confidence, interval_days, repetitions, ease, solved_on, next_review_on); revisions(id, user_id FK, problem_id FK, grade, reviewed_at UTC, scheduled_on, interval_days). Index (user_id, next_review_on). Every private read/write derives user identity from the server session. Revision changes and history insertion share a transaction. Dates use each user's IANA zone; timestamps use UTC. No client-controlled owner IDs.

## REST API
GET /api/auth/csrf; POST /api/auth/register; POST /api/auth/login; POST /api/auth/logout; GET /api/auth/me; PUT /api/auth/preferences; GET/POST /api/problems; PUT/DELETE /api/problems/{id}; GET /api/revisions; POST /api/problems/{id}/reviews with grade 0–3. Auth uses BCrypt, HttpOnly same-site session cookies, CSRF protection and same-origin requests through the Vite proxy. No tokens in localStorage. Validation errors have actionable JSON messages. Production requires HTTPS and secure cookies.

## Explainable scheduler
A small SM-2-inspired deterministic scheduler, rather than ML. New problems are due tomorrow. Grades: Again (0), Hard (1), Good (2), Easy (3). Again resets repetitions and interval to one day and lowers ease (floor 1.3). Hard uses max(1, round(previous interval × 1.2)), lowers ease, and does not advance successful repetitions. Good uses 1 day on first success, 6 on second, then previous interval × ease. Easy uses 4 days on first success, then max(previous + 1, previous × (ease + .3)), increases ease to a 3.0 ceiling. Intervals cap at 365 days. Scheduling starts from today's date in the user's zone, even when overdue. A missed day does not silently count as a successful recall. Grade previews use the same algorithm; backend is authoritative in account mode.

## Phases and verification
1. Product and architecture: this document.
2. UI: responsive dashboard, problem library, revision focus, analytics, notebook and preferences with explicit demo mode.
3. Core backend: authentication, owner-scoped CRUD, atomic review updates and history, MySQL configuration.
4. Connect frontend to backend; keep local preview useful without claiming hosted Java support.
5. Validate build/type checks; scheduler edge cases, account isolation, CSRF and authentication integration tests; document local MySQL setup and production limitations.

Risks: small sample histories make trends noisy; label sample data. Daily grouping must use user timezones. Forgotten problems should recur without creating an unbounded overdue penalty. Browser demo is device-local and is not a substitute for authentication. Production hardening includes login rate limits, email verification/reset, migrations, backups, and persistent session storage.
