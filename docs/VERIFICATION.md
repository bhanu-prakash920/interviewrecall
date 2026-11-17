# Verification

- Production: TypeScript and Vite build pass.
- Browser: Chrome, no runtime page errors; add, edit while preserving schedule, reveal notes, grade recall, reload persistence, search, deletion, all navigation and mobile drawer pass.
- Responsive: document overflow checks pass at 375, 768, 1024 and 1440 pixels. Desktop and mobile screenshots were visually inspected. Tables scroll inside their cards when necessary.
- Frontend scheduler: 4 tests pass (reset/floor, progression, hard/easy bounds, date and timezone boundaries).
- Backend: 10 tests pass (7 scheduler tests, 3 Spring integration tests). Account isolation includes attempts to read, modify, review and delete another user's problem. CSRF, invalid grades, login failure and logout are covered.
- Database integration tests use H2 MySQL compatibility mode. A live MySQL instance has not been exercised in this environment.
- Hosted deployment contains a static browser-local demo; the Java/MySQL account service runs separately through the documented local setup.
- Accessibility checks are manual/code checks for semantic controls, named icon buttons, focus trapping in dialogs, focus outlines and reduced-motion behavior. No automated WCAG certification is claimed.
