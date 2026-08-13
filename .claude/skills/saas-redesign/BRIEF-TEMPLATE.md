# Redesign brief

Fill this in and present it at step 5. Replace every `<…>` with a real value from the audit. Do not present it with placeholders left in.

---

## Baseline

Screenshots captured at `<path>`:

| Route | View | Screenshot |
|---|---|---|
| `/` | Dashboard.vue | `<file>` |
| `/inventory` | Inventory.vue | `<file>` |
| `/orders` | Orders.vue | `<file>` |
| `/spending` | Spending.vue | `<file>` |
| `/demand` | Demand.vue | `<file>` |
| `/reports` | Reports.vue | `<file>` |

## Audit findings

| Metric | Current | After |
|---|---|---|
| CSS custom properties | `<n>` | ~45 tokens in `styles.css` |
| Distinct hex colors | `<n>` | `<n>` (chart series only) |
| Distinct border-radius values | `<n>` | 3 + pill |
| Distinct box-shadows | `<n>` | 3 + focus ring |
| `@media` queries | `<n>` | 1 breakpoint at 1024px |
| Views overriding global classes | `<list>` | none |

Specific inconsistencies found: `<e.g. cards are 10px radius globally but 12px in modals and Reports.vue>`

## What changes

**Layout.** The 70px horizontal top nav is replaced by a fixed 260px light sidebar on the left: brand block, six icon+label nav rows, and a footer holding the language switcher, profile menu and a collapse toggle. It collapses to a 64px icon rail, and the state persists across reloads. A slim 56px topbar carries the page title and, below 1024px, a hamburger that opens the sidebar as an off-canvas drawer.

**Tokens.** A new `client/src/styles.css` holds the reset, the `:root` token block and every global class currently living in `App.vue`'s unscoped style block. `main.js` imports it. `index.html` finally loads the Inter font it already declares.

**Consistency.** Radius, shadow, spacing and type scales collapse to fixed steps. `Reports.vue` stops shadowing the global card and badge styles. The six modals stop drifting from each other.

## Files

| File | Change | Editor |
|---|---|---|
| `client/src/styles.css` | new — tokens + globals moved out of App.vue | main thread |
| `client/src/main.js` | one import line | main thread |
| `client/index.html` | Inter font links | main thread |
| `client/src/locales/en.js` | +4 nav keys | main thread |
| `client/src/locales/ja.js` | +4 nav keys | main thread |
| `client/src/App.vue` | shell rewrite: sidebar, topbar, collapse | vue-expert |
| `client/src/components/FilterBar.vue` | re-anchor sticky offset, drop own max-width | vue-expert |
| `client/src/views/Reports.vue` | delete global-class overrides | vue-expert |
| 6 modal components | normalize chrome onto tokens | vue-expert, one agent each |

Branch: `redesign/saas-sidebar`. One commit per phase.

## Explicitly not changing

- Any file under `server/` — this is client-only
- Component logic, API calls, router config, filter behavior
- `views/Backlog.vue` — unrouted and unreachable
- The `<PurchaseOrderModal>` reference in `Dashboard.vue` — pre-existing defect
- The `/api/tasks` 404s — pre-existing, backend routes do not exist
- No `BaseModal` extraction, no Options API conversion of `Reports.vue`

## Risk

`App.vue`'s unscoped style block is load-bearing for all seven views. It is moved verbatim first and restyled second, so a regression is bisectable to a single commit.

---

**Approve to proceed?**
