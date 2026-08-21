# AtlasBackend — Known risks

| ID | Risk | Severity | Notes |
|----|------|----------|-------|
| BE-01 | Full-scan vector retrieval | High | All scoped chunks loaded; cosine in process memory — will not scale |
| BE-02 | Embeddings in SQLite Text JSON | High | No ANN index; large rows; slow deserialize |
| BE-03 | No authentication | High | CRUD + search are world-readable/writable to anyone with network access |
| BE-04 | No migrations | Medium | `create_all` cannot evolve existing DB schemas safely |
| BE-05 | Sync OpenAI in request path | Medium | Blocks worker thread on embed/chat |
| BE-06 | Reindex on any page update | Medium | Title/url-only updates still re-embed |
| BE-07 | Page commit before index | Medium | `503` during index can leave page with zero chunks |
| BE-08 | Denormalized chunk IDs without FKs | Medium | Orphans possible if data mutated outside ORM cascades |
| BE-09 | Confidence / found_relevant heuristics | Low | Phrase-matching on LLM refusal text is brittle |
| BE-10 | `reindex_all` unwired | Low | Dead capability unless admin path added |
| BE-11 | Docker volume vs DB path mismatch | Medium | `atlas-data`→`/app/data` may not persist `./atlas.db` |
| BE-12 | No automated tests | High | Regressions easy, especially in RAG |
| BE-13 | Hardcoded similarity floor 0.3 | Low | Not in Settings |
| BE-14 | N+1 count queries | Low | List/hierarchy endpoints re-query aggregates |

## AI-generation caution

Prior AI work may have produced coherent structure with incomplete production concerns (auth, migrations, scale). Do not treat “compiles and demos” as “correct for enterprise.”
