"""Render professional architecture/flow diagrams for the Atlas POC Word document.

Produces print-ready PNGs (300 DPI) into docs/poc/assets/ using matplotlib only,
so the build has no system (graphviz/mermaid) dependencies.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS, exist_ok=True)

# Professional palette
NAVY = "#1F3A5F"
BLUE = "#2E5E8C"
LIGHT = "#EAF1F8"
LIGHT2 = "#DCE7F3"
ACCENT = "#C8A24B"   # muted gold
GREEN = "#E7F0E7"
GREEN_E = "#5B7A5B"
RED = "#F4E3E1"
RED_E = "#9C4A3F"
GREY_E = "#5B6470"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"


def new_ax(w=12, h=7.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fill=LIGHT, edge=BLUE, fc="#222222",
        fs=10.5, bold=False, rounded=0.02, lw=1.4):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rounded*100}",
        linewidth=lw, edgecolor=edge, facecolor=fill, mutation_aspect=1)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=fc, wrap=True,
            fontweight="bold" if bold else "normal", zorder=5)
    return (x + w / 2, y + h / 2)


def band(ax, x, y, w, h, title, fill=LIGHT2, edge=BLUE):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.2",
                       linewidth=1.6, edgecolor=edge, facecolor=fill, alpha=0.55)
    ax.add_patch(p)
    ax.text(x + 1.6, y + h - 2.4, title, ha="left", va="top",
            fontsize=11, color=NAVY, fontweight="bold")


def arrow(ax, p1, p2, color=NAVY, lw=1.6, style="-|>", dashed=False, rad=0.0):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                        linewidth=lw, color=color,
                        connectionstyle=f"arc3,rad={rad}",
                        linestyle="--" if dashed else "-", zorder=1)
    ax.add_patch(a)


def title(ax, t):
    ax.text(50, 98, t, ha="center", va="top", fontsize=15,
            color=NAVY, fontweight="bold")


def save(fig, name):
    out = os.path.join(ASSETS, name)
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.normpath(out))


# ---------------------------------------------------------------------------
# Figure 1 — High-level architecture (four planes)
# ---------------------------------------------------------------------------
def fig_architecture():
    fig, ax = new_ax(12, 8.4)
    title(ax, "Atlas high-level architecture")

    # Sources column (left)
    band(ax, 1, 8, 17, 80, "Knowledge sources")
    srcs = ["Confluence / Wiki", "SharePoint / OneDrive", "File shares & PDFs",
            "Jira / ticketing", "Databases / APIs"]
    sc = []
    for i, s in enumerate(srcs):
        cy = 74 - i * 13
        sc.append(box(ax, 2.5, cy, 14, 9, s, fill=WHITE, fs=9.2))

    # Ingestion plane
    band(ax, 22, 56, 30, 32, "Ingestion plane")
    con = box(ax, 24, 71, 26, 11, "Connector framework\n(scheduled + webhook)", fs=9.5)
    pipe = box(ax, 24, 58, 26, 11,
               "Processing pipeline\nparse · chunk · enrich · embed", fs=9.5)

    # Knowledge plane
    band(ax, 22, 8, 30, 44, "Knowledge plane")
    obj = box(ax, 24, 38, 12, 9, "Raw / object\nstore", fill=GREEN, edge=GREEN_E, fs=8.6)
    meta = box(ax, 38, 38, 12, 9, "Document &\nmetadata", fill=GREEN, edge=GREEN_E, fs=8.6)
    vec = box(ax, 24, 27, 12, 9, "Vector\nindex", fill=GREEN, edge=GREEN_E, fs=8.6)
    kw = box(ax, 38, 27, 12, 9, "Keyword\nindex", fill=GREEN, edge=GREEN_E, fs=8.6)
    kg = box(ax, 31, 16, 12, 9, "Knowledge graph\n(optional)", fill=GREEN, edge=GREEN_E, fs=8.2)

    # Query plane
    band(ax, 56, 30, 26, 58, "Query plane (RAG core)")
    orch = box(ax, 58, 71, 22, 11, "Query orchestrator", fs=9.5)
    retr = box(ax, 58, 56, 22, 11, "Hybrid retriever\n+ reranker", fs=9.5)
    synth = box(ax, 58, 41, 22, 11, "Answer synthesizer\n(LLM) + citations",
                fill=LIGHT, edge=ACCENT, fs=9.3)

    # Experience plane
    band(ax, 86, 30, 13, 58, "Experience")
    ui = box(ax, 87, 71, 11, 11, "Web UI /\nchat", fs=8.8)
    api = box(ax, 87, 56, 11, 11, "Query &\nAdmin APIs", fs=8.8)
    idp = box(ax, 87, 41, 11, 11, "Identity\nSSO/OIDC", fill=RED, edge=RED_E, fs=8.6)

    # Platform footer
    box(ax, 56, 9, 43, 16,
        "Security · Permission-aware retrieval · Observability & evaluation · "
        "Governance",
        fill=LIGHT2, edge=BLUE, fs=9.5, bold=True)

    # Flows (connect to box edges to avoid lines crossing through labels)
    for c in sc:
        arrow(ax, (16.5, c[1]), (24, con[1]), color=GREY_E, lw=1.0, rad=-0.15)
    arrow(ax, (37, 71), (37, 69))               # connector -> pipeline
    for t in [obj, meta, vec, kw, kg]:
        arrow(ax, (37, 58), (t[0], t[1] + 9), color=GREEN_E, lw=1.0, rad=-0.12)
    # Experience -> query (vertical within stacks / across boundary)
    arrow(ax, (92.5, 71), (92.5, 67))           # UI -> API
    arrow(ax, (87, 61.5), (80, 73), color=NAVY, rad=0.18)   # API -> orchestrator
    arrow(ax, (69, 71), (69, 67))               # orchestrator -> retriever
    # Retriever <-> knowledge plane (single double-headed connector)
    arrow(ax, (58, 60), (52, 40), color=BLUE, lw=1.6, style="<|-|>", rad=0.18)
    arrow(ax, (69, 56), (69, 52))               # retriever -> synthesizer
    arrow(ax, (80, 46.5), (87, 58), color=ACCENT, lw=1.6, rad=-0.18)  # answer -> API
    arrow(ax, (87, 44), (80, 60), color=RED_E, lw=1.0, dashed=True, rad=-0.15)  # IdP -> retriever

    save(fig, "fig1_architecture.png")


# ---------------------------------------------------------------------------
# Figure 2 — Ingestion processing pipeline (linear)
# ---------------------------------------------------------------------------
def fig_pipeline():
    fig, ax = new_ax(12, 4.6)
    title(ax, "Knowledge ingestion & processing pipeline")
    steps = [
        "Fetch\nraw document",
        "Extract text\n(HTML, PDF,\nDOCX, OCR)",
        "Normalize\nto canonical\ndoc + structure",
        "Chunk\n(structure-aware,\noverlapping)",
        "Enrich metadata\n(domain, project,\nowner, ACL)",
        "Embed chunks\n(embedding model)",
        "Index\nvector · keyword\n· graph · meta",
    ]
    n = len(steps)
    w = 12.0
    gap = (100 - n * w) / (n + 1)
    cy = 42
    centers = []
    for i, s in enumerate(steps):
        x = gap + i * (w + gap)
        fill = LIGHT if i not in (3, 5) else LIGHT2
        centers.append(box(ax, x, cy, w, 22, s, fill=fill, fs=8.4))
    for i in range(n - 1):
        arrow(ax, (centers[i][0] + w / 2, cy + 11),
              (centers[i + 1][0] - w / 2, cy + 11))
    ax.text(50, 22, "Idempotent, queue-driven stages — each scales independently; "
            "re-processing updates chunks in place and removes orphans.",
            ha="center", va="center", fontsize=9, color=GREY_E, style="italic")
    save(fig, "fig2_pipeline.png")


# ---------------------------------------------------------------------------
# Figure 3 — Ask-once query / answer (RAG) flow
# ---------------------------------------------------------------------------
def fig_query_flow():
    fig, ax = new_ax(12, 6.6)
    title(ax, "\u201cAsk once\u201d query-to-answer flow")

    q = box(ax, 4, 70, 20, 14, "1. User asks a\nquestion (once)", fill=LIGHT2, fs=9.5)
    intent = box(ax, 30, 70, 22, 14,
                 "2. Understand intent,\nexpand query,\nresolve filters", fs=9.2)
    retr = box(ax, 58, 70, 22, 14,
               "3. Hybrid retrieval\n(semantic + keyword)\nacross all sources", fs=9.2)
    acl = box(ax, 58, 44, 22, 13,
              "4. Permission filter\n(user-entitled\ncontent only)", fill=RED,
              edge=RED_E, fs=9.2)
    rr = box(ax, 30, 44, 22, 13,
             "5. Rerank, dedup\n& diversify\nacross documents", fs=9.2)
    synth = box(ax, 30, 18, 22, 14,
                "6. Synthesize one\ngrounded answer\n(LLM)", fill=LIGHT, edge=ACCENT,
                fs=9.3, bold=True)
    out = box(ax, 58, 18, 28, 14,
              "7. Consolidated answer\n+ inline citations\n+ confidence",
              fill=LIGHT2, edge=ACCENT, fs=9.3, bold=True)

    arrow(ax, (24, 77), (30, 77))      # q -> intent
    arrow(ax, (52, 77), (58, 77))      # intent -> retrieval
    arrow(ax, (69, 70), (69, 57))      # retrieval -> permission filter
    arrow(ax, (58, 50.5), (52, 50.5))  # filter -> rerank
    arrow(ax, (41, 44), (41, 32))      # rerank -> synthesize
    arrow(ax, (52, 25), (58, 25))      # synthesize -> output
    ax.text(50, 6, "Sources are intersected with the user\u2019s entitlements before "
            "anything reaches the model \u2014 answers can never leak restricted content.",
            ha="center", va="center", fontsize=9, color=RED_E, style="italic")
    save(fig, "fig3_query_flow.png")


# ---------------------------------------------------------------------------
# Figure 4 — Permission-aware retrieval
# ---------------------------------------------------------------------------
def fig_permissions():
    fig, ax = new_ax(11, 4.2)
    title(ax, "Permission-aware retrieval")
    u = box(ax, 4, 48, 22, 20, "User identity\n(groups, roles)", fill=LIGHT2, fs=9.5)
    d = box(ax, 4, 14, 22, 20, "Candidate documents\n(with captured ACLs)",
            fill=GREEN, edge=GREEN_E, fs=9.2)
    f = box(ax, 38, 31, 18, 20, "ACL filter\n(intersection)", fill=RED, edge=RED_E,
            fs=9.5, bold=True)
    ok = box(ax, 68, 48, 28, 20, "Entitled results\n\u2192 retrieval / LLM",
             fill=LIGHT, edge=GREEN_E, fs=9.3)
    no = box(ax, 68, 14, 28, 20, "Blocked content\n\u2192 never sent to LLM",
             fill=WHITE, edge=RED_E, fc=RED_E, fs=9.3)
    arrow(ax, (26, 56), (38, 45), rad=-0.05)
    arrow(ax, (26, 26), (38, 37), rad=0.05)
    arrow(ax, (56, 45), (68, 56), color=GREEN_E, rad=-0.05)
    arrow(ax, (56, 37), (68, 26), color=RED_E, rad=0.05)
    save(fig, "fig4_permissions.png")


# ---------------------------------------------------------------------------
# Figure 5 — Scalability (two decoupled planes)
# ---------------------------------------------------------------------------
def fig_scalability():
    fig, ax = new_ax(12, 5.0)
    title(ax, "Scalability: decoupled, independently scalable planes")
    band(ax, 2, 10, 46, 74, "Ingestion (throughput-bound, async)")
    q1 = box(ax, 5, 60, 16, 12, "Connector\nqueue", fill=WHITE, fs=8.8)
    w1 = box(ax, 28, 60, 16, 12, "Connector\nworkers (N)", fs=8.8)
    q2 = box(ax, 5, 42, 16, 12, "Processing\nqueue", fill=WHITE, fs=8.8)
    w2 = box(ax, 28, 42, 16, 12, "Pipeline\nworkers (N)", fs=8.8)
    q3 = box(ax, 5, 24, 16, 12, "Embed\nqueue", fill=WHITE, fs=8.8)
    w3 = box(ax, 28, 24, 16, 12, "Embedding\nworkers (N)", fs=8.8)
    arrow(ax, q1, w1); arrow(ax, w1, (13, 54), rad=0); arrow(ax, (13, 60), (13, 54))
    arrow(ax, q2, w2); arrow(ax, q3, w3)
    arrow(ax, (36, 60), (36, 54)); arrow(ax, (36, 42), (36, 36))

    band(ax, 52, 10, 46, 74, "Query (latency-bound, sync)")
    lb = box(ax, 66, 66, 18, 12, "Load balancer", fs=8.8)
    a1 = box(ax, 56, 44, 38, 14, "Stateless API / orchestrator (N)", fs=9.2)
    rp = box(ax, 56, 24, 18, 12, "Retrieval\npool", fs=8.8)
    lp = box(ax, 76, 24, 18, 12, "LLM pool /\nprovider", fill=LIGHT, edge=ACCENT, fs=8.8)
    arrow(ax, lb, (75, 58)); arrow(ax, (75, 44), rp, rad=0.15)
    arrow(ax, (75, 44), lp, rad=-0.15)
    save(fig, "fig5_scalability.png")


# ---------------------------------------------------------------------------
# Figure 6 — Deployment view
# ---------------------------------------------------------------------------
def fig_deployment():
    fig, ax = new_ax(12, 6.0)
    title(ax, "Deployment view (client VPC / on-prem)")
    band(ax, 2, 40, 64, 48, "Kubernetes cluster")
    ing = box(ax, 5, 70, 18, 12, "Ingress /\nAPI gateway", fs=8.8)
    api = box(ax, 26, 70, 18, 12, "Query API +\norchestrator (HPA)", fs=8.6)
    ui = box(ax, 47, 70, 16, 12, "Web UI", fs=8.8)
    wk = box(ax, 5, 50, 26, 12, "Ingestion & embedding\nworkers (HPA)", fs=8.6)
    md = box(ax, 35, 50, 28, 12, "Embedding / LLM serving\n(optional self-hosted)",
             fill=LIGHT, edge=ACCENT, fs=8.4)

    band(ax, 70, 40, 28, 48, "Stateful services")
    pg = box(ax, 72, 70, 24, 12, "PostgreSQL + pgvector", fill=GREEN, edge=GREEN_E, fs=8.4)
    osr = box(ax, 72, 56, 24, 11, "OpenSearch", fill=GREEN, edge=GREEN_E, fs=8.6)
    rd = box(ax, 72, 43, 11, 11, "Redis", fill=GREEN, edge=GREEN_E, fs=8.6)
    ob = box(ax, 85, 43, 11, 11, "Object\nstore", fill=GREEN, edge=GREEN_E, fs=8.2)

    idp = box(ax, 14, 20, 26, 12, "Enterprise IdP (OIDC/SAML)", fill=RED, edge=RED_E, fs=8.8)
    src = box(ax, 55, 20, 26, 12, "Source systems", fill=WHITE, fs=8.8)

    arrow(ax, ing, api); arrow(ax, api, ui, rad=0)
    arrow(ax, api, (72, 74), rad=-0.1)
    arrow(ax, api, osr, rad=-0.05)
    arrow(ax, wk, src, color=GREY_E, rad=-0.2)
    arrow(ax, wk, (72, 60), color=GREY_E, rad=-0.1)
    arrow(ax, api, idp, color=RED_E, dashed=True, rad=0.1)
    ax.text(50, 8, "All components run inside the client security boundary; "
            "the only optional egress (managed model API) can be removed by self-hosting.",
            ha="center", va="center", fontsize=8.6, color=GREY_E, style="italic")
    save(fig, "fig6_deployment.png")


if __name__ == "__main__":
    fig_architecture()
    fig_pipeline()
    fig_query_flow()
    fig_permissions()
    fig_scalability()
    fig_deployment()
    print("All diagrams rendered.")
