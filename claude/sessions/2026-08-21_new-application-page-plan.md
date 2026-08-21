# Session plan — New application page (preparation)

**Date:** 2026-08-21  
**Topic:** Establish architecture baseline and prepare to implement a new Atlas application page  
**Branch:** `genomicsai/claude-architecture-docs-c5c8`  
**Status:** Documentation complete — **page requirements not yet specified**

---

## 1. Objectives for this session

1. Inspect the repository that the cloud agent actually has (`CJ-Covance/AIProjects`).
2. Identify the primary application vs sibling projects.
3. Create the shared `/claude/` documentation layout (master, modules, sql, sessions).
4. Capture rules so a subsequent page implementation follows existing architecture.

## 2. Findings (inspection)

### Path discrepancy

Requester cited:

`C:\My Workspace\SrcCodes\PGSEmbarkService\PGSEmbarkService`

**Result:** No `PGSEmbarkService` / Embark sources exist in this repo. Work proceeds against **Atlas** (`backend/` + `frontend/`), which is the primary product in `AIProjects`.

### Primary app snapshot

- Backend: FastAPI + SQLAlchemy + SQLite + OpenAI RAG
- Frontend: Next.js App Router pages Ask (`/`), Browse (`/browse`), Manage (`/manage`)
- No auth, no migrations, no Atlas automated tests
- Design tokens: Atlas navy/teal Tailwind utilities

### Sibling projects (out of default page scope)

- `confluence2/`, `dotnet-api-test/`, `JiraTestDataImporter/`, `docs/schema-analyzer/`

## 3. Documentation delivered

```
claude/
  master/
    system-overview.md
    layering-rules.md
    coding-standards.md
    review-checklist.md
    sql-standards.md
  modules/
    AtlasBackend/
    AtlasFrontend/
    Confluence2/
    JiraTestDataImporter/
    UserApiDotNet/
  sql/
    AtlasSQLite/
  sessions/
    2026-08-21_new-application-page-plan.md  (this file)
```

## 4. How a new page will be implemented (ready checklist)

When page requirements arrive, execute in this order:

1. **Clarify requirements** — route path, nav label, user job-to-be-done, data dependencies, read-only vs mutations.
2. **Update this session plan** (or add `YYYY-MM-DD_<page>-plan.md`) with acceptance criteria.
3. **Backend (only if needed)** — schemas → router/service → register in `main.py` → update `modules/AtlasBackend/public-types.txt`.
4. **Frontend**
   - Add `frontend/src/app/<route>/page.tsx` (`"use client"` if interactive)
   - Extend `lib/types.ts` + `lib/api.ts` as needed
   - Extract shared UI to `components/` only if reused
   - Register link in `Navbar`
   - Match Ask/Browse/Manage shell + `atlas-*` classes
5. **Review** against `claude/master/review-checklist.md`
6. **Risks** — update module `known-risks.md` if introducing new concerns
7. Smoke test: load page, nav active state, API happy path + error path

## 5. Explicit non-actions this turn

- No application page UI/API code changes yet (requirements incomplete).
- No Embark-specific work (source absent).
- No redesign of Atlas visual system.
- No auth/migration framework introduction.

## 6. Blockers / inputs needed from requester

Provide the next message with at least:

| Input | Why needed |
|-------|------------|
| Page name + route (e.g. `/insights`) | Navbar + App Router folder |
| Primary user goal | One job per section |
| Data source (existing API vs new endpoint) | Layering + schema work |
| Wireframe or field list | Avoid speculative UI |
| Confirm target app is Atlas (not PGSEmbarkService) | Prevent building in the wrong product |

## 7. Exit criteria for “prep” (met)

- [x] Codebase inspected
- [x] `/claude/` tree created to repo standard
- [x] Master rules + Atlas module docs written
- [x] Session plan recorded
- [ ] New page implemented (blocked on requirements)
