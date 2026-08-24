# AtlasBackend — Summary

FastAPI application under `backend/app/` providing hierarchy CRUD, page indexing, and RAG search for Atlas.

## Responsibilities

- Expose REST API under `/api/*`
- Persist Source → Domain → Project → WebPage → Chunk
- Chunk and embed page content on write
- Retrieve top-k similar chunks and synthesize grounded answers via OpenAI

## Entry points

| File | Role |
|------|------|
| `backend/app/main.py` | App, CORS, lifespan `create_all`, router mounts, `/api/health` |
| `backend/app/config.py` | `Settings` from env |
| `backend/app/database.py` | Engine, session, `Base` |
| `backend/app/models.py` | ORM |
| `backend/app/schemas.py` | Public API DTOs |
| `backend/app/routers/*.py` | HTTP handlers |
| `backend/app/services/*.py` | Embeddings, indexer, RAG |
| `backend/seed_data.py` | Demo clinical-ops knowledge base |

## Dependencies (runtime)

- fastapi, uvicorn, sqlalchemy, pydantic, pydantic-settings
- openai, numpy, httpx, python-dotenv

## Non-goals (current code)

- Authentication / authorization
- Alembic migrations / Postgres / pgvector
- Async OpenAI or background workers
- Hybrid BM25 + vector retrieval
- Document upload parsers (PDF/DOCX)
