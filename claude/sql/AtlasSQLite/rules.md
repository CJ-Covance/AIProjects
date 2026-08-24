# AtlasSQLite — Rules

1. Prefer ORM model changes over ad-hoc SQL.
2. Any production-impacting schema change needs an explicit upgrade path (script + docs) because `create_all` will not alter existing tables.
3. Keep UUID string PKs and UTC timestamps consistent.
4. When indexing, refresh chunk rows fully for a page (delete + rewrite) to avoid stale embeddings.
5. Do not add stored procedures — SQLite deployment model does not use them.
6. Document new scripts in `migration-scripts-list.txt` when introduced.
7. Never point Atlas at Confluence2 Postgres or Jira importer SQL Server schemas without a deliberate multi-store design.
