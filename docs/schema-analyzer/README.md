# SchemaDoc AI — Documentation

Client-facing and build documentation for the AI-Powered Database Schema Analyzer.

## Files

| File | Purpose |
|------|---------|
| [SchemaDoc-AI-Client-Brief.md](./SchemaDoc-AI-Client-Brief.md) | Client-readable requirements summary (Markdown) |
| [SchemaDoc-AI-Build-Prompt.md](./SchemaDoc-AI-Build-Prompt.md) | Full technical build prompt for developers / AI agents |
| [SchemaDoc-AI-Client-Requirements.pdf](./SchemaDoc-AI-Client-Requirements.pdf) | **Printable PDF for client meetings** |

## Regenerate the client PDF

```bash
pip install reportlab
python docs/schema-analyzer/build/build_client_pdf.py
```

Output: `docs/schema-analyzer/SchemaDoc-AI-Client-Requirements.pdf`

## Client constraints (summary)

- **No application database** — filesystem text/JSON storage only
- **Python** backend (FastAPI)
- **React** UI
- **Printable PDF** as the primary artifact for stakeholder discussion
