# Build: SchemaDoc AI — AI-Powered Database Schema Analyzer

## Role

You are a senior full-stack engineer. Build a production-ready web application that ingests database schema files and produces enterprise-grade documentation and design artifacts derived **only** from parsed schema evidence.

**Client constraints (mandatory):**

- **No application database.** Do not use PostgreSQL, SQL Server, MySQL, SQLite, or any DB for app persistence.
- **File-based storage only.** All projects, parsed schemas, analysis results, exports, and session data must be saved as structured text files (JSON, Markdown, YAML) on the local filesystem or a mounted volume.
- **Backend: Python** (FastAPI recommended).
- **Frontend: React** (Vite + TypeScript recommended).
- **Client deliverable:** Generate a **printable PDF report** suitable for stakeholder review and discussion.

Do not invent tables, columns, relationships, or business rules unsupported by the uploaded schema. Document every inference.

---

## Product Summary

**SchemaDoc AI** lets users upload a database schema, run AI-assisted analysis, review structured deliverables in a React UI, and export a **client-ready PDF** plus Markdown/HTML.

The app acts as a combined Business Analyst, Solution Architect, Product Owner, QA Lead, and Technical Architect.

**Core principle:** Every artifact cites schema evidence (table/column/FK names). No placeholder or lorem ipsum content.

---

## Non-Goals (v1)

- No live database connectors or schema sync
- No SQL execution against customer databases
- No application database (even SQLite)
- No billing/subscriptions
- No multi-user cloud tenancy (single-user or simple local auth is fine for v1)
- No claims of regulatory compliance — only risk flags

---

## Technology Stack (required)

| Layer | Technology |
|-------|------------|
| Frontend | React 18+, TypeScript, Vite, Tailwind CSS, ShadCN UI (or equivalent) |
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| AI | OpenAI API with structured JSON output (model via env var) |
| Persistence | **Filesystem only** — JSON + Markdown + plain text |
| PDF export | WeasyPrint, ReportLab, or HTML → PDF (Playwright) |
| Auth (optional v1) | Simple API key or local session file; JWT in file if needed |
| Deployment | Docker Compose (API + React static build + shared `/data` volume) |

---

## File-Based Storage Layout

All data lives under a configurable root (default `./data/`):

```
data/
├── projects/
│   └── {project_id}/
│       ├── meta.json                 # name, dialect, status, timestamps
│       ├── uploads/
│       │   └── {upload_id}/
│       │       ├── original.sql      # raw upload
│       │       └── parse-log.txt
│       ├── schema/
│       │   └── schema.json           # normalized SchemaModel
│       ├── analysis/
│       │   ├── job.json              # status, progress, errors
│       │   └── prompts/              # optional audit trail
│       ├── deliverables/
│       │   ├── feature-inventory.json
│       │   ├── frd.json
│       │   ├── user-stories.json
│       │   ├── ui-screens.json
│       │   ├── menu-structure.json
│       │   ├── role-matrix.json
│       │   ├── workflows.json
│       │   ├── er-diagram.mmd
│       │   ├── api-spec.json
│       │   ├── openapi.json
│       │   ├── test-cases.json
│       │   ├── prd.json
│       │   ├── gap-analysis.json
│       │   └── bi-summary.json
│       └── exports/
│           ├── client-report.pdf     # primary client artifact
│           ├── full-report.md
│           └── full-report.html
└── index.json                        # project registry (id, name, updatedAt)
```

**Rules:**

- Atomic writes: write to `.tmp` then rename
- `index.json` is the only project listing source
- No binary DB files; uploads may be `.sql` text only
- Schema hash stored in `meta.json` for cache invalidation

---

## Phased Delivery

### Phase 1 — MVP (ship first)

1. React UI: project list, upload, analysis progress, dashboard
2. Python parser: PostgreSQL + SQL Server DDL (minimum)
3. FastAPI endpoints for upload, analyze, fetch deliverables
4. File-based project CRUD
5. AI pipeline with structured JSON deliverables (1–6, 8, 12)
6. **Client PDF report** generation (printable, branded cover + TOC)
7. Markdown + HTML export

### Phase 2

- Remaining deliverables (7, 9–11)
- OpenAPI JSON download
- Interactive ER diagram in React
- DOCX/XLSX export

### Phase 3

- Analysis versioning (folder per version)
- Custom domain templates
- Optional simple auth

---

## User Workflow

### Step 1 — Create Project & Upload Schema

**Supported inputs:**

- `.sql` DDL: SQL Server, MySQL, PostgreSQL, Oracle
- Schema JSON (canonical format below)
- ERD/text exports (parse structural content; fail gracefully otherwise)

**Limits:** 10 MB max file; warn above 200 tables; reject above 500.

**Parser extracts:** tables, columns, PKs, FKs, constraints, indexes, views, procedures, functions, triggers.

**Canonical Schema JSON:**

```json
{
  "dialect": "postgresql",
  "tables": [{
    "name": "users",
    "columns": [{ "name": "id", "type": "uuid", "nullable": false, "isPrimaryKey": true }],
    "foreignKeys": [{ "column": "role_id", "references": { "table": "roles", "column": "id" } }]
  }]
}
```

On parse failure: return statement-level errors; do not run AI.

### Step 2 — AI Schema Analysis

Async job with states: `Queued → Parsing → Analyzing → Generating → Complete | Failed`.

**Pipeline:**

1. Structural analysis (master, transaction, audit, lookup, junction, reporting, security tables)
2. Domain detection with confidence 0–100 and evidence
3. Module clustering
4. Deliverable generation (one JSON file per type)
5. Gap analysis (rules + LLM recommendations)

**Constraints:**

- OpenAI structured outputs / Pydantic validation
- Chunk by functional module, not arbitrary tokens
- Cache by `(schemaHash + promptVersion)` in filesystem
- Progress via polling or SSE

### Step 3 — Review & Export

- Browse deliverables in React
- **Download Client Discussion PDF** (primary export for stakeholders)
- Download Markdown, HTML, ZIP bundle

---

## Deliverables

Each deliverable is a JSON (or `.mmd`) file with `evidence[]` and `relatedTables[]` on every item.

| # | Deliverable | Key fields |
|---|-------------|------------|
| 1 | Feature Inventory | name, description, relatedTables, complexity, businessValue, evidence |
| 2 | FRD | modules with purpose, inputs, rules, outputs, dependencies, validation |
| 3 | User Stories | persona, story, acceptanceCriteria, priority, storyPoints |
| 4 | UI Screen List | screenName, purpose, controls, gridColumns, actions, validationRules |
| 5 | Menu Structure | nested tree JSON |
| 6 | Role Permission Matrix | roles × screens × CRUD/Export/Approve |
| 7 | Business Workflows | Mermaid flowcharts + BPMN-style text |
| 8 | ER Diagram | Mermaid `erDiagram` with cardinality |
| 9 | API Requirements | REST per entity + OpenAPI 3.1 JSON |
| 10 | Test Cases | functional, integration, security, performance |
| 11 | PRD | vision, goals, personas, NFRs, risks, metrics |
| 12 | Gap Analysis | audit, security, lookup, history, soft delete, indexes, etc. |

**Additional outputs:** BI summary, complexity score, architecture recommendations, security review.

---

## Client PDF Report (required)

The PDF is the **primary artifact for client meetings**. It must be:

- **Printable** (A4, margins, page numbers, TOC)
- **Professional** (cover page, executive summary, section headers)
- **Self-contained** (readable without the web app)
- **Schema-grounded** (tables/features cited from upload)

**Suggested PDF structure:**

1. Cover — project name, date, schema dialect, table count
2. Executive Summary — domain detected, complexity score, top findings
3. Schema Overview — entity list, relationship summary, ER diagram (rendered or listed)
4. Feature Inventory (top features table)
5. Gap Analysis (severity-rated table + recommendations)
6. User Stories (priority subset)
7. UI Screens & Menu (summary tables)
8. API Overview (endpoint count + sample specs)
9. Architecture & Security Recommendations
10. Appendix — full tables list, methodology disclaimer

Generate via Python (`reportlab` or HTML template → PDF). Store at `exports/client-report.pdf`.

---

## Backend API (FastAPI)

Base: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/projects` | List/create (reads/writes `index.json`) |
| GET/DELETE | `/projects/{id}` | Get/delete project folder |
| POST | `/projects/{id}/upload` | Multipart schema upload |
| POST | `/projects/{id}/analyze` | Start analysis job |
| GET | `/projects/{id}/jobs/status` | Job status from `job.json` |
| GET | `/projects/{id}/dashboard` | Aggregated metrics |
| GET | `/projects/{id}/deliverables` | List available files |
| GET | `/projects/{id}/deliverables/{type}` | Return JSON/MMD content |
| POST | `/projects/{id}/export/pdf` | Generate client PDF |
| GET | `/projects/{id}/exports/{filename}` | Download export file |

CORS enabled for React dev server.

---

## React Pages

| Route | Page |
|-------|------|
| `/` | Project list |
| `/projects/:id` | Dashboard metrics |
| `/projects/:id/upload` | Upload + parse status |
| `/projects/:id/analysis` | Job progress + BI summary |
| `/projects/:id/features` | Feature Inventory |
| `/projects/:id/frd` | FRD |
| `/projects/:id/stories` | User Stories |
| `/projects/:id/screens` | UI Screens |
| `/projects/:id/menu` | Menu Structure |
| `/projects/:id/permissions` | Role Matrix |
| `/projects/:id/workflows` | Mermaid workflows |
| `/projects/:id/er-diagram` | ER diagram |
| `/projects/:id/apis` | API spec |
| `/projects/:id/tests` | Test Cases |
| `/projects/:id/gaps` | Gap Analysis |
| `/projects/:id/export` | **Download Client PDF** + other formats |

**UX:** responsive, loading states, Mermaid rendering, prominent **“Download PDF for Client Review”** button.

---

## Quality & Acceptance Criteria

1. Every deliverable includes `evidence` or `relatedTables`
2. Consistent IDs (F-*, US-*, TC-*)
3. Cross-artifact consistency (same module names everywhere)
4. No placeholders — enterprise BA/Architect/PO/QA quality
5. Pydantic validation before writing files

**Definition of Done:**

- [ ] Upload SQL/JSON → parse errors or success
- [ ] 50-table sample analyzes in < 5 minutes
- [ ] All Phase 1 deliverables visible in React UI
- [ ] **Client PDF generates and prints cleanly on A4**
- [ ] All persistence is filesystem text files — zero database
- [ ] README with env vars and Docker Compose instructions
- [ ] Sample schema in `samples/healthcare-lab.sql`

---

## Environment Variables

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1
DATA_ROOT=./data
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_MB=10
```

---

## Implementation Order

1. Repo scaffold (FastAPI + Vite React)
2. Filesystem project service + `index.json`
3. DDL parser (PostgreSQL, SQL Server)
4. Upload + parse pipeline
5. OpenAI analysis worker
6. Deliverable writers (JSON files)
7. React UI pages
8. **Client PDF generator**
9. Docker Compose + README

Start with architecture diagram, folder structure, and Phase 1 plan — then build incrementally with working commits.
