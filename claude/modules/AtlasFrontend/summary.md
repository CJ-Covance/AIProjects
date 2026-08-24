# AtlasFrontend — Summary

Next.js 14 App Router UI under `frontend/src/` for Ask, Browse, and Manage experiences over the Atlas REST API.

## Responsibilities

- Present RAG Q&A with scope filters and citations
- Browse hierarchy tree
- Manage knowledge entities via cascading CRUD columns
- Own visual shell (Navbar, Atlas Tailwind tokens)

## Key paths

| Path | Role |
|------|------|
| `src/app/layout.tsx` | Root layout, Inter font, Navbar, main landmark |
| `src/app/page.tsx` | Ask (`/`) |
| `src/app/browse/page.tsx` | Browse |
| `src/app/manage/page.tsx` | Manage |
| `src/app/globals.css` | Design tokens + utility component classes |
| `src/components/*` | Navbar, ScopeFilters, AnswerDisplay, CitationPanel |
| `src/lib/api.ts` | Typed fetch client |
| `src/lib/types.ts` | Shared TS interfaces |

## Stack

- Next.js 14.2, React 18, TypeScript strict
- Tailwind CSS 3.4
- `output: "standalone"` for Docker
- Env: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)
