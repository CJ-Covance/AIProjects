# SQL Standards — Atlas

> Atlas today uses **SQLAlchemy ORM + SQLite**. There are no hand-written stored procedures and no Alembic migrations in `backend/`.

## Current persistence model

| Concern | Practice |
|---------|----------|
| Engine | `DATABASE_URL` (default `sqlite:///./atlas.db`) |
| Session | `SessionLocal` / `get_db` dependency |
| Schema create | `Base.metadata.create_all` on app lifespan (+ seed script) |
| Migrations | **None** — additive ORM fields will not alter existing DB files automatically |
| Raw SQL | Avoid; use ORM queries consistent with routers/services |
| Stored procedures | Not used |

## Tables (logical)

| Table | Purpose |
|-------|---------|
| `sources` | Root hierarchy node |
| `domains` | Child of source |
| `projects` | Child of domain |
| `web_pages` | Content documents under project |
| `chunks` | Indexed text slices + embedding JSON; denormalized `source_id` / `domain_id` / `project_id` **without FK constraints** |

## Rules for schema changes

1. Update `backend/app/models.py` first; keep relationships and cascades explicit.
2. Update Pydantic schemas and frontend types in the same change set.
3. Document the change under `claude/sql/AtlasSQLite/` (summary + known-risks).
4. If existing deployments matter, provide an explicit migration script (even a one-off `.sql` or Python upgrade) — do **not** assume `create_all` upgrades live DBs.
5. Prefer UUID string PKs and UTC timestamps to match existing tables.
6. Do not add UNIQUE constraints on names without product confirmation (duplicates are currently allowed).
7. Soft-delete is not a current pattern; hard delete + cascade is the default.

## Query conventions

- Filter lists by parent id query params where routers already do.
- For RAG, filter `Chunk` by denormalized scope columns; do not load embeddings for unrelated scopes when a filter is present.
- Avoid N+1 count queries when touching list/hierarchy hot paths if you are already editing those endpoints — but do not drive-by rewrite all counters.

## Seed & Docker

- `seed_data.py` is idempotent if any `Source` exists.
- Compose runs seed then uvicorn. Be aware: named volume `atlas-data` → `/app/data` may **not** match default SQLite path `./atlas.db` inside the container — verify persistence when changing deploy layout.

## Sibling SQL (out of Atlas scope)

- `JiraTestDataImporter/Database/SqlScripts/` — SQL Server scripts for the importer only.
- `confluence2/lib/db` — Drizzle + Postgres for Confluence2 only.

Do not reuse those dialects or scripts inside Atlas without an explicit multi-product decision.
