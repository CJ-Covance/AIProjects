# SchemaDoc AI — Client Requirements Brief

**Upload a database schema. Receive enterprise documentation and a printable PDF for stakeholder review.**

---

## What we are building

SchemaDoc AI is a web application that acts as an AI-powered **Business Analyst, Solution Architect, Product Owner, QA Lead, and Technical Architect** — all in one.

A user uploads a database schema file (SQL DDL, JSON, or similar). The system parses tables, relationships, and constraints, then generates a full set of software design and business analysis artifacts **derived from that schema**.

The primary output for client discussions is a **professional, printable PDF report** that can be shared in meetings without requiring access to the application.

---

## Client requirements (agreed constraints)

| Requirement | Approach |
|-------------|----------|
| **No application database** | The app does not use PostgreSQL, SQL Server, or any database for its own data |
| **File-based storage** | All projects, parsed schemas, and generated documents are saved as text/JSON files on disk |
| **Python backend** | API, parsing, AI orchestration, and PDF generation run in Python (FastAPI) |
| **React UI** | Modern responsive web interface for upload, review, and export |
| **Client PDF** | One-click generation of a printable PDF for executive and stakeholder review |

This keeps deployment simple (Docker + shared folder), avoids database licensing and administration, and makes outputs easy to archive, email, and audit.

---

## User journey

```mermaid
flowchart LR
    A[Upload schema] --> B[Parse & validate]
    B --> C[AI analysis]
    C --> D[Review in React UI]
    D --> E[Download Client PDF]
    E --> F[Discuss with stakeholders]
```

### Step 1 — Upload schema

Supported formats:

- SQL Server, MySQL, PostgreSQL, Oracle `.sql` scripts
- Database DDL exports
- Schema JSON files
- ERD / documentation exports (where structurally parseable)

The system extracts tables, columns, keys, constraints, indexes, views, procedures, functions, and triggers.

### Step 2 — AI analysis

The engine analyzes:

- **Database structure** — entity relationships, master/transaction/audit/security/reporting tables
- **Business domain** — Healthcare, Laboratory, Finance, Insurance, Banking, Retail, Manufacturing, Logistics, CRM, ERP, HRMS, or custom domains
- **Functional modules** — grouped features inferred from table clusters

### Step 3 — Generated deliverables

| # | Artifact | Purpose |
|---|----------|---------|
| 1 | Feature Inventory | Features mapped to tables with complexity and business value |
| 2 | Functional Requirements (FRD) | Module-level behavior, inputs, rules, outputs |
| 3 | User Stories | Agile stories with acceptance criteria and story points |
| 4 | UI Screen List | Screens, controls, grids, actions, validation |
| 5 | Menu Structure | Hierarchical navigation tree |
| 6 | Role Permission Matrix | CRUD/Export/Approve by role and screen |
| 7 | Business Workflows | Mermaid process diagrams |
| 8 | ER Diagram | Entity-relationship diagram with cardinality |
| 9 | API Requirements | REST specs + OpenAPI JSON |
| 10 | Test Cases | Functional, integration, security, performance |
| 11 | PRD | Product vision, personas, goals, risks, metrics |
| 12 | Gap Analysis | Missing audit, security, indexes, archival patterns, etc. |

**Plus:** domain summary, complexity score, architecture recommendations, security review.

### Step 4 — Client PDF export

A formatted **Client Discussion PDF** includes:

- Executive summary and domain detection
- Schema overview and ER diagram
- Top features and gap analysis
- Sample user stories, screens, and API overview
- Architecture and security recommendations
- Appendix with full table inventory

Designed for **A4 printing**, page numbers, and table of contents.

---

## Technology stack

| Layer | Choice |
|-------|--------|
| UI | React, TypeScript, Tailwind CSS |
| API | Python, FastAPI |
| AI | OpenAI (structured JSON output) |
| Storage | Text/JSON files on filesystem |
| PDF | Python-generated printable report |
| Deploy | Docker Compose (optional) |

**Explicitly excluded:** application database, Azure Blob (optional later), complex auth in v1.

---

## Dashboard metrics

- Tables and relationships count
- Features, screens, APIs, and user stories identified
- Gaps by severity
- Domain confidence and complexity score

---

## Quality standards

- **No placeholder text** — every output grounded in the uploaded schema
- **Evidence cited** — tables and columns referenced for each finding
- **Enterprise grade** — readable by BA, Architect, PO, and QA audiences
- **Internally consistent** — same module and feature names across all artifacts

---

## Phased delivery

### Phase 1 (MVP)

Upload, parse, AI analysis, core deliverables, React UI, **Client PDF**, Markdown/HTML export.

### Phase 2

Full API spec, workflows, interactive ER diagram, DOCX/XLSX export.

### Phase 3

Version history, domain templates, optional authentication.

---

## Success criteria for Phase 1

1. User uploads a 30–50 table sample schema successfully
2. Analysis completes with all core deliverables on disk as JSON/text files
3. React UI displays dashboard and deliverable pages
4. **Client PDF downloads and prints cleanly for a stakeholder meeting**
5. No database used anywhere in the application

---

## Next steps

1. Confirm sample schema from client (or use provided healthcare/lab sample)
2. Approve Phase 1 scope and PDF report outline
3. Provision OpenAI API access and deployment environment
4. Review MVP demo and first Client PDF together
