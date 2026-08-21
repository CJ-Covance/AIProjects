# AtlasFrontend — Known risks

| ID | Risk | Severity | Notes |
|----|------|----------|-------|
| FE-01 | Browse→Ask deep link broken | Medium | `/?project=` not consumed by Ask |
| FE-02 | No auth gate on Manage | High | Anyone can mutate knowledge base |
| FE-03 | Markdown not rendered in answers | Low | Manage placeholder mentions Markdown; Ask is plain text + `[N]` markers |
| FE-04 | Unused `api.getPage` / Geist fonts | Low | Dead surface / leftover create-next-app assets |
| FE-05 | Docker copies `./public` | Medium | No `public/` tree may break image build depending on Docker stage |
| FE-06 | No tests / weak a11y | Medium | Clickable citation `div`s; emoji in Browse |
| FE-07 | Manage Add no-ops without parent | Low | Silent when domain/project/page parent not selected |
| FE-08 | Error `detail` shape assumptions | Low | Non-string FastAPI validation errors may stringify poorly |
| FE-09 | Stock frontend README | Low | Still create-next-app boilerplate in places |

## New page guidance

Follow Ask/Browse/Manage patterns. Update this file when the new page introduces new client risks (polling, uploads, streaming, auth).
