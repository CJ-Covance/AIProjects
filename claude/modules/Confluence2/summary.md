# Confluence2 — Summary

Sibling enterprise RAG platform under `confluence2/` (pnpm monorepo). **Not** part of the Atlas runtime.

## Stack (high level)

- Express API + Drizzle/Postgres FTS
- Vite React client + React Query
- Replit OIDC auth
- Gemini for answer synthesis
- OpenAPI (`api-spec`) as contract source of truth

## Rule for Atlas work

Do not import, copy, or couple Atlas changes to this tree unless a session explicitly scopes a cross-product effort.
