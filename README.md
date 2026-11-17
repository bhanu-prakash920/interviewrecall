# InterviewRecall

A coding interview revision companion built with React, TypeScript, Vite, Tailwind, Java 17, Spring Boot, and MySQL.

## Start the local demo

```sh
npm ci
npm run dev
```

Open http://127.0.0.1:5173. The clearly labeled demo contains sample problems and revision history. Adding, searching, filtering, reviewing, deleting, preferences, analytics and JSON export work locally. Demo changes stay in this browser. Sample history is illustrative; no charts claim live telemetry. No AI or paid service is needed.

## Start the complete account workflow

Prerequisites: Node 20.19+ or 22.12+, Java 17+, Maven 3.6+, Docker Compose (or an existing MySQL 8 database).

From this directory:

```sh
docker compose up -d --wait
```

In another terminal:

```sh
cd backend
mvn spring-boot:run
```

Start the frontend with `npm run dev`. In **Connect your account**, choose **Create an account**. Real accounts start with an empty library. The Vite development proxy sends `/api` requests to port 8080, keeping cookies and CSRF on the same origin. The hosted static preview does not host Java; use the local server for authentication and database persistence.

The local database credentials in `compose.yaml` are development defaults. To use an existing database, set `DB_URL`, `DB_USER`, and `DB_PASSWORD` before launching Java. Stop the database with `docker compose down`; omit `-v` to preserve data.

## Validate

```sh
npm run build
npm test
cd backend
mvn test
```

Backend integration tests use H2 in MySQL compatibility mode and do not require a running MySQL instance. They exercise registration, login, CRUD, forbidden cross-account access, review persistence, validation, CSRF, and logout. Scheduler tests cover forgotten problems, interval progression, floors/caps, invalid grades, year rollover and timezone boundaries. These tests do not replace deployment validation against a real MySQL server.

Browser QA (requires Google Chrome and a running `npm run dev`):

```sh
npm run test:ui
```

## Product and architecture

Read [the product plan](docs/PRODUCT.md) for the MVP, ranked enhancements, schema, API design, scheduler and implementation roadmap.

- `src/model.ts`: frontend DTO types, local demo seed and scheduler mirror.
- `src/api.ts`: same-origin cookie/CSRF transport.
- `src/main.tsx`: application state, screens and workflows.
- `src/components`: reusable problem table, metric and activity components.
- `src/styles.css`: reference-driven design system and responsive styles.
- `backend/src/main/java/com/interviewrecall`: controllers, services, repositories, entities, scheduler and security.

The backend owns scheduling for account data. The browser algorithm is used only in demo mode and interval previews. Every review saves its history and new schedule in one database transaction; a row lock serializes simultaneous reviews of the same problem.

## Design

Supplied forest, lime and mint palette; Archivo typography; quiet frosted panels with backdrop blur. Standalone illustrations from the supplied assets are in `public/assets`. Accessibility/responsive guidance was consulted from [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). Glass styling preserves solid text and focus outlines; reduced-motion is supported. No dark mode is currently implemented.

## Deployment limits

The Sites deployment is a private static demo. To deploy full-stack accounts, build the frontend and serve it behind an HTTPS reverse proxy that forwards `/api` to Spring Boot, with MySQL on a private network. Set `COOKIE_SECURE=true`. Add production migrations, rate limits, email verification/password reset, backups and durable sessions before a public launch. Current JPA `ddl-auto=update` is for local development. No third-party platform scraping or automatic problem import is implemented.
