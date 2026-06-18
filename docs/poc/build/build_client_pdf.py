"""Build the client-facing Atlas user-journey POC PDF.

Run after render_ui_mockups.py. Produces:
    docs/poc/Atlas-Unified-Knowledge-Platform-Client-POC.pdf
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "..", "assets", "ui")
OUT = os.path.join(HERE, "..", "Atlas-Unified-Knowledge-Platform-Client-POC.pdf")

NAVY = colors.HexColor("#1F3A5F")
BLUE = colors.HexColor("#2E5E8C")
GOLD = colors.HexColor("#B78A2E")
GREY = colors.HexColor("#5B6470")
LIGHT = colors.HexColor("#EAF1F8")
DARK = colors.HexColor("#222222")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 0.85 * inch


def img(name, width=6.3 * inch):
    path = os.path.join(ASSETS, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing asset: {path}")
    im = Image(path, width=width, height=width * 0.62)
    im.hAlign = "CENTER"
    return im


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=32, leading=38, textColor=NAVY, alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontName="Helvetica",
            fontSize=16, leading=22, textColor=BLUE, alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "cover_tag": ParagraphStyle(
            "cover_tag", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=11, leading=16, textColor=GREY, alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=14, textColor=DARK, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=24, textColor=NAVY, spaceBefore=10, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=18, textColor=BLUE, spaceBefore=12, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=DARK, alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, textColor=DARK, leftIndent=14,
            bulletIndent=0, spaceAfter=4,
        ),
        "step": ParagraphStyle(
            "step", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, textColor=GREY, alignment=TA_CENTER,
            spaceAfter=12, spaceBefore=2,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, leading=14, textColor=NAVY, alignment=TA_CENTER,
            spaceAfter=8, spaceBefore=4,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, textColor=GREY, alignment=TA_CENTER,
        ),
    }
    return styles


class NumberedCanvas:
    """Mixin applied via doc.build callback."""
    pass


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE_H - 0.55 * inch, PAGE_W - MARGIN, PAGE_H - 0.55 * inch)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.42 * inch,
                           "Atlas — Unified Knowledge Platform")
    canvas.drawCentredString(PAGE_W / 2, 0.45 * inch,
                             f"Page {doc.page}  ·  Confidential — Client POC Brief")
    canvas.restoreState()


def cover_block(st):
    story = [
        Spacer(1, 1.4 * inch),
        Paragraph("ATLAS", st["cover_title"]),
        Paragraph("Unified Knowledge Platform", st["cover_sub"]),
        Spacer(1, 0.15 * inch),
        Paragraph(
            "Ask once. Receive one clear, consolidated answer —<br/>"
            "summarized from every relevant page across your organization.",
            st["cover_tag"],
        ),
        Spacer(1, 0.35 * inch),
        _hr_table(),
        Spacer(1, 0.2 * inch),
        Paragraph("Proof of Concept — Client Overview", st["cover_sub"]),
        _hr_table(),
        Spacer(1, 0.5 * inch),
        Paragraph(
            "<b>Prepared for:</b> Client Executive Review<br/>"
            "<b>Prepared by:</b> CJ-Covance<br/>"
            "<b>Version:</b> 1.0 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> June 2026<br/>"
            "<b>Classification:</b> Confidential",
            st["cover_meta"],
        ),
        PageBreak(),
    ]
    return story


def _hr_table():
    t = Table([[""]], colWidths=[5.5 * inch], rowHeights=[2])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    t.hAlign = "CENTER"
    return t


def bullet(st, text):
    return Paragraph(f"•&nbsp;&nbsp;{text}", st["bullet"])


def figure(name, caption, st, width=6.3 * inch):
    return [
        img(name, width),
        Paragraph(caption, st["caption"]),
    ]


def step_section(num, title, body_lines, image_name, caption, st):
    items = [
        Paragraph(f"Step {num} — {title}", st["step"]),
    ]
    for line in body_lines:
        items.append(Paragraph(line, st["body"]))
    items.extend(figure(image_name, caption, st))
    return items


def build_story(st):
    story = cover_block(st)

    # 1. Introduction
    story.append(Paragraph("1.  Introduction", st["h1"]))
    story.append(Paragraph(
        "This document presents a proof of concept for <b>Atlas</b>, an enterprise "
        "knowledge platform designed for the way people actually work. Today, answering "
        "a single question often means opening many documents across wikis, file shares, "
        "and ticketing systems — and reading each one by hand. Atlas changes that "
        "experience: you ask a question once, and the platform returns a clear, "
        "consolidated answer drawn from every relevant page you are permitted to access.",
        st["body"],
    ))
    story.append(Paragraph(
        "The pages that follow walk through the website from a user's point of view — "
        "what you see on screen, what you do at each step, and how the platform saves "
        "time while keeping every answer traceable to its original source.",
        st["body"],
    ))

    # 2. The problem
    story.append(Paragraph("2.  The challenge today", st["h1"]))
    story.append(Paragraph(
        "Knowledge in large organizations is spread across many tools, teams, and "
        "projects. A question such as <i>\"What is our data-retention policy for clinical "
        "trial documents, and which projects already follow it?\"</i> may require "
        "reading a policy page in Confluence, a guideline in SharePoint, several project "
        "charters, and a compliance tracker in Jira — often taking hours, and still "
        "leaving doubt about which version is current.",
        st["body"],
    ))
    for item in [
        "Search tools return links, not answers — the reading and comparison is still manual.",
        "The same information may appear in different formats with different wording.",
        "New team members spend weeks learning where knowledge lives.",
        "Experts are repeatedly interrupted to answer questions that already exist in writing.",
    ]:
        story.append(bullet(st, item))

    story.extend(figure(
        "ui_06_before_after.png",
        "Figure 1.  Before Atlas, people read documents one by one. With Atlas, they ask once and receive a consolidated answer.",
        st, width=6.0 * inch,
    ))

    # 3. What Atlas offers
    story.append(PageBreak())
    story.append(Paragraph("3.  What Atlas offers", st["h1"]))
    story.append(Paragraph(
        "Atlas is a scalable, extensible platform that <b>centralizes knowledge across "
        "domains and projects</b>. It connects to your existing systems — wikis, document "
        "stores, file shares, and ticketing tools — and builds a unified knowledge layer "
        "behind a simple web experience. You do not need to know where a document lives; "
        "you simply ask your question in plain English.",
        st["body"],
    ))
    story.extend(figure(
        "ui_07_journey.png",
        "Figure 2.  The user journey in four steps: sign in, ask, review, and verify.",
        st, width=6.2 * inch,
    ))
    story.append(Paragraph("What makes Atlas different:", st["h2"]))
    for item in [
        "<b>One question, one answer</b> — Atlas searches all connected sources and synthesizes a single summary.",
        "<b>Every claim is cited</b> — You can open the original page behind any statement.",
        "<b>Your permissions are respected</b> — You only see content you are already allowed to read.",
        "<b>Built to grow</b> — New sources and business domains can be added without rebuilding the platform.",
    ]:
        story.append(bullet(st, item))

    # 4. Using the website
    story.append(PageBreak())
    story.append(Paragraph("4.  Using the Atlas website — step by step", st["h1"]))
    story.append(Paragraph(
        "The following sections show the main screens a user would encounter. Each "
        "illustration reflects the intended experience for the proof of concept.",
        st["body"],
    ))

    story.extend(step_section(
        1, "Open Atlas and sign in",
        [
            "You open Atlas in your web browser and sign in with your company account "
            "(single sign-on). No new password is required.",
            "The home page welcomes you with a search bar and a short summary of what "
            "Atlas can do. You can see which knowledge sources are connected and confirm "
            "that your existing access permissions apply.",
        ],
        "ui_01_home.png",
        "Figure 3.  The Atlas home page — a single search bar spans all connected knowledge sources.",
        st,
    ))

    story.extend(step_section(
        2, "Ask your question",
        [
            "Type your question in everyday language — the same way you would ask a "
            "colleague. You do not need to choose which system to search.",
            "Optional filters let you narrow the scope by domain, project, or time "
            "(for example, \"current policy only\"). When you press <b>Ask</b>, Atlas "
            "searches every connected source at once.",
        ],
        "ui_02_ask_question.png",
        "Figure 4.  The user enters a question in plain English and optionally applies filters.",
        st,
    ))

    story.append(PageBreak())
    story.extend(step_section(
        3, "Read the consolidated answer",
        [
            "Within seconds, Atlas presents a single, readable answer — not a list of "
            "links. The response combines information from every relevant page and "
            "presents it in clear, formal English.",
            "Numbered citations appear inline. A confidence indicator shows how well "
            "the available sources support the answer. If sources disagree or one "
            "project is behind on compliance, Atlas says so explicitly.",
        ],
        "ui_03_answer.png",
        "Figure 5.  One consolidated answer with inline citations — no need to open dozens of documents.",
        st,
    ))

    story.extend(step_section(
        4, "Verify sources and open originals",
        [
            "Click any citation number to open a panel showing the source documents "
            "Atlas used. Each entry includes the document title, where it lives "
            "(Confluence, SharePoint, Jira, and so on), when it was last updated, "
            "and the exact passage that supports the answer.",
            "You can open the original page in one click whenever you need full "
            "context or want to share a direct link with a colleague.",
        ],
        "ui_04_sources.png",
        "Figure 6.  Source citations let users verify every claim and open the original document.",
        st,
    ))

    story.append(PageBreak())
    story.extend(step_section(
        5, "Browse by domain or project (optional)",
        [
            "If you prefer to explore before asking, the Browse page lists the "
            "domains and projects Atlas knows about — along with how many pages "
            "are indexed in each area.",
            "Selecting a domain pre-fills your next question so answers stay focused "
            "on the area you care about.",
        ],
        "ui_05_browse.png",
        "Figure 7.  Users can browse knowledge by domain and project, or ask across the entire organization.",
        st,
    ))

    # 5. Before and after
    story.append(Paragraph("5.  What changes for you", st["h1"]))
    t = Table([
        [Paragraph("<b>Today</b>", st["body"]), Paragraph("<b>With Atlas</b>", st["body"])],
        [
            Paragraph("Search returns many links; you open and read each document.", st["body"]),
            Paragraph("You receive one consolidated answer with citations to expand.", st["body"]),
        ],
        [
            Paragraph("You reconcile conflicting documents manually.", st["body"]),
            Paragraph("Atlas highlights conflicts and shows which source is most recent.", st["body"]),
        ],
        [
            Paragraph("Knowledge is siloed by team and tool.", st["body"]),
            Paragraph("One question spans every domain and project you can access.", st["body"]),
        ],
        [
            Paragraph("Answers depend on who you ask.", st["body"]),
            Paragraph("Answers are consistent, grounded, and fully traceable.", st["body"]),
        ],
    ], colWidths=[3.15 * inch, 3.15 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C5CED8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    t.hAlign = "CENTER"
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    # 6. POC scope
    story.append(Paragraph("6.  What the proof of concept will demonstrate", st["h1"]))
    story.append(Paragraph(
        "The proof of concept is a time-boxed demonstration on a representative "
        "slice of your organization's knowledge. It is designed to prove the core "
        "user experience before a wider rollout.",
        st["body"],
    ))
    for item in [
        "A working web experience like the screens shown in this document.",
        "Connection to two or three representative sources (for example, a wiki, a file share, and a ticketing system).",
        "Cross-document answers with inline citations on real content from one or two priority domains.",
        "Permission-aware retrieval — users only see what they are entitled to read.",
        "A measured quality report and a plan for scaling to all sources and domains.",
    ]:
        story.append(bullet(st, item))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "<i>Ask once. Receive one clear, consolidated, trustworthy answer — "
        "across every domain and project.</i>",
        st["callout"],
    ))

    # 7. Next steps
    story.append(Paragraph("7.  Recommended next steps", st["h1"]))
    story.append(Paragraph(
        "To proceed with the proof of concept, we recommend the following:",
        st["body"],
    ))
    for i, item in enumerate([
        "Confirm two or three representative knowledge sources and one or two priority domains.",
        "Identify a small working group: a product owner, a subject-matter contact per domain, and an IT/security contact.",
        "Approve a time-boxed POC with access to a secure environment in your cloud or VPC.",
        "Review the working demonstration, quality report, and production rollout plan at the end of the POC.",
    ], start=1):
        story.append(Paragraph(f"{i}.&nbsp;&nbsp;{item}", st["bullet"]))

    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "Atlas turns fragmented documents into a single, trustworthy answer — "
        "so your teams spend less time searching and more time acting on what they learn.",
        st["body"],
    ))

    return story


def main():
    st = build_styles()
    doc = BaseDocTemplate(
        OUT, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=0.75 * inch, bottomMargin=0.65 * inch,
        title="Atlas — Unified Knowledge Platform — Client POC",
        author="CJ-Covance",
    )
    frame = Frame(MARGIN, 0.65 * inch, PAGE_W - 2 * MARGIN, PAGE_H - 1.35 * inch, id="normal")
    doc.addPageTemplates([PageTemplate(id="All", frames=[frame], onPage=on_page)])
    doc.build(build_story(st))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
