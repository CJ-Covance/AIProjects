# AtlasFrontend — Rules

1. New pages: create `src/app/<route>/page.tsx`, mark `"use client"` if interactive (current norm), add Navbar `links` entry.
2. Use page shell: constrained width (`max-w-4xl` or `max-w-6xl`), `px-6 py-10`, navy H1, muted subtitle.
3. Call backend only through `lib/api.ts`; extend that module when adding endpoints.
4. Keep DTOs in `lib/types.ts` aligned with backend `schemas.py`.
5. Reuse `.atlas-card`, `.atlas-btn-*`, `.atlas-input`, `.atlas-select` before inventing new card/button systems.
6. Prefer local React state; do not add global state libraries without a session plan.
7. Errors: catch → string message → inline alert (amber/red bordered boxes as existing pages do).
8. If linking with query params (e.g. `?project=`), implement read-side handling on the destination page.
9. Do not introduce Inter alternatives casually — Inter is current brand font via `next/font` (note: product design rules elsewhere may push expressive fonts for greenfield marketing pages; **this app already uses Inter + Atlas tokens — preserve them**).
10. Keep sibling monorepos out of imports.
