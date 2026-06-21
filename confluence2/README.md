# Confluence2.0 — Unified Knowledge Platform

Enterprise RAG knowledge platform rebuilt from the development handoff spec. Authenticated users add knowledge pages (tagged by domain/project), ask one natural-language question, and receive a single AI-synthesized answer with citations back to the exact source pages.

This project lives alongside **Atlas** in the monorepo and does not modify the existing Atlas app.

## Stack

- **API:** Express 5, Drizzle ORM, Postgres full-text search
- **Auth:** Replit OIDC (PKCE) with local dev bypass
- **AI:** Gemini via Replit AI Integration proxy, with direct `GOOGLE_API_KEY` fallback for local dev
- **Web:** React 19 + Vite + React Query
- **Spec:** OpenAPI at `lib/api-spec/openapi.yaml`

## Prerequisites (local, no Docker)

1. **Node.js 20+** and **pnpm**
2. **PostgreSQL 16+** installed on your machine

### Local Postgres setup (Ubuntu/Debian example)

```bash
sudo apt install postgresql postgresql-contrib
sudo pg_ctlcluster 16 main start
sudo -u postgres psql -c "CREATE USER confluence2 WITH PASSWORD 'confluence2';"
sudo -u postgres psql -c "CREATE DATABASE confluence2 OWNER confluence2;"
```

## Quick start

```bash
cd confluence2
cp .env.example .env
pnpm install
pnpm db:push
pnpm dev:all
```

- API: http://localhost:5000
- Web: http://localhost:5173

On first visit, click **Continue with Replit Auth**. When `REPL_ID` is not set, `DEV_AUTH_BYPASS=true` creates a local dev session automatically.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres connection string |
| `REPL_ID` | Replit OIDC client id (set on Replit) |
| `ISSUER_URL` | OIDC issuer (default `https://replit.com/oidc`) |
| `SESSION_SECRET` | Session cookie signing secret |
| `REPLIT_DOMAINS` | Allowed callback domains |
| `AI_INTEGRATIONS_GEMINI_API_KEY` | Replit Gemini proxy key |
| `AI_INTEGRATIONS_GEMINI_BASE_URL` | Replit Gemini proxy base URL |
| `DEV_AUTH_BYPASS` | `true` for local login without Replit Auth |
| `GOOGLE_API_KEY` | Direct Gemini key for local dev fallback |
| `PORT` | API port (default `5000`) |
| `WEB_ORIGIN` | Frontend origin for CORS (default `http://localhost:5173`) |

## Replit deployment

1. Import this repo into Replit.
2. Enable **Replit Auth** and **Replit AI (Gemini)** integrations so the env vars in §1 of the handoff are injected automatically.
3. Enable the **Postgres** integration for `DATABASE_URL`.
4. Set `REPLIT_DOMAINS` to your published Repl domain.
5. Run:

```bash
pnpm install
pnpm db:push
pnpm run build
```

6. Configure the Repl to run the API and serve the built frontend through the shared proxy.

Set `DEV_AUTH_BYPASS=false` (or remove it) in production on Replit.

## API overview

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/api/healthz` | No | Health check |
| GET | `/api/login` | No | Start OIDC login |
| GET | `/api/callback` | No | OIDC callback |
| GET | `/api/logout` | No | Logout |
| GET | `/api/auth/user` | Optional | Current user |
| POST | `/api/mobile-auth/token-exchange` | No | Mobile session exchange |
| POST | `/api/mobile-auth/logout` | Yes | Mobile logout |
| GET/POST | `/api/pages` | Yes | List / create pages |
| GET/DELETE | `/api/pages/:id` | Yes | Page detail / delete |
| GET | `/api/knowledge-stats` | Yes | Totals + top domains |
| GET | `/api/workspaces` | Yes | Domain/project counts |
| POST | `/api/ask` | Yes | Ask question |
| GET | `/api/ask/history` | Yes | Recent questions |

## Ask flow

1. `requireAuth` validates the session.
2. `retrieveRelevantPages()` runs Postgres FTS (OR-relaxed `websearch_to_tsquery`) with ILIKE fallback.
3. `generateAnswer()` calls Gemini (`gemini-2.5-flash`) with a grounding prompt.
4. Citations are validated against retrieved pages and persisted to `questions`.

## OpenAPI codegen

The OpenAPI spec is the contract at `lib/api-spec/openapi.yaml`.

**Orval** is a tool that reads an OpenAPI file and generates TypeScript types, Zod schemas, and React Query hooks automatically. This MVP uses a hand-written API client plus Zod schemas in `lib/api-client` to keep setup light. To regenerate TypeScript types from the spec:

```bash
pnpm codegen
```

If you later want full React Query hook generation, add [Orval](https://orval.dev/) and point it at `lib/api-spec/openapi.yaml`.

## Project layout

```
confluence2/
├── artifacts/
│   ├── api-server/       # Express API
│   └── confluence2/      # React + Vite frontend
├── lib/
│   ├── api-spec/         # OpenAPI source of truth
│   ├── api-client/       # Shared Zod schemas
│   ├── db/               # Drizzle schema
│   └── integrations-gemini-ai/
└── package.json
```

## Constraints (POC)

- No vector embeddings (Replit AI has no embeddings endpoint); retrieval is Postgres FTS, swappable later.
- Manual knowledge entry only (no PDF upload).
- `/api/ask` returns a single non-streaming JSON response.
