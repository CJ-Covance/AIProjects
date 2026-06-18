# Atlas — Unified Knowledge Platform (UKP)

> **Proof of Concept — Technical & Architectural Proposal**
> A scalable, extensible enterprise platform that centralizes knowledge across
> domains and projects, so people can **ask a question once** and receive a
> **clear, consolidated, cited answer** synthesized from every relevant page —
> instead of reading documents one by one.

---

## Document Set

This folder contains the full POC proposal. Read in the order below.

| # | Document | Audience | What it covers |
|---|----------|----------|----------------|
| 1 | [`01-executive-summary.md`](./01-executive-summary.md) | Executives, sponsors | The problem, the proposed solution, value, and the ask — in one read. |
| 2 | [`02-architecture.md`](./02-architecture.md) | Architects, engineering leads, security | The full technical and architectural design: components, data flow, scalability, extensibility, security, and the technology stack. |
| 3 | [`03-poc-plan.md`](./03-poc-plan.md) | Delivery leads, sponsors | POC scope, phased plan, success criteria, evaluation method, cost, risks, and team model. |

A companion **one-page brief** for circulation is at
[`one-pager.md`](./one-pager.md).

### Printable Word document

A formal, print-ready Microsoft Word version that consolidates the full proposal
(cover page, table of contents, formatted tables, and professional diagrams) is
provided for client distribution:

- **[`Atlas-Unified-Knowledge-Platform-POC.docx`](./Atlas-Unified-Knowledge-Platform-POC.docx)**

> When first opened in Microsoft Word, accept the prompt to update fields (or
> press `Ctrl+A` then `F9`) so the table of contents and page numbers populate.

#### Rebuilding the Word document

The `.docx` and its diagrams are generated from source so they stay easy to
update:

```bash
pip install python-docx matplotlib
python docs/poc/build/render_diagrams.py   # renders PNG diagrams -> docs/poc/assets/
python docs/poc/build/build_docx.py        # builds the .docx
```

- `build/render_diagrams.py` — renders the architecture/flow diagrams to
  print-ready PNGs (no system dependencies).
- `build/build_docx.py` — assembles the formatted Word document.

---

## The idea in one sentence

Today, answering a single cross-team question means hunting through Confluence
spaces, SharePoint sites, shared drives, ticketing systems, and PDFs — reading
each document individually and stitching the answer together by hand. **Atlas**
ingests all of that knowledge, understands it, and returns a single
**grounded, source-cited summary** in response to a natural-language question,
respecting each user's existing access permissions.

## Why now

- Knowledge is fragmented across **many tools, domains, and projects**.
- Search returns *links*, not *answers* — the synthesis work is still manual.
- Modern retrieval-augmented generation (RAG) makes **grounded, cited answers**
  practical and auditable at enterprise scale.
- A thin, **connector-based, extensible** architecture lets us add new sources
  and new domains without re-platforming.

## What this POC proves

1. We can **ingest and unify** heterogeneous knowledge sources behind one model.
2. We can **answer cross-document questions** with high relevance and
   **inline citations** back to the source pages.
3. We can do this **securely** — honoring source-system permissions per user.
4. The architecture **scales horizontally** and is **extensible** to new
   connectors, domains, and answer formats without core rewrites.
