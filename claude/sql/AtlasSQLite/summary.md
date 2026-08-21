# AtlasSQLite — Summary

Persistence area for the primary Atlas app. SQLite database file created/used by SQLAlchemy models in `backend/app/models.py`.

## How schema is applied

- Runtime: `Base.metadata.create_all(bind=engine)` in FastAPI lifespan
- Seed: same create_all path inside `seed_data.py` before inserts
- No Alembic; no checked-in `.sql` DDL for Atlas

## Logical schema

1. **sources** — id (str PK), name, description, created_at, updated_at
2. **domains** — FK → sources
3. **projects** — FK → domains
4. **web_pages** — FK → projects; title, content, url
5. **chunks** — FK → web_pages; chunk_index, content, embedding (Text JSON); denormalized source_id/domain_id/project_id without FKs

## Related code

- `backend/app/database.py`
- `backend/app/models.py`
- `backend/seed_data.py`
