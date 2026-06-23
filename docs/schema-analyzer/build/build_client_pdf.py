"""Build the client-facing SchemaDoc AI requirements PDF.

Produces:
    docs/schema-analyzer/SchemaDoc-AI-Client-Requirements.pdf
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "SchemaDoc-AI-Client-Requirements.pdf")

NAVY = colors.HexColor("#1B3A4B")
TEAL = colors.HexColor("#2A7B8C")
AMBER = colors.HexColor("#C48A1A")
GREY = colors.HexColor("#5B6470")
LIGHT = colors.HexColor("#EEF4F7")
DARK = colors.HexColor("#222222")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 0.85 * inch


def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=30, leading=36, textColor=NAVY, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontName="Helvetica",
            fontSize=15, leading=20, textColor=TEAL, alignment=TA_CENTER, spaceAfter=12,
        ),
        "cover_tag": ParagraphStyle(
            "cover_tag", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=11, leading=16, textColor=GREY, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=14, textColor=DARK, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=17, leading=22, textColor=NAVY, spaceBefore=8, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12.5, leading=17, textColor=TEAL, spaceBefore=10, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=DARK, leftIndent=14, spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=GREY, alignment=TA_CENTER, spaceAfter=10,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, leading=14, textColor=NAVY, alignment=TA_CENTER,
            spaceBefore=6, spaceAfter=8,
        ),
    }


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE_H - 0.55 * inch, PAGE_W - MARGIN, PAGE_H - 0.55 * inch)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.42 * inch, "SchemaDoc AI")
    canvas.drawCentredString(
        PAGE_W / 2, 0.45 * inch,
        f"Page {doc.page}  ·  Client Requirements Brief  ·  June 2026",
    )
    canvas.restoreState()


def hr():
    t = Table([[""]], colWidths=[5.5 * inch], rowHeights=[2])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    t.hAlign = "CENTER"
    return t


def bullet(st, text):
    return Paragraph(f"•&nbsp;&nbsp;{text}", st["bullet"])


def simple_table(headers, rows, col_widths):
    cell = lambda t: Paragraph(t, ParagraphStyle(
        "tc", fontName="Helvetica", fontSize=9.5, leading=13, textColor=DARK,
    ))
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=WHITE,
    )) for h in headers]]
    for row in rows:
        data.append([cell(c) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C5CED8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    t.hAlign = "CENTER"
    return t


def cover(st):
    return [
        Spacer(1, 1.3 * inch),
        Paragraph("SCHEMADOC AI", st["cover_title"]),
        Paragraph("AI-Powered Database Schema Analyzer", st["cover_sub"]),
        Spacer(1, 0.1 * inch),
        Paragraph(
            "Upload a database schema. Generate enterprise documentation.<br/>"
            "Share a printable PDF with stakeholders.",
            st["cover_tag"],
        ),
        Spacer(1, 0.3 * inch),
        hr(),
        Spacer(1, 0.15 * inch),
        Paragraph("Client Requirements &amp; Solution Brief", st["cover_sub"]),
        hr(),
        Spacer(1, 0.45 * inch),
        Paragraph(
            "<b>Prepared for:</b> Client Review &amp; Discussion<br/>"
            "<b>Version:</b> 1.0 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> June 2026<br/>"
            "<b>Classification:</b> Confidential",
            st["cover_meta"],
        ),
        PageBreak(),
    ]


def build_story(st):
    story = cover(st)

    story.append(Paragraph("1.  Executive summary", st["h1"]))
    story.append(Paragraph(
        "<b>SchemaDoc AI</b> is a web application that ingests a database schema file "
        "and automatically produces comprehensive software documentation, business analysis "
        "artifacts, and system design outputs. The application combines the perspectives of "
        "a Business Analyst, Solution Architect, Product Owner, QA Lead, and Technical Architect.",
        st["body"],
    ))
    story.append(Paragraph(
        "Per client requirements, the solution uses a <b>Python</b> API backend, a "
        "<b>React</b> web UI, <b>no application database</b>, and stores all data as "
        "<b>text and JSON files</b> on the filesystem. The primary deliverable for "
        "client meetings is a <b>printable PDF report</b> generated from the analysis.",
        st["body"],
    ))

    story.append(Paragraph("2.  Agreed client constraints", st["h1"]))
    story.append(simple_table(
        ["Requirement", "Our approach"],
        [
            ["No application database", "Zero DB — no PostgreSQL, SQL Server, or SQLite for app data"],
            ["File-based storage", "Projects, schemas, and deliverables saved as JSON/Markdown/text files"],
            ["Python backend", "FastAPI for parsing, AI orchestration, and PDF generation"],
            ["React UI", "Modern responsive interface for upload, review, and export"],
            ["Client PDF", "One-click printable report for stakeholder discussions"],
        ],
        [2.4 * inch, 3.9 * inch],
    ))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("3.  How it works", st["h1"]))
    for step, text in [
        ("Upload", "User uploads SQL DDL, schema JSON, or supported ERD export. System validates and parses tables, columns, keys, constraints, indexes, views, and routines."),
        ("Analyze", "AI classifies structure, detects business domain, clusters modules, and generates deliverables grounded in schema evidence."),
        ("Review", "User browses results in the React dashboard — features, FRD, user stories, screens, APIs, gaps, and more."),
        ("Share", "User downloads a <b>Client Discussion PDF</b> formatted for A4 printing — ready for executive and technical review meetings."),
    ]:
        story.append(Paragraph(f"<b>{step}.</b> {text}", st["body"]))

    story.append(PageBreak())
    story.append(Paragraph("4.  Generated deliverables", st["h1"]))
    story.append(Paragraph(
        "All outputs are derived from the uploaded schema. No placeholder text. "
        "Each item cites related tables and schema evidence.",
        st["body"],
    ))
    deliverables = [
        ("1", "Feature Inventory", "Features, tables, complexity, business value"),
        ("2", "FRD", "Functional modules with inputs, rules, outputs, validation"),
        ("3", "User Stories", "Agile format with acceptance criteria and story points"),
        ("4", "UI Screen List", "Screens, controls, grid columns, actions"),
        ("5", "Menu Structure", "Hierarchical navigation tree"),
        ("6", "Role Permission Matrix", "CRUD, Export, Approve by role and screen"),
        ("7", "Business Workflows", "Mermaid process flowcharts"),
        ("8", "ER Diagram", "Entity relationships with cardinality"),
        ("9", "API Requirements", "REST endpoints + OpenAPI specification"),
        ("10", "Test Cases", "Functional, integration, security, performance"),
        ("11", "PRD", "Vision, personas, goals, risks, success metrics"),
        ("12", "Gap Analysis", "Missing audit, security, indexes, archival patterns"),
    ]
    story.append(simple_table(
        ["#", "Artifact", "Contents"],
        deliverables,
        [0.35 * inch, 1.65 * inch, 4.3 * inch],
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Additional AI outputs:", st["h2"]))
    for item in [
        "Domain summary with confidence score",
        "Project complexity score and effort estimates",
        "Architecture recommendations (monolith vs microservices, auth, caching)",
        "Security review (PII exposure, audit gaps, authorization model)",
    ]:
        story.append(bullet(st, item))

    story.append(Paragraph("5.  Client PDF report (primary shareable artifact)", st["h1"]))
    story.append(Paragraph(
        "The PDF is designed for meetings where stakeholders may not have access to the "
        "web application. It is professionally formatted for A4 printing with cover page, "
        "table of contents, and page numbers.",
        st["body"],
    ))
    story.append(Paragraph("PDF contents:", st["h2"]))
    for item in [
        "Executive summary — domain, complexity, top findings",
        "Schema overview — table count, relationships, ER diagram",
        "Feature inventory and gap analysis (severity-rated)",
        "Sample user stories, UI screens, and API overview",
        "Architecture and security recommendations",
        "Appendix — full table list and methodology notes",
    ]:
        story.append(bullet(st, item))

    story.append(PageBreak())
    story.append(Paragraph("6.  Technology stack", st["h1"]))
    story.append(simple_table(
        ["Layer", "Technology"],
        [
            ["Frontend", "React, TypeScript, Tailwind CSS"],
            ["Backend", "Python 3.11+, FastAPI, Pydantic"],
            ["AI", "OpenAI API with structured JSON output"],
            ["Storage", "Filesystem — JSON, Markdown, text files only"],
            ["PDF export", "Python-generated printable report"],
            ["Deployment", "Docker Compose with shared data volume (optional)"],
        ],
        [1.8 * inch, 4.5 * inch],
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "<b>Explicitly excluded in v1:</b> application database, complex multi-tenant auth, "
        "live database connectors.",
        st["body"],
    ))

    story.append(Paragraph("7.  Dashboard metrics", st["h1"]))
    for item in [
        "Tables and relationships count",
        "Features, screens, APIs, and user stories identified",
        "Gaps identified by severity (Critical / High / Medium / Low)",
        "Business domain detected with confidence percentage",
        "Overall complexity score",
    ]:
        story.append(bullet(st, item))

    story.append(Paragraph("8.  Quality standards", st["h1"]))
    for item in [
        "<b>Schema-grounded</b> — every output justified by table/column/FK evidence",
        "<b>No placeholders</b> — enterprise-grade BA, Architect, PO, and QA quality",
        "<b>Consistent</b> — same module and feature names across all artifacts",
        "<b>Traceable</b> — deliverables stored as readable JSON/text files on disk",
    ]:
        story.append(bullet(st, item))

    story.append(Paragraph("9.  Phased delivery", st["h1"]))
    story.append(Paragraph("<b>Phase 1 — MVP</b>", st["h2"]))
    for item in [
        "Schema upload and parsing (PostgreSQL + SQL Server minimum)",
        "AI analysis and core deliverables (features, FRD, stories, screens, gaps, ER)",
        "React UI with dashboard and deliverable pages",
        "Client PDF, Markdown, and HTML export",
    ]:
        story.append(bullet(st, item))
    story.append(Paragraph("<b>Phase 2</b>", st["h2"]))
    story.append(bullet(st, "Full API spec, workflows, interactive ER diagram, DOCX/XLSX export"))
    story.append(Paragraph("<b>Phase 3</b>", st["h2"]))
    story.append(bullet(st, "Analysis versioning, domain templates, optional authentication"))

    story.append(Paragraph("10.  Phase 1 success criteria", st["h1"]))
    for i, item in enumerate([
        "Client provides or approves a sample schema (30–50 tables)",
        "Upload and parse complete with clear error reporting on failure",
        "AI analysis produces all Phase 1 deliverables as files on disk",
        "React UI displays dashboard metrics and deliverable content",
        "<b>Client PDF downloads and prints cleanly for stakeholder review</b>",
        "Confirmed: no database used anywhere in the application",
    ], start=1):
        story.append(Paragraph(f"{i}.&nbsp;&nbsp;{item}", st["bullet"]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "<i>Upload once. Document everything. Share a PDF your stakeholders can discuss tomorrow.</i>",
        st["callout"],
    ))

    story.append(Paragraph("11.  Recommended next steps", st["h1"]))
    for i, item in enumerate([
        "Confirm sample schema (or use provided healthcare/laboratory sample)",
        "Approve Phase 1 scope and Client PDF outline",
        "Provision OpenAI API access and deployment environment (Docker or VM)",
        "Schedule MVP demo and first Client PDF review meeting",
    ], start=1):
        story.append(Paragraph(f"{i}.&nbsp;&nbsp;{item}", st["bullet"]))

    return story


def main():
    st = build_styles()
    doc = BaseDocTemplate(
        OUT, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=0.75 * inch, bottomMargin=0.65 * inch,
        title="SchemaDoc AI — Client Requirements Brief",
    )
    frame = Frame(MARGIN, 0.65 * inch, PAGE_W - 2 * MARGIN, PAGE_H - 1.35 * inch, id="normal")
    doc.addPageTemplates([PageTemplate(id="All", frames=[frame], onPage=on_page)])
    doc.build(build_story(st))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
