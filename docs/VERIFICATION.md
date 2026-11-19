# Verification

- Production: TypeScript and Vite build pass.
- Browser: Chrome, no runtime page errors; add, edit while preserving schedule, reveal notes, grade recall, reload persistence, search, deletion, all navigation and mobile drawer pass.
- Responsive: document overflow checks pass at 375, 768, 1024 and 1440 pixels. Desktop and mobile screenshots were visually inspected. Tables scroll inside their cards when necessary.
- Frontend scheduler: 4 tests pass (reset/floor, progression, hard/easy bounds, date and timezone boundaries).
- Backend: 11 tests pass (7 scheduler tests, 3 API integration tests, 1 presentation-fixture integration test). Account isolation includes attempts to read, modify, review and delete another user's problem. CSRF, invalid grades, login failure and logout are covered.
- Automated database integration tests use H2 MySQL compatibility mode. Live local MySQL 9.5.0 on port 3307 was additionally verified during presentation setup: real browser login, 12 seeded problems, 41 sample revisions, 9,500-character approach and note fields, review/history persistence, reload, deletion cleanup, and logout. Docker MySQL 8.4 and public full-stack deployment have not been verified.
- Hosted deployment contains a static browser-local demo; the Java/MySQL account service runs separately through the documented local setup.
- Accessibility checks are manual/code checks for semantic controls, named icon buttons, focus trapping in dialogs, focus outlines and reduced-motion behavior. No automated WCAG certification is claimed.

## Presentation setup — 18 November 2026

- `npm run present` starts an isolated native MySQL database in `.local/mysql`, the Spring Boot `presentation` profile, and Vite (or reuses an existing frontend).
- The profile creates `demo@interviewrecall.test` once and preserves existing records on later starts. The fixture test checks password hashing, login, idempotence, and retained preferences.
- `node tests/presentation-check.mjs` verifies the account through Chrome and actual MySQL; its temporary problem and review are removed at the end. It expects the initial 12-problem/41-revision presentation dataset.
- The MySQL-specific row-size failure found in the first real startup was corrected by mapping approach and notes to `TEXT`, with input limits retained in DTOs.
- Source report PDFs describe their earlier verification stage; this file and PROJECT_EXPLANATION.md document the newer presentation setup.
- Clean restart verified against the live local database: demo credentials, 12 problems, and 41 revision records were preserved.
