---
name: saas-redesign
description: Redesigns this project's Vue 3 client into a modern SaaS interface with a collapsible left sidebar, a CSS custom property token system, and consistent spacing. Use this skill when asked to redesign, restyle, modernize or polish the UI, replace the top nav with a sidebar, or fix inconsistent spacing, colors or card styling under client/src.
---

# SaaS Redesign

Converts the Factory Inventory Management client from its current horizontal top-nav layout into a modern SaaS-style application shell: a collapsible left vertical sidebar, a real design token layer, consistent spacing, and the app's first responsive breakpoints. The target design is fully specified in [REFERENCE.md](REFERENCE.md) — do not invent an alternative one.

This is an **audit → propose → approve → apply → verify** workflow. Step 5 is a hard stop.

## Workflow

1. **Confirm both dev servers are running.** Frontend on `http://localhost:3030`, backend on `http://localhost:8090`. Use the `/start` command, or `cd server && uv run python main.py` and `cd client && npm run dev`. If the backend is down, views render error states and the screenshots are worthless.

2. **Capture the baseline.** With `mcp__playwright__*` against `http://localhost:3030`, screenshot all six routes: `/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`. Record the file paths — the brief and the final report both reference them.

3. **Audit the current state.** Read `client/src/App.vue` (the whole file — its unscoped `<style>` is the de-facto design system), `client/src/main.js`, `client/index.html`, and `client/src/components/FilterBar.vue`. Skim each view's `<style scoped>`. Record concrete numbers: count of hardcoded hex values, distinct border-radius values, distinct box-shadows, `@media` queries, and every place a view redefines a global class.

4. **Write the brief.** Fill in [BRIEF-TEMPLATE.md](BRIEF-TEMPLATE.md) using the audit numbers and the target spec from [REFERENCE.md](REFERENCE.md). Name every file that will change and who edits it.

5. **STOP and present the brief. Wait for explicit approval.** Do not create a branch, do not edit a single file, do not spawn a subagent before the user approves. If the user asks for changes, revise the brief and stop again.

6. **Create the branch.** `git checkout -b redesign/saas-sidebar`. Never redesign directly on `main` or on the current working branch.

7. **Apply, phase by phase.** Follow the phase table below exactly. Commit after each phase with a semantic message (`refactor(client): ...` / `feat(client): ...`) so a bad phase reverts cleanly.

8. **Verify and report.** Run the verification checklist below, then report what changed, what was verified, and what was deliberately left alone.

## Phases

| Phase | Files | Who edits | Parallel |
|---|---|---|---|
| 1 | `client/src/styles.css` (new), `client/src/main.js`, `client/index.html` | main thread | with phase 2 |
| 2 | `client/src/locales/en.js`, `client/src/locales/ja.js` | main thread | with phase 1 |
| 3 | `client/src/App.vue` | vue-expert | no |
| 4 | `client/src/components/FilterBar.vue`, `client/src/views/Reports.vue` | vue-expert | yes, one agent each |
| 5 | the six modal components | vue-expert | yes, one agent each |
| 6 | verification | main thread | no |

Phase 3 must land and render before phases 4 and 5 can be judged visually.

## Delegation contract

Project CLAUDE.md rule, non-negotiable: **any time you create or significantly modify a `.vue` file you must delegate to `vue-expert`.**

- Non-`.vue` files (`styles.css`, `main.js`, `index.html`, `locales/*.js`) are edited directly in the main thread. Analysis, auditing and verification also stay in the main thread.
- Every `.vue` edit goes through the Agent tool with `subagent_type: vue-expert`.
- **One agent per file. Never two agents on the same file.** Parallelism is split by file, not by concern.
- Every delegation prompt must include:
  - the exact absolute file path,
  - the token names the agent is allowed to use (paste the relevant block from REFERENCE.md — the agent cannot see this skill),
  - the specific markup and CSS to produce,
  - the literal URL `http://localhost:3030`. The `vue-expert` agent definition still says port 3000 and is stale; if you do not pass the correct URL it will test against a dead port.
  - a reminder that behavior must not change — this is a restyle, not a refactor of logic.
- `vue-expert` is scoped to `client/src/**`, refuses `server/`, and will not add emojis. Do not ask it to.

## Verification

1. Reload all six routes and screenshot each; compare against the phase-0 baseline.
2. Toggle the sidebar collapse, reload the page, confirm the rail state survived (`localStorage` key `app-sidebar-collapsed`).
3. Resize to 900px wide — sidebar goes off-canvas, hamburger opens it, no horizontal scroll on `body`.
4. Switch the locale to 日本語 and confirm every sidebar label is translated, including Reports.
5. Read the console. It must be clean **except** for the pre-existing `/api/tasks` 404s (see Gotchas) — those are not yours.
6. `cd tests && uv run pytest backend/ -v` — a client-only change must not move these. Run them to prove it.
7. `git diff main...redesign/saas-sidebar --stat` and review.

## Gotchas

- `App.vue`'s unscoped `<style>` block is **load-bearing for every view** (`.card`, `.stat-card`, `.badge`, `.page-header`, `.table-container`, bare `table` styles). Moving it into `styles.css` must be a faithful move first, restyled second. Rewrite it in place and all seven views break at once.
- `client/src/views/Reports.vue` is the only Options API view and it **shadows** the global `.card`, `.card-header`, `.card-title`, `.stats-grid`, `.stat-card` and `.badge` with different values. Skip its cleanup and it stays visibly inconsistent no matter what the token layer says.
- `client/src/components/FilterBar.vue` hardcodes `top: 70px` to sit under the old 70px header. A sidebar layout must re-anchor it or it floats.
- `client/src/views/Backlog.vue` is **not registered in the router** in `client/src/main.js` and has no `<style>` block. It is unreachable — restyle it only if the user explicitly asks.
- `client/src/views/Dashboard.vue` renders `<PurchaseOrderModal>`, which is not imported, not registered, and does not exist on disk. Pre-existing defect. Leave it.
- `/api/tasks` and `/api/purchase-orders` are called from `client/src/api.js` but have no routes in `server/main.py`. The task calls in `App.vue` 404 today. **Preserve that behavior — do not "fix" it during a redesign.**
- The repo is public. No credentials, internal hostnames, or private registry URLs in any file this skill touches.
