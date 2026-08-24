# Review Checklist — Atlas

Use this before merging any Atlas change (human or AI-authored).

## Intent & scope

- [ ] Change matches an agreed session plan or clearly stated requirement
- [ ] Diff does not touch sibling projects (`confluence2/`, `dotnet-api-test/`, `JiraTestDataImporter/`) unless explicitly in scope
- [ ] No drive-by refactors unrelated to the request
- [ ] AI-generated code was verified against real behavior (not accepted on provenance alone)

## Architecture / layering

- [ ] Routers stay thin; business logic in services where appropriate
- [ ] Schemas updated in `schemas.py` for any API contract change
- [ ] Frontend types + `api.ts` updated in lockstep with backend
- [ ] No new cross-layer imports (see `layering-rules.md`)
- [ ] New page: Navbar link + App Router folder + shared shell conventions

## Correctness

- [ ] Parent FK existence checks on create (source/domain/project/page)
- [ ] Page create/update still indexes (or intentional exception documented)
- [ ] Delete order preserves referential integrity (chunks before/with page via cascade)
- [ ] RAG scope filters still prefer project > domain > source
- [ ] Empty / no-hit search paths still return grounded refusal behavior
- [ ] Missing `OPENAI_API_KEY` handled (health flag, 503 on index, safe search message)

## API / UI contract

- [ ] Status codes consistent (`201`/`204`/`404`/`503`)
- [ ] Out DTOs include expected computed counts
- [ ] Frontend error banners show useful messages
- [ ] Deep links: if query params are written, they are also read

## Data & SQL

- [ ] No destructive schema change without `sql/` docs update
- [ ] Aware that `create_all` does not migrate existing SQLite files
- [ ] Chunk denormalized IDs remain consistent with page hierarchy on index

## Security & ops

- [ ] No secrets committed
- [ ] CORS origins still appropriate for the environment
- [ ] Reminder: there is still **no auth** — do not expose Manage CRUD beyond trusted networks without an auth plan
- [ ] Docker/env examples updated if new required config was added

## Quality bar

- [ ] Matches `coding-standards.md` naming and style
- [ ] No unused dead code introduced without reason
- [ ] Manual smoke: health, hierarchy, search (with and without scope), one CRUD path for touched resources
- [ ] `/claude/` module `known-risks.md` updated if new risks were introduced or mitigated
