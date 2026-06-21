"""Build Confluence2.0 Development Handoff Summary PDF.

Usage:
    pip install reportlab
    python docs/build_handoff_pdf.py
"""
from __future__ import annotations

import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Confluence2.0-Development-Handoff-Summary.pdf")

NAVY = colors.HexColor("#0c2340")
BLUE = colors.HexColor("#1e4d8c")
TEAL = colors.HexColor("#0d9488")
GREY = colors.HexColor("#5b6470")
DARK = colors.HexColor("#222222")
LIGHT_BG = colors.HexColor("#e8f4f8")

PAGE_W, PAGE_H = A4
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=20,
            textColor=BLUE,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=GREY,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=DARK,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=3,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            textColor=DARK,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=GREY,
            spaceAfter=4,
        ),
    }


def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, PAGE_H - 0.5 * inch, PAGE_W - MARGIN, PAGE_H - 0.5 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN, PAGE_H - 0.38 * inch, "Confluence2.0 — Development Handoff Summary")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.38 * inch, f"Page {doc.page}")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W / 2, 0.42 * inch, f"Version 2.0.0 · {date.today().isoformat()}")
    canvas.restoreState()


def p(text: str, style: str, styles: dict) -> Paragraph:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return Paragraph(escaped, styles[style])


def bullets(items: list[str], styles: dict) -> list:
    return [p(f"• {item}", "bullet", styles) for item in items]


def table(data: list[list[str]], col_widths: list[float]) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def build_story(styles: dict) -> list:
    story: list = []
    today = date.today().strftime("%B %d, %Y")

    story.append(Spacer(1, 1.6 * inch))
    story.append(p("Confluence2.0", "cover_title", styles))
    story.append(p("Development Handoff Summary", "cover_sub", styles))
    story.append(Spacer(1, 0.2 * inch))
    story.append(p("Unified Knowledge Platform with RAG Search", "cover_meta", styles))
    story.append(Spacer(1, 0.15 * inch))
    story.append(p(f"Document date: {today}", "cover_meta", styles))
    story.append(p("Application version: 2.0.0", "cover_meta", styles))
    story.append(p("Repository: CJ-Covance/AIProjects", "cover_meta", styles))
    story.append(PageBreak())

    # 1 Executive Summary
    story.append(p("1. Executive Summary", "h1", styles))
    story.append(
        p(
            "Confluence2.0 is an enterprise knowledge platform that lets users ask natural-language "
            "questions and receive consolidated, cited answers from an organizational knowledge base. "
            "Content is organized in a four-level hierarchy (Source → Domain → Project → Web Pages), "
            "stored on disk and in SQLite, and searched using Retrieval-Augmented Generation (RAG).",
            "body",
            styles,
        )
    )
    story.append(
        p(
            "The platform was built as a full-stack POC/demo: FastAPI backend, Next.js 14 frontend, "
            "OpenAI and Google Gemini integration with automatic provider fallback, folder-based file "
            "ingestion (PDF, HTML, MD, TXT), activity logging, and a management UI for CRUD operations.",
            "body",
            styles,
        )
    )

    # 2 Product Scope
    story.append(p("2. Product Scope & Features Delivered", "h1", styles))
    story.extend(
        bullets(
            [
                "Ask — Natural-language search with scope filters (source, domain, project) and inline citations.",
                "Browse — Hierarchical knowledge explorer with page counts.",
                "Manage — CRUD for sources, domains, projects, and web pages; sync/upload project files.",
                "Logs — Activity and error log viewer with filtering.",
                "RAG pipeline — Chunking, embedding, vector retrieval, and grounded answer generation.",
                "Folder sync — Auto-import files from knowledge_base/ during search or manual sync.",
                "Multi-provider AI — OpenAI and Google Gemini with LLM_PROVIDER=auto fallback on quota errors.",
                "Keyword fallback — Term-overlap retrieval when embeddings fail or scores are low.",
                "Demo branding — UI rebranded to Confluence2.0 with version footer (v2.0.0).",
            ],
            styles,
        )
    )

    # 3 Architecture
    story.append(p("3. System Architecture", "h1", styles))
    story.append(p("3.1 Knowledge Hierarchy", "h2", styles))
    story.append(
        p(
            "Source (root) → Domain → Project → Web Pages. Each level can map to a folder under "
            "backend/knowledge_base/. Files placed in source root folders (e.g. Cancer/cancer1.txt) "
            "are synced to the first project under that source.",
            "body",
            styles,
        )
    )
    story.append(p("3.2 RAG Pipeline", "h2", styles))
    story.extend(
        bullets(
            [
                "Sync — Import disk files into WebPage records (folder_sync service).",
                "Index — Split content into chunks; embed via OpenAI or Google; store in chunks table.",
                "Retrieve — Cosine similarity + keyword fallback; top-K chunks selected.",
                "Generate — LLM produces answer strictly from retrieved context with citations.",
            ],
            styles,
        )
    )
    story.append(p("3.3 Tech Stack", "h2", styles))
    story.append(
        table(
            [
                ["Layer", "Technology"],
                ["Frontend", "Next.js 14, React 18, TypeScript, Tailwind CSS"],
                ["Backend", "FastAPI, SQLAlchemy, Pydantic, Uvicorn"],
                ["Database", "SQLite (atlas.db) with embedding vectors stored as JSON"],
                ["AI — OpenAI", "text-embedding-3-small + gpt-4o-mini"],
                ["AI — Google", "gemini-embedding-001 + gemini-2.0-flash"],
                ["File parsing", "pypdf, native HTML/MD/TXT readers"],
            ],
            [1.4 * inch, CONTENT_W - 1.4 * inch],
        )
    )
    story.append(Spacer(1, 10))

    # 4 Repository Structure
    story.append(p("4. Repository Structure", "h1", styles))
    paths = [
        "backend/app/main.py — FastAPI entry point, health endpoints",
        "backend/app/models.py — SQLAlchemy models (Source, Domain, Project, WebPage, Chunk, ActivityLog)",
        "backend/app/routers/ — REST API route handlers",
        "backend/app/services/rag.py — Search and answer generation",
        "backend/app/services/llm_provider.py — OpenAI/Google switching and connectivity tests",
        "backend/app/services/folder_sync.py — Disk-to-database file import",
        "backend/app/services/indexer.py — Chunking and embedding pipeline",
        "backend/knowledge_base/ — On-disk knowledge files (gitignored)",
        "backend/.env — API keys and configuration (not in git)",
        "frontend/src/app/ — Next.js pages: /, /browse, /manage, /logs",
        "frontend/src/lib/api.ts — Backend API client",
        "docs/ — Documentation and this handoff PDF",
    ]
    for line in paths:
        story.append(p(line, "mono", styles))

    story.append(PageBreak())

    # 5 Setup
    story.append(p("5. Local Development Setup", "h1", styles))
    story.append(p("5.1 Prerequisites", "h2", styles))
    story.extend(
        bullets(
            [
                "Python 3.9+ (tested on 3.9.5 Windows and 3.12 Linux)",
                "Node.js 20+",
                "OpenAI API key and/or Google Gemini API key",
            ],
            styles,
        )
    )
    story.append(p("5.2 Backend", "h2", styles))
    for cmd in [
        "cd backend",
        "python -m venv .venv",
        ".venv\\Scripts\\activate   (Windows)",
        "python -m pip install -r requirements.txt",
        "copy .env.example .env",
        "python seed_data.py",
        "python -m uvicorn app.main:app --reload --port 8000",
    ]:
        story.append(p(cmd, "mono", styles))
    story.append(p("5.3 Frontend", "h2", styles))
    for cmd in ["cd frontend", "npm install", "npm run dev"]:
        story.append(p(cmd, "mono", styles))
    story.append(
        p("Open http://localhost:3000 (frontend). Backend API: http://localhost:8000", "body", styles)
    )

    # 6 Configuration
    story.append(p("6. Environment Configuration", "h1", styles))
    story.append(
        p(
            "All backend configuration lives in backend/.env. Cursor IDE API keys are NOT used — "
            "the application calls OpenAI and Google APIs directly.",
            "body",
            styles,
        )
    )
    story.append(
        table(
            [
                ["Variable", "Default", "Description"],
                ["LLM_PROVIDER", "auto", "openai | google | auto (fallback on quota errors)"],
                ["OPENAI_API_KEY", "—", "OpenAI API key"],
                ["GOOGLE_API_KEY", "—", "Google Gemini key (GEMINI_API_KEY alias accepted)"],
                ["GOOGLE_EMBEDDING_MODEL", "gemini-embedding-001", "Do not use retired text-embedding-004"],
                ["GOOGLE_CHAT_MODEL", "gemini-2.0-flash", "Gemini chat model"],
                ["KNOWLEDGE_BASE_ROOT", "knowledge_base", "Root folder for on-disk files"],
                ["OPENAI_SSL_VERIFY", "true", "Set false only for dev SSL issues on Windows"],
            ],
            [1.5 * inch, 1.1 * inch, CONTENT_W - 2.6 * inch],
        )
    )
    story.append(Spacer(1, 8))
    story.append(p("6.1 Verify AI Connectivity", "h2", styles))
    story.extend(
        bullets(
            [
                "GET http://localhost:8000/api/health — shows key status and env file path",
                "GET http://localhost:8000/api/health/test-llm — runs live embed + chat tests",
                "If OpenAI quota is exhausted, set LLM_PROVIDER=google and use a valid GOOGLE_API_KEY",
            ],
            styles,
        )
    )

    # 7 API
    story.append(p("7. Key API Endpoints", "h1", styles))
    story.append(
        table(
            [
                ["Method", "Endpoint", "Description"],
                ["GET", "/api/health", "Health check and provider status"],
                ["GET", "/api/health/test-llm", "Test OpenAI/Google connectivity"],
                ["POST", "/api/search", "RAG question answering"],
                ["POST", "/api/reindex", "Re-index pages in scope"],
                ["GET", "/api/hierarchy", "Full knowledge tree"],
                ["GET/POST/PUT/DELETE", "/api/sources, /domains, /projects, /pages", "CRUD operations"],
                ["POST", "/api/projects/{id}/sync-folder", "Import files from disk"],
                ["POST", "/api/projects/{id}/upload", "Upload file to project folder"],
                ["GET", "/api/logs", "Activity and error logs"],
            ],
            [0.7 * inch, 2.2 * inch, CONTENT_W - 2.9 * inch],
        )
    )

    story.append(PageBreak())

    # 8 Demo Workflow
    story.append(p("8. Demo Workflow", "h1", styles))
    story.extend(
        bullets(
            [
                "Manage: Create Source (e.g. Cancer) → Domain → Project.",
                "Place files in backend/knowledge_base/{Source}/ or project subfolders.",
                "Use Sync folder or Upload file on Manage, or simply Ask a question (auto-sync).",
                "Ask: Select scope filter, enter question (e.g. Benign vs Malignant Tumors), click Ask.",
                "Review answer, citations, and search diagnostics (pages/chunks indexed).",
                "Logs: Check indexing or API errors if search returns no results.",
            ],
            styles,
        )
    )

    # 9 Known Issues
    story.append(p("9. Known Issues & Troubleshooting", "h1", styles))
    story.append(
        table(
            [
                ["Issue", "Cause", "Resolution"],
                [
                    "OpenAI 429 quota error",
                    "Billing/quota exhausted",
                    "Set LLM_PROVIDER=google; add GOOGLE_API_KEY; restart backend",
                ],
                [
                    "Google 404 embedding model",
                    "text-embedding-004 retired",
                    "Use GOOGLE_EMBEDDING_MODEL=gemini-embedding-001",
                ],
                [
                    "pip install fails on Python 3.9",
                    "google-genai 1.47+ needs Python 3.10",
                    "Use pinned google-genai==1.46.0 in requirements.txt",
                ],
                [
                    "Page saved but indexing failed",
                    "AI key missing or provider error",
                    "Check /api/health/test-llm; fix .env; re-save page",
                ],
                [
                    "No search results",
                    "Missing chunks or wrong scope",
                    "Ensure Domain+Project exist; run POST /api/reindex",
                ],
                [
                    "SSL certificate error (Windows)",
                    "Corporate proxy/certs",
                    "pip install certifi; or OPENAI_SSL_VERIFY=false (dev only)",
                ],
                [
                    "Logs page 404",
                    "Wrong URL",
                    "Use http://localhost:3000/logs (not port 8000)",
                ],
            ],
            [1.3 * inch, 1.8 * inch, CONTENT_W - 3.1 * inch],
        )
    )

    # 10 Handoff Checklist
    story.append(Spacer(1, 12))
    story.append(p("10. Handoff Checklist", "h1", styles))
    story.extend(
        bullets(
            [
                "Clone repository and checkout branch cursor/atlas-knowledge-platform-86a3 (or main after merge).",
                "Create backend/.env from .env.example with valid GOOGLE_API_KEY or OPENAI_API_KEY.",
                "Run pip install -r requirements.txt and npm install in frontend.",
                "Start backend (port 8000) and frontend (port 3000).",
                "Verify GET /api/health/test-llm returns any_provider_working: true.",
                "Create knowledge hierarchy in Manage and add/sync content.",
                "Run demo search queries and confirm citations appear.",
                "Review PR #4 on GitHub for full change history.",
            ],
            styles,
        )
    )

    # 11 Future
    story.append(p("11. Recommended Future Enhancements", "h1", styles))
    story.extend(
        bullets(
            [
                "PostgreSQL + pgvector for production-scale vector search",
                "SSO / OIDC authentication and role-based access control",
                "Hybrid retrieval (BM25 + semantic) and re-ranking",
                "Connectors for Confluence, SharePoint, Jira",
                "Document versioning, audit trails, and approval workflows",
                "Docker/Kubernetes deployment with secrets management",
            ],
            styles,
        )
    )

    story.append(Spacer(1, 20))
    story.append(
        p(
            "This document summarizes the development state of Confluence2.0 as of the handoff date. "
            "For live API exploration, use the FastAPI docs at http://localhost:8000/docs when the "
            "backend is running.",
            "small",
            styles,
        )
    )

    return story


def main():
    styles = build_styles()
    frame = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2 * MARGIN, id="normal")
    doc = BaseDocTemplate(
        OUT,
        pagesize=A4,
        title="Confluence2.0 Development Handoff Summary",
        author="Development Team",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    doc.build(build_story(styles))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
