"""Render client-facing website UI mockups for the Atlas user-journey POC PDF.

Produces print-ready PNGs (200 DPI) into docs/poc/assets/ui/
"""
import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets", "ui")
os.makedirs(ASSETS, exist_ok=True)

NAVY = "#1F3A5F"
BLUE = "#2E5E8C"
LIGHT = "#EAF1F8"
LIGHT2 = "#DCE7F3"
ACCENT = "#C8A24B"
GREEN = "#E7F0E7"
GREEN_E = "#5B7A5B"
GREY = "#5B6470"
GREY_BG = "#F4F6F8"
WHITE = "#FFFFFF"
TEXT = "#222222"
CITE_BG = "#FFF8E8"
BORDER = "#C5CED8"

plt.rcParams["font.family"] = "DejaVu Sans"


def save(fig, name):
    out = os.path.join(ASSETS, name)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)
    print("wrote", os.path.normpath(out))


def browser_chrome(ax, title="Atlas — Unified Knowledge Platform"):
    """Draw a browser window frame."""
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.axis("off")
    frame = FancyBboxPatch((0.5, 0.5), 99, 61, boxstyle="round,pad=0,rounding_size=1.2",
                           linewidth=1.5, edgecolor=BORDER, facecolor=WHITE)
    ax.add_patch(frame)
    ax.add_patch(Rectangle((0.5, 55.5), 99, 6, facecolor=LIGHT2, edgecolor=BORDER, linewidth=1))
    for i, c in enumerate(["#E57373", "#FFD54F", "#81C784"]):
        ax.add_patch(plt.Circle((3 + i * 2.2, 58.5), 0.7, color=c))
    ax.add_patch(FancyBboxPatch((12, 57.2), 76, 2.6, boxstyle="round,pad=0,rounding_size=0.5",
                                facecolor=WHITE, edgecolor=BORDER, linewidth=0.8))
    ax.text(50, 58.5, "https://atlas.company.internal", ha="center", va="center",
            fontsize=7.5, color=GREY)
    ax.text(2, 53.5, title, fontsize=9, color=NAVY, fontweight="bold")


def nav_bar(ax, active="Home"):
    items = ["Home", "Ask Atlas", "Browse", "My History", "Help"]
    x = 3
    for item in items:
        bold = item == active
        ax.text(x, 51.5, item, fontsize=7.5, color=NAVY if bold else GREY,
                fontweight="bold" if bold else "normal")
        if bold:
            ax.plot([x - 0.5, x + len(item) * 0.55], [50.8, 50.8], color=ACCENT, linewidth=2)
        x += 11


def search_box(ax, y, text, placeholder=False):
    ax.add_patch(FancyBboxPatch((8, y), 84, 6.5, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=WHITE, edgecolor=BLUE, linewidth=1.8))
    ax.text(10, y + 3.2, text, fontsize=8.5, color=GREY if placeholder else TEXT,
            style="italic" if placeholder else "normal")
    ax.add_patch(FancyBboxPatch((87.5, y + 0.8), 3.8, 4.8, boxstyle="round,pad=0,rounding_size=0.6",
                                facecolor=BLUE, edgecolor=BLUE))
    ax.text(89.4, y + 3.2, "Ask", ha="center", va="center", fontsize=7.5, color=WHITE,
            fontweight="bold")


def citation_chip(ax, x, y, num, w=3.2):
    ax.add_patch(FancyBboxPatch((x, y), w, 2.2, boxstyle="round,pad=0,rounding_size=0.4",
                                facecolor=CITE_BG, edgecolor=ACCENT, linewidth=0.8))
    ax.text(x + w / 2, y + 1.1, str(num), ha="center", va="center", fontsize=6.5,
            color=NAVY, fontweight="bold")


def wrapped_text(ax, x, y, w, text, fs=8, color=TEXT, line_h=2.8, bold_prefix=None):
    lines = textwrap.wrap(text, width=int(w * 1.15))
    cy = y
    for i, line in enumerate(lines):
        if i == 0 and bold_prefix:
            ax.text(x, cy, bold_prefix, fontsize=fs, color=color, fontweight="bold")
            ax.text(x + len(bold_prefix) * 0.42, cy, line, fontsize=fs, color=color)
        else:
            ax.text(x, cy, line, fontsize=fs, color=color)
        cy -= line_h
    return cy


# ---------------------------------------------------------------------------
# Screen 1 — Home / landing
# ---------------------------------------------------------------------------
def ui_home():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    browser_chrome(ax)
    nav_bar(ax, "Home")

    ax.text(50, 46, "Ask once. Get one clear answer.", ha="center", fontsize=14,
            color=NAVY, fontweight="bold")
    ax.text(50, 42.5, "Atlas searches every wiki, document, and ticket you can access — "
            "and returns a single, consolidated summary with sources.",
            ha="center", fontsize=8.5, color=GREY, wrap=True)

    search_box(ax, 35, "Ask a question across all your knowledge sources…", placeholder=True)

    ax.text(50, 31, "Popular starting points", ha="center", fontsize=8, color=GREY)
    chips = ["Data retention policy", "Project onboarding checklist",
             "Clinical trial SOPs", "Security & compliance"]
    cx = 14
    for chip in chips:
        w = len(chip) * 0.55 + 2
        ax.add_patch(FancyBboxPatch((cx, 27), w, 3.2, boxstyle="round,pad=0,rounding_size=0.8",
                                    facecolor=LIGHT, edgecolor=BLUE, linewidth=0.8))
        ax.text(cx + w / 2, 28.6, chip, ha="center", va="center", fontsize=7, color=BLUE)
        cx += w + 1.5

    ax.add_patch(FancyBboxPatch((8, 8), 40, 16, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=GREY_BG, edgecolor=BORDER, linewidth=0.8))
    ax.text(10, 21, "Connected sources", fontsize=8, color=NAVY, fontweight="bold")
    for i, src in enumerate(["Confluence · 12 spaces", "SharePoint · 8 sites",
                              "File shares · 3 drives", "Jira · 4 projects"]):
        ax.text(10, 18.5 - i * 2.8, f"•  {src}", fontsize=7.2, color=TEXT)

    ax.add_patch(FancyBboxPatch((52, 8), 40, 16, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=GREEN, edgecolor=GREEN_E, linewidth=0.8, alpha=0.35))
    ax.text(54, 21, "Your access is respected", fontsize=8, color=GREEN_E, fontweight="bold")
    ax.text(54, 17.5, "Atlas only uses documents you are already\n"
            "permitted to read. Restricted content never\n"
            "appears in your answers.", fontsize=7.2, color=TEXT)

    save(fig, "ui_01_home.png")


# ---------------------------------------------------------------------------
# Screen 2 — User typing a question
# ---------------------------------------------------------------------------
def ui_ask_question():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    browser_chrome(ax)
    nav_bar(ax, "Ask Atlas")

    ax.text(8, 46, "Step 1 — Ask your question in plain English", fontsize=10,
            color=NAVY, fontweight="bold")

    question = ("What is our current data-retention policy for clinical trial "
                "documents, and which projects already implement it?")
    search_box(ax, 38, question)

    ax.text(8, 33, "Optional filters", fontsize=8, color=GREY)
    filters = [("Domain", "Clinical Operations"), ("Project", "All projects"),
               ("Time", "Current only")]
    fx = 8
    for label, val in filters:
        ax.add_patch(FancyBboxPatch((fx, 28.5), 22, 3.5, boxstyle="round,pad=0,rounding_size=0.6",
                                    facecolor=WHITE, edgecolor=BORDER))
        ax.text(fx + 1, 31.2, f"{label}: ", fontsize=7, color=GREY)
        ax.text(fx + 1 + len(label) * 0.45, 31.2, val, fontsize=7, color=NAVY, fontweight="bold")
        fx += 24

    ax.add_patch(FancyBboxPatch((8, 8), 84, 17, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=LIGHT, edgecolor=BLUE, linewidth=0.8, alpha=0.5))
    ax.text(10, 22, "What happens next?", fontsize=8.5, color=NAVY, fontweight="bold")
    steps = [
        "Atlas searches across Confluence, SharePoint, file shares, and Jira simultaneously.",
        "It reads and compares the most relevant pages — you do not need to open them yourself.",
        "Within seconds, you receive one consolidated answer with links to every source used.",
    ]
    for i, s in enumerate(steps):
        ax.text(10, 18.5 - i * 3.2, f"{i + 1}.  {s}", fontsize=7.5, color=TEXT)

    save(fig, "ui_02_ask_question.png")


# ---------------------------------------------------------------------------
# Screen 3 — Consolidated answer
# ---------------------------------------------------------------------------
def ui_answer():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    browser_chrome(ax)
    nav_bar(ax, "Ask Atlas")

    ax.text(8, 46, "Step 2 — Read one consolidated answer", fontsize=10,
            color=NAVY, fontweight="bold")

    ax.add_patch(FancyBboxPatch((8, 10), 84, 33, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=WHITE, edgecolor=BLUE, linewidth=1.2))
    ax.text(10, 40, "Answer", fontsize=9, color=NAVY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((78, 39), 12, 2.8, boxstyle="round,pad=0,rounding_size=0.5",
                                facecolor=GREEN, edgecolor=GREEN_E, alpha=0.4))
    ax.text(84, 40.4, "High confidence", ha="center", fontsize=6.5, color=GREEN_E, fontweight="bold")

    answer = (
        "Clinical trial documents must be retained for a minimum of 15 years after "
        "study completion, per the Global Data Retention Policy (2024 revision). "
        "Electronic records require encrypted storage with audit trails. "
        "Projects ALPHA-204, BETA-117, and GAMMA-09 have documented compliance in their "
        "project charters; DELTA-33 is flagged as pending implementation review."
    )
    wrapped_text(ax, 10, 36, 78, answer, fs=8, line_h=2.6)

    for i, n in enumerate([1, 2, 3, 4]):
        citation_chip(ax, 10 + i * 3.8, 14.5, n)

    ax.text(10, 12.5, "Sources cited inline — click any number to view the original page.",
            fontsize=7, color=GREY, style="italic")

    ax.add_patch(FancyBboxPatch((8, 4), 40, 4.5, boxstyle="round,pad=0,rounding_size=0.6",
                                facecolor=LIGHT2, edgecolor=BORDER))
    ax.text(10, 6.2, "Was this answer helpful?   Yes   ·   No   ·   Add comment",
            fontsize=7.2, color=GREY)

    save(fig, "ui_03_answer.png")


# ---------------------------------------------------------------------------
# Screen 4 — Source citations panel
# ---------------------------------------------------------------------------
def ui_sources():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    browser_chrome(ax)
    nav_bar(ax, "Ask Atlas")

    ax.text(8, 46, "Step 3 — Verify sources with one click", fontsize=10,
            color=NAVY, fontweight="bold")

    # Left: condensed answer
    ax.add_patch(FancyBboxPatch((8, 18), 38, 25, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=LIGHT, edgecolor=BORDER, linewidth=0.8))
    ax.text(10, 40, "Answer (summary)", fontsize=8, color=NAVY, fontweight="bold")
    wrapped_text(ax, 10, 36, 34,
                 "…15 years after study completion… Projects ALPHA-204, BETA-117…",
                 fs=7.2, line_h=2.4)
    citation_chip(ax, 10, 20, 1)
    citation_chip(ax, 14, 20, 2, w=3.2)
    ax.add_patch(FancyBboxPatch((13.5, 19.5), 4.5, 3.2, boxstyle="round,pad=0,rounding_size=0.4",
                                facecolor=ACCENT, edgecolor=ACCENT, alpha=0.25, linewidth=1.5))

    # Right: sources panel
    ax.add_patch(FancyBboxPatch((50, 8), 42, 35, boxstyle="round,pad=0,rounding_size=1",
                                facecolor=WHITE, edgecolor=ACCENT, linewidth=1.5))
    ax.text(52, 40.5, "Sources (4 documents)", fontsize=8.5, color=NAVY, fontweight="bold")

    sources = [
        ("[1] Global Data Retention Policy (2024)", "Confluence · Updated Mar 2024",
         "…minimum retention period of 15 years for all clinical trial records…"),
        ("[2] Clinical Ops — Retention Guidelines", "SharePoint · Updated Jan 2025",
         "…encrypted storage and audit trail requirements for electronic records…"),
        ("[3] Project ALPHA-204 Charter", "Confluence · Updated Feb 2025",
         "…retention policy implemented and verified by QA…"),
        ("[4] Project Compliance Tracker", "Jira · Updated yesterday",
         "…DELTA-33: implementation review pending…"),
    ]
    sy = 37
    for title, meta, snippet in sources:
        ax.text(52, sy, title, fontsize=7.5, color=BLUE, fontweight="bold")
        ax.text(52, sy - 2.2, meta, fontsize=6.5, color=GREY)
        ax.add_patch(FancyBboxPatch((52, sy - 6.5), 38, 3.5, boxstyle="round,pad=0,rounding_size=0.4",
                                    facecolor=CITE_BG, edgecolor=BORDER, linewidth=0.5))
        ax.text(53, sy - 4.8, snippet, fontsize=6.5, color=TEXT, style="italic")
        ax.text(52, sy - 8, "Open original →", fontsize=6.5, color=BLUE)
        sy -= 10.5

    save(fig, "ui_04_sources.png")


# ---------------------------------------------------------------------------
# Screen 5 — Browse by domain
# ---------------------------------------------------------------------------
def ui_browse():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    browser_chrome(ax)
    nav_bar(ax, "Browse")

    ax.text(8, 46, "Browse knowledge by domain and project", fontsize=10,
            color=NAVY, fontweight="bold")
    ax.text(8, 43, "Explore what Atlas knows — or narrow your next question to a specific area.",
            fontsize=8, color=GREY)

    domains = [
        ("Clinical Operations", "842 pages", "12 projects"),
        ("Regulatory Affairs", "516 pages", "8 projects"),
        ("Quality Assurance", "391 pages", "6 projects"),
        ("IT & Security", "278 pages", "4 projects"),
    ]
    positions = [(8, 28), (52, 28), (8, 12), (52, 12)]
    for (name, pages, projects), (x, y) in zip(domains, positions):
        ax.add_patch(FancyBboxPatch((x, y), 40, 13, boxstyle="round,pad=0,rounding_size=1",
                                    facecolor=WHITE, edgecolor=BLUE, linewidth=1))
        ax.text(x + 2, y + 10.5, name, fontsize=9, color=NAVY, fontweight="bold")
        ax.text(x + 2, y + 7.5, f"{pages}  ·  {projects}", fontsize=7.5, color=GREY)
        ax.add_patch(FancyBboxPatch((x + 2, y + 2.5), 16, 3.5, boxstyle="round,pad=0,rounding_size=0.6",
                                    facecolor=BLUE, edgecolor=BLUE))
        ax.text(x + 10, y + 4.2, "Ask in this domain", ha="center", fontsize=7, color=WHITE)

    save(fig, "ui_05_browse.png")


# ---------------------------------------------------------------------------
# Screen 6 — Before / After comparison
# ---------------------------------------------------------------------------
def ui_before_after():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 55)
    ax.axis("off")

    ax.text(50, 52, "Before Atlas  vs.  With Atlas", ha="center", fontsize=13,
            color=NAVY, fontweight="bold")

    # Before panel
    ax.add_patch(FancyBboxPatch((3, 5), 44, 42, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor="#FFF5F5", edgecolor="#D4A0A0", linewidth=1.2))
    ax.text(25, 43, "Before — reading one by one", ha="center", fontsize=9,
            color="#9C4A3F", fontweight="bold")
    before_items = [
        "Search returns 30+ links across tools",
        "Open each wiki page, PDF, and ticket",
        "Compare versions manually",
        "Spend hours; still unsure which is current",
        "Answer depends on who you ask",
    ]
    for i, item in enumerate(before_items):
        ax.text(6, 37 - i * 5.5, f"✗  {item}", fontsize=7.8, color=TEXT)

    # After panel
    ax.add_patch(FancyBboxPatch((53, 5), 44, 42, boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=GREEN, edgecolor=GREEN_E, linewidth=1.2, alpha=0.35))
    ax.text(75, 43, "With Atlas — ask once", ha="center", fontsize=9,
            color=GREEN_E, fontweight="bold")
    after_items = [
        "Ask one question in plain English",
        "Atlas reads every relevant page for you",
        "Receive one clear, consolidated answer",
        "Every claim linked to its source",
        "Consistent, traceable, permission-safe",
    ]
    for i, item in enumerate(after_items):
        ax.text(56, 37 - i * 5.5, f"✓  {item}", fontsize=7.8, color=TEXT)

    save(fig, "ui_06_before_after.png")


# ---------------------------------------------------------------------------
# Screen 7 — User journey overview
# ---------------------------------------------------------------------------
def ui_journey():
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 38)
    ax.axis("off")
    ax.text(50, 35, "Your journey in four simple steps", ha="center", fontsize=12,
            color=NAVY, fontweight="bold")

    steps = [
        ("1", "Sign in", "Use your\ncompany login"),
        ("2", "Ask", "Type your\nquestion once"),
        ("3", "Review", "Read the\nconsolidated answer"),
        ("4", "Verify", "Open cited\nsources if needed"),
    ]
    xs = [6, 28, 50, 72]
    for (num, title, desc), x in zip(steps, xs):
        ax.add_patch(FancyBboxPatch((x, 12), 18, 18, boxstyle="round,pad=0,rounding_size=1.5",
                                    facecolor=LIGHT, edgecolor=BLUE, linewidth=1.2))
        ax.add_patch(FancyBboxPatch((x + 6.5, 25), 5, 5, boxstyle="circle,pad=0",
                                    facecolor=BLUE, edgecolor=BLUE))
        ax.text(x + 9, 27.5, num, ha="center", va="center", fontsize=10, color=WHITE,
                fontweight="bold")
        ax.text(x + 9, 21.5, title, ha="center", fontsize=9, color=NAVY, fontweight="bold")
        ax.text(x + 9, 17, desc, ha="center", fontsize=7.5, color=GREY)

    for i in range(3):
        ax.annotate("", xy=(xs[i + 1] - 1, 21), xytext=(xs[i] + 19, 21),
                    arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2))

    save(fig, "ui_07_journey.png")


if __name__ == "__main__":
    ui_home()
    ui_ask_question()
    ui_answer()
    ui_sources()
    ui_browse()
    ui_before_after()
    ui_journey()
    print("All UI mockups rendered.")
