# JiraTestDataImporter — Rules

1. Keep `Program.cs` orchestration-only; business logic in Services.
2. Depend on interfaces (`IJiraClient`, `IDatabaseRepository`) for testability.
3. Secrets via config/env — never hardcode tokens.
4. Respect DryRun/TestMode flags.
5. SQL scripts live under `Database/SqlScripts/` — document changes in `claude/sql/` only if this module is in scope.
