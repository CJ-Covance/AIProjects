# AtlasBackend — Rules

1. All new endpoints live in an existing or new router under `app/routers/` and are registered in `main.py`.
2. Request/response contracts are defined in `schemas.py` before (or with) the router.
3. Indexing and RAG must use `services/indexer.py`, `services/embeddings.py`, and `services/rag.py` — do not reimplement cosine search or chunk windows in routers.
4. On page content create/update, call `index_web_page`; surface `503` if OpenAI is required and unavailable (match existing pages router behavior).
5. Preserve cascade-delete semantics on hierarchy models.
6. Scope filter preference for search: `project_id` > `domain_id` > `source_id`.
7. Do not commit API keys; read from `settings.openai_api_key`.
8. Keep answers grounded: system prompt must continue to forbid unsupported claims and require citations.
9. `reindex_all()` exists in indexer but is not exposed — wire it only with an explicit product decision (admin endpoint or CLI).
10. Reject changes that import from `confluence2` or other sibling trees.
