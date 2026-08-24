# AtlasSQLite — Known risks

| ID | Risk | Notes |
|----|------|-------|
| SQL-01 | No migration framework | Existing DBs drift from models silently |
| SQL-02 | Embedding blobs in Text | Size + parse cost; not a vector store |
| SQL-03 | Missing FKs on chunk scope columns | Denormalized ids can drift |
| SQL-04 | No unique name constraints | Duplicate source/domain/project names allowed |
| SQL-05 | Docker volume path mismatch | Persist path may not include `atlas.db` |
| SQL-06 | SQLite concurrency | Fine for POC; write locks under concurrent Manage + Ask |
| SQL-07 | Seed idempotency is coarse | Any existing Source skips entire seed |

Sibling SQL risk note: Jira importer SQL Server scripts and Confluence2 Drizzle migrations are separate inventories — do not merge lists here.
