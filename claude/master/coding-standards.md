# Coding Standards — Atlas

> Derived from existing `backend/` and `frontend/` conventions. Match local style over inventing new patterns.

## General

- Prefer small, focused diffs that follow existing file structure.
- Do not add comments that only narrate obvious code.
- Do not add README/docs unless asked — except the maintained `/claude/` tree for architecture work.
- Treat AI-authored code as suspect until reviewed against this file and `review-checklist.md`.

## Backend (Python / FastAPI)

### Language & typing

- Python 3.12+ style: `str | None`, `list[str]`, not `Optional` / `List` unless editing older patterns.
- Use SQLAlchemy 2.0 `Mapped` / `mapped_column`.
- Use Pydantic v2 (`model_config = {"from_attributes": True}`).

### Structure

- One router module per resource (`sources`, `domains`, `projects`, `pages`, `search`).
- Shared create/update/out schemas live in `schemas.py`.
- IDs are UUID4 strings; timestamps UTC via the existing helper pattern on models.
- Cascade deletes follow ORM relationships already defined (`cascade="all, delete-orphan"`).

### Errors & responses

- Raise `HTTPException` with clear `detail` strings.
- List endpoints may accept parent FK query params (`source_id`, `domain_id`, `project_id`).
- Out DTOs include computed counts (`domain_count`, `page_count`, `chunk_count`) via router helpers — keep that pattern.

### Services

- OpenAI clients are created per call today; do not introduce a global singleton without measuring connection needs.
- Embeddings are JSON-serialized into Text columns — preserve encode/decode helpers in embeddings/indexer/rag.
- Keep temperature and system-prompt grounding rules when touching RAG: answers must stay citation-grounded.

### Config

- New tunables go through `Settings` in `config.py` and env vars.
- Update `.env.example` when adding required env keys.

## Frontend (TypeScript / Next.js)

### Language

- TypeScript `strict`; ESLint `next/core-web-vitals` + `next/typescript`.
- Path alias `@/*` → `src/*`.
- Prefer `async`/`await` with try/catch; surface `err instanceof Error ? err.message : fallback`.

### UI patterns

- Client components for interactive pages: `"use client"` at top.
- State: `useState` / `useEffect` / `useCallback` — no Redux/React Query unless a session plan adopts them.
- Styling: Tailwind + Atlas tokens (`atlas-navy`, `atlas-blue`, `atlas-teal`, `atlas-light`, `atlas-accent`) and component classes (`.atlas-card`, `.atlas-btn-primary`, `.atlas-btn-secondary`, `.atlas-input`, `.atlas-select`).
- Avoid introducing a component library (MUI/shadcn) unless planned.
- Page header pattern: bold navy title + one muted supporting sentence.

### API

- All HTTP goes through `lib/api.ts` `request<T>` helper.
- Mirror backend field names (`snake_case` as returned by FastAPI).
- Handle `204` as void; parse FastAPI `detail` on errors.

### Navigation

- Exact pathname match for active nav (see `Navbar`).
- If deep-linking with query params, **read** them with `useSearchParams` on the target page (Browse currently links `/?project=` but Ask does not consume it — fix if extending that flow).

## Naming

| Kind | Convention |
|------|------------|
| Python modules/functions | `snake_case` |
| Python classes | `PascalCase` |
| TS interfaces | `PascalCase` (`Source`, `SearchResponse`) |
| React components | `PascalCase` file + default export matching usage |
| CSS tokens | `atlas-*` prefix |

## Testing expectations (current baseline)

- Atlas has **no** automated tests today. New critical logic (RAG ranking, chunking) should prefer pure functions that are testable; adding a test suite is encouraged but must follow existing layout if/when introduced.
- Sibling .NET projects have their own test conventions — do not apply them to Atlas Python/TS without a plan.

## What not to do

- Do not store secrets in source; use env / `.env` (gitignored).
- Do not switch SQLite → Postgres mid-feature without migration strategy and doc updates.
- Do not add auth middleware as a drive-by change.
- Do not “fix” UI with cards, purple gradients, or new visual systems that fight existing Atlas navy/teal tokens unless redesign is the assigned task.
