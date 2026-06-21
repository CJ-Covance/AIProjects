# Atlas — Unified Knowledge Platform

> **Ask once. Receive one clear, consolidated answer** — summarized from every relevant page across your organization.

Atlas is an enterprise knowledge platform that centralizes content across a hierarchical structure (Source → Domain → Project → Web Pages) and uses Retrieval-Augmented Generation (RAG) to answer natural-language questions with grounded, cited responses.

## Architecture

```
Source (Root)
 ├── Domain
 │    ├── Project
 │    │    ├── Web Page 1
 │    │    ├── Web Page 2
 │    │    └── Web Page N
 │    └── ...
 └── ...
```

**Tech stack:**
- **Frontend:** Next.js 14, React, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy, SQLite
- **AI:** OpenAI embeddings (`text-embedding-3-small`) + chat (`gpt-4o-mini`)
- **Vector store:** Embeddings stored in SQLite with cosine similarity retrieval

## Features

- **Search / Ask** — Natural-language questions with scope filters (source, domain, project)
- **RAG pipeline** — Retrieves relevant chunks, generates grounded answers with inline citations
- **Browse** — Explore the knowledge hierarchy with page counts
- **Manage** — Full CRUD for sources, domains, projects, and web pages
- **Auto-indexing** — Content is chunked and embedded whenever pages are added or modified
- **No-hallucination guardrails** — Answers are strictly grounded in retrieved content; clearly states when no matching information is found

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- OpenAI API key

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

python seed_data.py          # Load sample clinical-trial knowledge base
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Docker

```bash
export OPENAI_API_KEY=sk-...
docker compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/hierarchy` | Full knowledge tree |
| POST | `/api/search` | RAG-powered question answering |
| GET/POST/PUT/DELETE | `/api/sources` | Source CRUD |
| GET/POST/PUT/DELETE | `/api/domains` | Domain CRUD |
| GET/POST/PUT/DELETE | `/api/projects` | Project CRUD |
| GET/POST/PUT/DELETE | `/api/pages` | Web page CRUD (auto-indexes on write) |

### Search Example

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the data retention policy for clinical trial documents?"}'
```

## Sample Questions

After running `seed_data.py`, try these questions:

- "What is our data-retention policy for clinical trial documents?"
- "Which projects are compliant with the data retention policy?"
- "What are the GDPR requirements for clinical data processing?"
- "How do I upload documents to the eTMF system?"

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/             # API route handlers
│   │   └── services/
│   │       ├── embeddings.py    # OpenAI embedding utilities
│   │       ├── indexer.py       # Chunking & indexing pipeline
│   │       └── rag.py           # Retrieval & answer generation
│   └── seed_data.py             # Sample knowledge base
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (Ask, Browse, Manage)
│       ├── components/          # UI components
│       └── lib/                 # API client & types
├── docs/poc/                    # POC architecture documentation
└── docker-compose.yml
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required for embeddings and answer generation |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat/completion model |
| `DATABASE_URL` | `sqlite:///./atlas.db` | Database connection string |
| `CHUNK_SIZE` | `800` | Characters per text chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `TOP_K_CHUNKS` | `8` | Number of chunks retrieved per query |

## Future Enhancements

- Document upload (PDF, DOCX, HTML)
- PostgreSQL + pgvector for production scale
- Hybrid retrieval (BM25 + semantic)
- SSO / OIDC authentication
- Permission-aware retrieval (ACL filtering)
- Versioning and audit trails
- Connector framework for external systems (Confluence, SharePoint, Jira)

## License

See [LICENSE](LICENSE).

## Confluence2.0 (sibling project)

A separate enterprise RAG platform rebuilt from the Replit POC handoff lives in [`confluence2/`](confluence2/README.md). It uses Express, Postgres FTS, Replit Auth, and Gemini — and does not modify the Atlas app above.
