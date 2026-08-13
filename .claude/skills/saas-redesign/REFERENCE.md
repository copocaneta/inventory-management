# Target design specification

The concrete end state for the redesign. Everything here is derived from what the codebase already uses — no new brand colors, no new dependencies, no CSS framework. Deps stay `vue`, `vue-router`, `axios`.

## 1. Token layer — new file `client/src/styles.css`

### Why a new file rather than `:root` inside App.vue

`App.vue` becomes the sidebar shell component. Keeping a 300-line design system inside it makes both jobs harder, and it means `vue-expert` has to touch the token block every time it touches layout. A separate file also lets phase 1 (main thread, non-`.vue`) land before phase 3 (delegated `.vue` work), so the shell can consume tokens that already exist.

Wiring is one line in `client/src/main.js`:

```js
import './styles.css'
```

Place it above the `App.vue` import so component styles win over globals.

### What moves into styles.css

Move, verbatim first, from `App.vue`'s unscoped `<style>`:

- the `*` reset and `body` rules
- `.page-header`, `.page-header h2`, `.page-header p`
- `.stats-grid`, `.stat-card` (+ `.warning` `.success` `.danger` `.info` variants), `.stat-label`, `.stat-value`
- `.card`, `.card-header`, `.card-title`
- `.table-container` and the bare `table` / `thead` / `th` / `td` / `tbody tr` / `tbody tr:hover` rules
- `.badge` and all ten variants
- `.loading`, `.error`

Do **not** move `.app`, `.top-nav`, `.nav-container`, `.logo`, `.subtitle`, `.nav-tabs`, `.main-content` — those are shell layout and are replaced wholesale in phase 3.

Once moved and verified rendering identically, rewrite the values in terms of the tokens below.

### The tokens

```css
:root {
  /* surface + text */
  --c-bg: #f8fafc;
  --c-surface: #ffffff;
  --c-surface-alt: #f1f5f9;
  --c-border: #e2e8f0;
  --c-border-strong: #cbd5e1;
  --c-text: #0f172a;
  --c-text-muted: #64748b;
  --c-text-subtle: #94a3b8;

  /* accent + status */
  --c-primary: #2563eb;
  --c-primary-soft: #eff6ff;
  --c-focus: #3b82f6;
  --c-success: #10b981;
  --c-warning: #f59e0b;
  --c-danger: #ef4444;
  --c-info: #3b82f6;

  /* spacing — 4px base */
  --s-1: 0.25rem;
  --s-2: 0.5rem;
  --s-3: 0.75rem;
  --s-4: 1rem;
  --s-5: 1.25rem;
  --s-6: 1.5rem;
  --s-8: 2rem;
  --s-12: 3rem;

  /* radius — collapses the existing 4/6/8/10/12px sprawl to three steps */
  --r-sm: 6px;
  --r-md: 10px;
  --r-lg: 14px;
  --r-pill: 9999px;

  /* elevation — replaces 14 ad-hoc shadows */
  --e-1: 0 1px 2px rgba(15, 23, 42, 0.06);
  --e-2: 0 4px 12px rgba(15, 23, 42, 0.08);
  --e-3: 0 20px 50px rgba(15, 23, 42, 0.15);
  --ring: 0 0 0 3px rgba(59, 130, 246, 0.15);

  /* type */
  --t-xs: 0.75rem;
  --t-sm: 0.8125rem;
  --t-md: 0.875rem;
  --t-base: 0.9375rem;
  --t-lg: 1.125rem;
  --t-xl: 1.5rem;
  --t-2xl: 1.875rem;

  /* layout */
  --sidebar-w: 260px;
  --sidebar-w-rail: 64px;
  --topbar-h: 56px;
  --content-max: 1600px;
}
```

Mapping rule when rewriting existing CSS: `#64748b` → `var(--c-text-muted)`, `#e2e8f0` → `var(--c-border)`, `#0f172a` → `var(--c-text)`, `#f8fafc` → `var(--c-bg)`, `#f1f5f9` → `var(--c-surface-alt)`, `#2563eb` → `var(--c-primary)`. Chart series colors (`#8b5cf6`, `#c4b5fd`, `#86efac`, `#fcd34d`, the `#667eea`/`#764ba2` gradient) stay literal — they are data encodings, not UI chrome.

### Font

`client/index.html` currently links no stylesheet and no font, so the Inter family declared in `App.vue` never loads and silently falls back. Add to `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## 2. Shell — `client/src/App.vue`

### Structure

```
.app-shell            display:grid; grid-template-columns: var(--sidebar-w) 1fr; min-height:100vh
├── aside.sidebar     position:fixed; width:var(--sidebar-w); height:100vh
│   ├── .sidebar-brand   logo mark + t('nav.companyName'); t('nav.subtitle') hidden when collapsed
│   ├── nav.sidebar-nav  6 router-links, each = inline SVG icon + label span
│   └── .sidebar-foot    LanguageSwitcher + ProfileMenu + collapse toggle button
└── .app-main         grid-column 2
    ├── header.topbar    height:var(--topbar-h); hamburger (mobile only) + current page title
    ├── <FilterBar />
    └── main.main-content  max-width:var(--content-max); padding: var(--s-6) var(--s-8)
```

`ProfileDetailsModal` and `TasksModal` stay mounted at the end of the template exactly as they are today.

### Nav items

Six, in this order, each with an inline SVG icon (24x24, `stroke="currentColor"`, `fill="none"`, `stroke-width="1.75"`). **No emojis, no icon font, no icon package.**

| Route | Label | Icon suggestion |
|---|---|---|
| `/` | `t('nav.overview')` | grid / squares |
| `/inventory` | `t('nav.inventory')` | box |
| `/orders` | `t('nav.orders')` | clipboard list |
| `/spending` | `t('nav.finance')` | currency / chart |
| `/demand` | `t('nav.demandForecast')` | trending-up arrow |
| `/reports` | `t('nav.reports')` | document with lines |

`nav.reports` does not exist yet — `App.vue` hardcodes the English string `Reports`. Phase 2 adds the key.

### Active state

Drop the six manual `:class="{ active: $route.path === '...' }"` bindings. Use the router's own classes:

```html
<router-link to="/" exact-active-class="active" class="sidebar-link"> … </router-link>
<router-link to="/inventory" active-class="active" class="sidebar-link"> … </router-link>
```

Only `/` needs `exact-active-class`; the rest use `active-class`.

The active indicator becomes a 3px left accent bar, replacing the old `.nav-tabs a.active::after` bottom underline:

```css
.sidebar-link {
  display: flex;
  align-items: center;
  gap: var(--s-3);
  padding: var(--s-3) var(--s-4);
  margin: 0 var(--s-3);
  border-radius: var(--r-sm);
  color: var(--c-text-muted);
  font-size: var(--t-md);
  font-weight: 500;
  text-decoration: none;
  position: relative;
  transition: background 0.15s ease, color 0.15s ease;
}
.sidebar-link:hover { background: var(--c-surface-alt); color: var(--c-text); }
.sidebar-link.active { background: var(--c-primary-soft); color: var(--c-primary); }
.sidebar-link.active::before {
  content: '';
  position: absolute;
  left: calc(var(--s-3) * -1);
  top: 20%;
  bottom: 20%;
  width: 3px;
  border-radius: 0 2px 2px 0;
  background: var(--c-primary);
}
.sidebar-link svg { width: 20px; height: 20px; flex-shrink: 0; }
```

### Collapse behavior

State lives in `App.vue`'s `setup()`, mirroring how `client/src/composables/useI18n.js` reads `localStorage` at module scope:

```js
const collapsed = ref(localStorage.getItem('app-sidebar-collapsed') === 'true')
const toggleSidebar = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem('app-sidebar-collapsed', String(collapsed.value))
}
```

Bind on the shell root, and override the width token rather than writing two sets of rules:

```html
<div class="app-shell" :class="{ 'is-collapsed': collapsed }">
```

```css
.app-shell.is-collapsed { --sidebar-w: var(--sidebar-w-rail); }
.is-collapsed .sidebar-link { justify-content: center; margin: 0 var(--s-2); padding: var(--s-3); }
.is-collapsed .sidebar-link span,
.is-collapsed .sidebar-brand .subtitle { display: none; }
```

Collapsed links keep a `:title` attribute so the label is still discoverable.

### Responsive — the app's first breakpoints

```css
@media (max-width: 1024px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    z-index: 300;
  }
  .app-shell.is-open .sidebar { transform: translateX(0); }
  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: 290;
  }
  .topbar-hamburger { display: inline-flex; }
}
```

The hamburger is hidden above 1024px. Opening the drawer sets `is-open`; clicking the backdrop or navigating closes it.

### Z-index scale

Keep these consistent, they currently conflict: sidebar `300`, backdrop `290`, topbar `200`, FilterBar `90`, modals `2000`. `TasksModal` uses `1000` today and must be raised to `2000` in phase 5.

### Preserve unchanged

The tasks state and the `api.getTasks` / `createTask` / `deleteTask` / `toggleTask` calls in `App.vue`'s `setup()`, and the `ProfileDetailsModal` / `TasksModal` mounts with their existing props and event handlers. This is a restyle.

## 3. Dependent fixes

### `client/src/components/FilterBar.vue`

- `top: 70px` → `top: var(--topbar-h)`. This is the only reason the filter strip currently aligns.
- Delete `.filters-container`'s own `max-width: 1600px` and `padding: 0 2rem` — the content column owns width now, and leaving them double-indents the bar against the sidebar.
- Rewrite `.filter-select` and `.reset-filters-btn` onto tokens; focus ring becomes `box-shadow: var(--ring)`.

### `client/src/views/Reports.vue`

Its `<style scoped>` block redefines global classes with different values — `.card` (radius 12px, no border, different shadow), `.card-header`, `.card-title`, `.stats-grid`, `.stat-card`, `.badge` and the three badge variants. **Delete those rules** so the view inherits `styles.css`. Keep only genuinely local rules: `.reports-table`, `.chart-container`, `.bar-chart`, `.bar-wrapper`, `.bar-container`, `.bar`, `.bar-label`, `.positive-change`, `.negative-change`.

It is the only Options API view. Do not convert it — out of scope, and conversion risks the hand-rolled formatting methods.

### The six modals

`BacklogDetailModal.vue`, `CostDetailModal.vue`, `InventoryDetailModal.vue`, `ProductDetailModal.vue`, `ProfileDetailsModal.vue`, `TasksModal.vue`.

Chrome is copy-pasted across all six and `TasksModal` has drifted. Normalize each onto this, one agent per file:

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--s-4);
  z-index: 2000;
}
.modal-container {
  background: var(--c-surface);
  border-radius: var(--r-lg);
  box-shadow: var(--e-3);
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.modal-header,
.modal-footer { padding: var(--s-5) var(--s-6); }
.modal-header { border-bottom: 1px solid var(--c-border); }
.modal-footer { border-top: 1px solid var(--c-border); display: flex; justify-content: flex-end; gap: var(--s-3); }
.modal-body { flex: 1; overflow-y: auto; padding: var(--s-6); }
```

Per-file `max-width` stays as it is (600px / 700px / 900px for `TasksModal`). `TasksModal` specifically: `z-index` 1000 → 2000, `width: 90%` → `width: 100%` + its existing `max-width`, `max-height: 85vh` → `90vh`, shadow → `var(--e-3)`.

**Do not extract a `BaseModal` component.** It is a tempting cleanup and it is out of scope — six more files of churn and a behavior-change risk in a change that is supposed to be visual.

## 4. i18n keys

Add to **both** `client/src/locales/en.js` and `client/src/locales/ja.js` under the existing `nav` namespace. Missing ja keys fall back to English silently, which is worse than an obvious break.

```js
// en.js
nav: {
  // …existing keys…
  reports: 'Reports',
  collapseSidebar: 'Collapse sidebar',
  expandSidebar: 'Expand sidebar',
  openMenu: 'Open menu'
}
```

```js
// ja.js
nav: {
  // …existing keys…
  reports: 'レポート',
  collapseSidebar: 'サイドバーを折りたたむ',
  expandSidebar: 'サイドバーを展開',
  openMenu: 'メニューを開く'
}
```

Existing nav keys, for reference: `overview`, `inventory`, `orders`, `finance`, `demandForecast`, `companyName`, `subtitle`.
