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

- Python 3.9+ (tested on 3.9.5 and 3.12)
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
python -m uvicorn app.main:app --reload --port 8000
```

> **Python 3.9 note:** Use `python -m pip install -r requirements.txt` if `pip` points to a different Python version. The dependency set pins `numpy<2` because NumPy 2.x requires Python 3.10+.

> **Windows note:** Dependencies use pre-built wheels only (no Visual C++ Build Tools required). If you previously failed on `greenlet`, run:
> ```bash
> python -m pip install --upgrade pip
> python -m pip install greenlet==3.2.4 numpy==1.26.4
> python -m pip install -r requirements.txt
> ```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Folder-based knowledge (PDF / HTML)

Atlas maps each Source → Domain → Project to a folder on disk under `backend/knowledge_base/`:

```
backend/knowledge_base/
  Clinical_Operations_Wiki/          ← Source folder
    Clinical_Trials/               ← Domain folder
      Project_Alpha/               ← Project folder
        charter.pdf
        policy.html
```

1. Set optional **Folder name** when creating Sources, Domains, and Projects in **Manage** (defaults to the entity name).
2. Place PDF, HTML, HTM, MD, or TXT files in the project folder.
3. Click **Sync folder from disk** or **Upload file** on the Manage page, or simply **Ask** a question — search auto-syncs files before answering.

Supported file types: `.pdf`, `.html`, `.htm`, `.md`, `.txt`

### Activity logs

Open **Logs** in the navigation bar (`/logs`) to view backend activity, API errors, page save details, and the `backend/logs/atlas.log` file tail. Use this to diagnose "failed to fetch" errors — usually the backend is not running or not reachable at `http://localhost:8000`.

Configure the root path in `backend/.env`:

```env
KNOWLEDGE_BASE_ROOT=knowledge_base
```


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
