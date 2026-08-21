# System Overview — AIProjects / Atlas

> Living architecture snapshot derived from the checked-in source (not assumed AI-generated correctness).
> Last reviewed: 2026-08-21

## Repository identity

| Item | Value |
|------|-------|
| GitHub | `CJ-Covance/AIProjects` |
| Primary product | **Atlas — Unified Knowledge Platform** |
| Sibling products in-repo | Confluence2.0, .NET User API sample, Jira Test Data Importer, SchemaDoc specs |
| Local path referenced by requester | `C:\My Workspace\SrcCodes\PGSEmbarkService\PGSEmbarkService` |

**Path note:** `PGSEmbarkService` is **not present** in this repository (no matches for Embark / PGSEmbark / EmbarkService). All documentation below is grounded in the code that actually exists under `/workspace`. If Embark is a separate product, it must be provided as another repo or path before Embark-specific implementation work.

## What Atlas does

Atlas centralizes organizational knowledge in a hierarchy and answers natural-language questions with grounded, cited RAG responses:

```
Source (root)
 └── Domain
      └── Project
           └── Web Page(s)  →  Chunk(s) + embeddings
```

Tagline (product copy): *Ask once. Receive one clear, consolidated answer.*

## Runtime topology

```
Browser (Next.js :3000)
    │  REST JSON (NEXT_PUBLIC_API_URL)
    ▼
FastAPI (uvicorn :8000)
    ├── routers/     HTTP boundary
    ├── services/    embeddings, indexer, RAG
    └── SQLAlchemy → SQLite (atlas.db)
                          └── OpenAI (embed + chat)
```

Docker Compose (`docker-compose.yml`) builds only Atlas backend + frontend. Sibling projects are **not** composed into that stack.

## Tech stack (implemented POC)

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 App Router, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn |
| Persistence | SQLite (`DATABASE_URL`, default `sqlite:///./atlas.db`) |
| Vectors | Embeddings stored as JSON text on `chunks`; in-process cosine similarity |
| AI | OpenAI `text-embedding-3-small` + `gpt-4o-mini` |
| Auth | **None** (all endpoints/UI are open) |
| Migrations | **None** (`Base.metadata.create_all` on startup) |
| Tests | **None** for Atlas frontend/backend |

## Implemented UI surfaces

| Route | Page | Purpose |
|-------|------|---------|
| `/` | Ask | Question + optional scope filters → answer + citations |
| `/browse` | Browse | Hierarchy tree + page counts |
| `/manage` | Manage | Cascading CRUD for sources → domains → projects → pages |

## Implemented API surface (summary)

- `GET /api/health`
- `GET /api/hierarchy`
- `POST /api/search`
- Full CRUD under `/api/sources`, `/api/domains`, `/api/projects`, `/api/pages`

Page create/update triggers re-indexing (chunk → embed → store). Delete removes chunks then the page.

## Target architecture vs current code

`docs/poc/` describes a fuller UKP (connectors, hybrid retrieval, ACL, SSO, pgvector, observability). **That vision is not implemented** in the current Atlas tree. Treat POC docs as product intent; treat `backend/` + `frontend/` as the source of truth for what ships today.

## Sibling projects (do not mix into Atlas changes)

| Path | Role |
|------|------|
| `confluence2/` | Separate Express + Postgres FTS + Gemini RAG rebuild |
| `dotnet-api-test/` | .NET Framework 4.8 User API + WinForms AWS console sample |
| `JiraTestDataImporter/` | .NET Framework console: Jira → SQL Server upsert |
| `docs/schema-analyzer/` | Spec-only SchemaDoc AI tool (no app code) |

## Documentation layout (this `/claude/` tree)

| Area | Purpose |
|------|---------|
| `claude/master/` | Cross-cutting rules for the primary Atlas app |
| `claude/modules/` | Per-module summaries, rules, types, deps, risks |
| `claude/sql/` | Persistence conventions and inventory |
| `claude/sessions/` | Dated plans for concrete change work |

When adding a **new application page**, follow `layering-rules.md`, `coding-standards.md`, and `modules/AtlasFrontend/*` before coding. Confirm page requirements in a session plan first.
