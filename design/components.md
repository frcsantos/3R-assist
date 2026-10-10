# Component Inventory — Assist3R (Ethos Theme)

> Extracted from Ethos HTML templates. Maps to spec screens S1–S6.
> Implementation target: `frontend/src/components/`
> Reference: `patterns.md` → UI Components

---

## Template → Screen mapping

| Ethos template | Primary screens | Notes |
|---|---|---|
| `landing_page_assist3r` | Marketing / pre-auth | Hero, features, pricing — not in MVP nav |
| `entrada_de_protocolo_assist3r_light` | **S1** Input, partial S2 flow | Protocol textarea, lang toggle, 3R explainer |
| `dashboard_principal_assist3r_light` | **S5** History, hub | Summary cards, protocol table, resources |
| `relat_rio_de_an_lise_assist3r_light` | **S2** Params, **S3** Results | Extracted params table, recommendation cards, export |

S4 (Search) has no dedicated Ethos template — reuse filter patterns from Pass A + result cards from S3.

---

## Layout

### `AppShell`
- **Source:** all templates
- **Structure:** fixed top nav (64px) + optional sidebar + main content
- **Props:** `variant: 'marketing' | 'app' | 'workspace'`, `sidebar?: boolean`
- **Screens:** all
- **Priority:** P0

### `TopNav`
- **Source:** `dashboard_principal`, `entrada_de_protocolo`
- **Elements:** logo, primary links (Analisar | Buscar), search (dashboard only), auth CTA
- **Active state:** `border-b-2 border-primary pb-1 font-medium`
- **Height:** `h-nav` (64px)
- **Screens:** S1–S6
- **Priority:** P0

### `Sidebar` (workspace variant only)
- **Source:** `entrada_de_protocolo`
- **Width:** 256px (`w-64`), `surface-container-low`, right border
- **Note:** Ethos uses sidebar in protocol entry; spec reserves sidebar for S4 search only. **Defer sidebar in MVP** unless S4 is implemented — use single-column TopNav layout per Pass A.
- **Priority:** P2 (S4)

### `PageHeader`
- **Source:** `dashboard_principal`, `relat_rio_de_an_lise`
- **Elements:** breadcrumb (optional), title, subtitle/metadata, action buttons
- **Screens:** S2, S3, S5
- **Priority:** P1

---

## Navigation & flow

### `Breadcrumb`
- **Source:** `relat_rio_de_an_lise` — `History > Analysis`
- **Typography:** `font-metadata text-metadata`, chevron separator
- **Screens:** S2, S3, S5
- **Priority:** P2

### `StepIndicator`
- **Source:** `entrada_de_protocolo` — Input → Analysis → Report
- **States:** active (filled circle), inactive (outlined), connector line
- **Screens:** S1 → S2 → S3 flow
- **Priority:** P1

---

## Forms & input

### `ProtocolTextarea`
- **Source:** `entrada_de_protocolo`
- **Shell:** white card, `border-subtle`, label `label-caps` uppercase
- **Inner:** `surface-container-low` textarea, `font-monospace-data`, char counter bottom-right
- **Screens:** S1
- **Priority:** P0

### `LangToggle`
- **Source:** `entrada_de_protocolo`
- **Structure:** pill track (`surface-container-high`) with EN/PT buttons inside input shell
- **Active pill:** white bg (no shadow in Ethos flat spec — remove `shadow-sm` from template)
- **Screens:** S1
- **Priority:** P0

### `FileDropZone`
- **Source:** `entrada_de_protocolo`
- **Style:** dashed `border-emphasis`, hover → `surface-container-low` + `border-primary`
- **Note:** optional for MVP if text-only input is sufficient
- **Priority:** P3

### `EditableField` / `ParameterRow`
- **Source:** `relat_rio_de_an_lise` table rows
- **Layout:** label (`small-label`) + editable value + confidence (`monospace-data`)
- **Screens:** S2
- **Priority:** P0

### `SearchInput`
- **Source:** `dashboard_principal`
- **Style:** `surface-container-lowest`, icon left, `rounded-lg`, focus ring avoided per Ethos
- **Screens:** S4, dashboard
- **Priority:** P2

---

## Actions

### `Button` (variants)
| Variant | Classes (Tailwind) | Source |
|---|---|---|
| `primary` | `bg-primary text-on-primary rounded-md hover:opacity-90` | all |
| `secondary` | `border border-border-emphasis bg-surface-container-lowest hover:bg-surface-container` | report export bar |
| `ghost` | `text-on-secondary-container hover:text-primary` | table "View" links |
| `icon` | `p-2 rounded-full hover:bg-surface-container-high` | settings, account |

- **Priority:** P0

### `FilterBar` (horizontal)
- **Source:** Pass A S3 (not in Ethos templates)
- **Note:** horizontal chips above results — distinct from S4 sidebar filters
- **Screens:** S3
- **Priority:** P1

---

## Data display

### `SummaryCard`
- **Source:** `dashboard_principal`
- **Structure:** label (`label-caps`), icon, large number (`monospace-data` 3xl), trend/metadata
- **Screens:** S5 dashboard
- **Priority:** P2

### `DataTable`
- **Source:** `dashboard_principal`, `relat_rio_de_an_lise`
- **Header:** `surface-container-low`, `label-caps`
- **Rows:** `divide-border-subtle`, hover `surface-container-low` or `background`
- **Screens:** S2 (params), S5 (history)
- **Priority:** P1

### `ResultCard`
- **Source:** `relat_rio_de_an_lise` recommendation cards
- **Structure:**
  - Header: 3R badge + score or `open_in_new` icon
  - Title: `card-title`
  - Metadata rows: key/value with `border-b border-subtle`
  - Source link chips
- **States:** default, hover (`border-emphasis`), dimmed (`opacity-65` when score ≤ 65%)
- **Screens:** S3, S4
- **Priority:** P0

### `ProtocolSummaryCard`
- **Source:** `relat_rio_de_an_lise`
- **Grid:** 3-column metadata (date, study type, species)
- **Screens:** S3
- **Priority:** P1

### `InsightCallout`
- **Source:** `relat_rio_de_an_lise` — `bg-info-bg border-info-border`
- **Elements:** lightbulb icon, title, body with optional bold link
- **Screens:** S3
- **Priority:** P2

### `ResourceCard`
- **Source:** `dashboard_principal` sidebar
- **Structure:** icon box (semantic bg), title, description, tag chip
- **Screens:** S5
- **Priority:** P3

---

## Badges & status

### `ThreeRBadge`
- **Variants:** `replacement` | `reduction` | `refinement`
- **Style:** `px-2 py-0.5 rounded font-badge-button border` + semantic colors
- **Rule:** 1px border mandatory
- **Priority:** P0

### `JurisdictionBadge`
- **Variants:** `both` (info blue) | `intl-only` (neutral) | `brazil-only` (amber)
- **Source:** `design-tokens.md` jurisdiction table
- **Screens:** S3, S4
- **Priority:** P0

### `StatusBadge`
- **Source:** `dashboard_principal` table — "Replacement Found", "Under Review"
- **Variants:** 3R semantic or neutral (`surface-container-high opacity-65`)
- **Screens:** S5
- **Priority:** P2

### `ConfidenceIndicator`
- **Source:** spec S2 (ADR-010)
- **Display:** badge or label — "Alta confiança" / score aggregate
- **Screens:** S2
- **Priority:** P1

---

## Content blocks

### `ThreeRExplainer`
- **Source:** `entrada_de_protocolo` side panel
- **Structure:** 3 sections with icon box + title + description per R
- **Screens:** S1 (optional sidebar), help/modal
- **Priority:** P2

### `DraftSavedIndicator`
- **Source:** `entrada_de_protocolo` — progress bar + timestamp
- **Screens:** S1
- **Priority:** P3

---

## Feedback

### `Toast`
- **Source:** `dashboard_principal` snackbar
- **Style:** `bg-primary text-on-primary rounded-lg`, bottom center
- **Priority:** P3

### `EmptyState`
- **Source:** Pass A (no Ethos template)
- **Screens:** S3 no results, S5 no history
- **Priority:** P1

### `LoadingState`
- **Source:** spec (analysis in progress)
- **Screens:** S1 → S2 transition
- **Priority:** P1

---

## Marketing (pre-MVP / landing)

### `HeroSection`, `FeatureGrid`, `PricingTable`, `Footer`
- **Source:** `landing_page_assist3r`
- **Note:** defer until post-pilot if not needed for auth funnel
- **Priority:** P4

---

## Implementation order (M3)

```
P0 — AppShell, TopNav, Button, ProtocolTextarea, LangToggle,
     ThreeRBadge, JurisdictionBadge, ResultCard
P1 — StepIndicator, PageHeader, DataTable, EditableField,
     FilterBar, ProtocolSummaryCard, ConfidenceIndicator, EmptyState, LoadingState
P2 — Breadcrumb, SearchInput, InsightCallout, SummaryCard, StatusBadge, ThreeRExplainer
P3 — FileDropZone, ResourceCard, DraftSavedIndicator, Toast
P4 — Marketing components, Sidebar (S4)
```

---

## Shared utilities

| Utility | Purpose |
|---|---|
| `cn()` | className merge (clsx + tailwind-merge) |
| `scoreDimClass(score)` | returns `opacity-65` when score ≤ 65 |
| `threeRColorClass(type)` | maps R-type → Tailwind color tokens |

---

*Created at M2.5 Ethos adoption. Update when new screens are added or components diverge from templates.*
