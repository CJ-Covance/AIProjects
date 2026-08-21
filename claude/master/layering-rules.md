# Layering Rules — Atlas

> Enforce these boundaries for every change. Crossing layers without cause is a review failure.

## Backend layers (top → bottom)

```
HTTP (routers)  →  Application services  →  ORM models / DB session  →  External APIs (OpenAI)
                 ↗ Pydantic schemas (request/response contracts)
```

| Layer | Location | May depend on | Must not |
|-------|----------|---------------|----------|
| Routers | `backend/app/routers/` | schemas, models, `get_db`, services, FastAPI | Embed OpenAI calls or chunking logic inline; invent response shapes outside `schemas.py` |
| Services | `backend/app/services/` | models, `settings`, OpenAI/numpy helpers | Import FastAPI `Request`/`HTTPException` for business flow (prefer raise domain errors or return status for router mapping); call other routers |
| Schemas | `backend/app/schemas.py` | pydantic only | Import ORM models or services |
| Models | `backend/app/models.py` | SQLAlchemy, `database.Base` | Import routers, OpenAI, FastAPI |
| Config/DB | `config.py`, `database.py` | settings / engine only | Business logic |

### Router rules

1. Keep handlers thin: validate parent FKs, call service or simple CRUD, map to `*Out` helpers.
2. Use `Depends(get_db)` for sessions; commit in the same place existing code does for that resource.
3. Page writes that change content **must** go through `index_web_page` (or explicitly document why not).
4. Prefer existing HTTP status conventions: `404` missing entity, `201` create, `204` delete, `503` when indexing requires OpenAI and key is missing.

### Service rules

1. RAG and indexing live only in `services/rag.py`, `services/indexer.py`, `services/embeddings.py`.
2. Do not duplicate chunking parameters — read from `settings`.
3. Retrieval scope preference is fixed: `project_id` > `domain_id` > `source_id` (only one filter applied). Do not change without a session plan and UI parity update.

## Frontend layers

```
Page (app/*/page.tsx)  →  Shared components  →  lib/api.ts  →  Backend REST
                        ↗ lib/types.ts
```

| Layer | Location | May depend on | Must not |
|-------|----------|---------------|----------|
| Pages | `frontend/src/app/**/page.tsx` | components, `api`, `types`, React hooks | Raw `fetch` to backend (use `api`); duplicate DTO shapes |
| Components | `frontend/src/components/` | `types`, React, Tailwind utilities | Call backend except via props/callbacks owned by page, or shared `api` when already established |
| API client | `frontend/src/lib/api.ts` | `types`, `fetch` | UI / React imports |
| Types | `frontend/src/lib/types.ts` | none | Runtime logic |

### Page composition rules

1. New routes are App Router folders with a `"use client"` page unless there is a clear SSR need (today: all interactive pages are client).
2. Register navigation in `Navbar` `links` array.
3. Reuse shell: `mx-auto max-w-* px-6 py-10`, navy title, muted subtitle, `atlas-*` utility classes from `globals.css`.
4. Extend `api` + `types` when the backend contract changes; keep frontend and backend DTO names aligned.

## Cross-cutting

- **Do not** couple Atlas code to `confluence2/`, `dotnet-api-test/`, or `JiraTestDataImporter/`.
- **Do not** introduce a second HTTP client or parallel schema system without replacing the existing one.
- Auth, ACL, and migration frameworks are out of current architecture — adding them requires a session plan and master-doc update first.
- AI-generated code is not trusted by default: verify against these layering rules and `review-checklist.md`.
