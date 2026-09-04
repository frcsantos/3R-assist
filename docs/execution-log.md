# Execution Log — 3R Assist

> **Scope:** Narrative deviation rationale only — what changed from the plan, why, and what it cost.
> Status tracking belongs in your task tool (Linear, GitHub Projects, etc.).
> Started at Module 3. Archived at end of each cycle (M4/M5).

---

## M0 — Bootstrap

- Scaffold initialized from Framework v1.5.
- ADR tooling: plain markdown ADRs in `decisions.md` (see ADR-000).
- Scope tier declared: Minimal (see ADR-001).
- Permitted compressions logged: CI optional (smoke-test acceptable); M2.5 passes B/C optional; formal M5 replaceable with 3 informal tests if Fórum Animal network doesn't yield 5 users.
- `patterns.md` initialized and reviewed against expected stack.

## M2 — Specification

- Phases A–D complete.
- ADR-002 to ADR-007 registered (stack, architecture, data access).
- H2 and H5 remain Untested — Phase 1 development blockers.

## M2.5 — UI Design

- Pass A (structure) complete: 6 screens mapped, navigation shape defined.
- Pass B (visual) complete: token system, S1 and S3 in high fidelity.
- Pass C (interactive prototype) omitted — Minimal tier compression; recorded here per ADR-001.

**Spec Sync (M2.5.6) — 5 divergences resolved:**

| ID | Divergence | Resolution |
|---|---|---|
| D1 | S6 not in nav in spec | spec.md 2.3 updated; ADR-008 created |
| D2 | Export visible-but-locked for anonymous not specified | spec.md 2.2 F10 and 2.3 S3 updated; ADR-009 created |
| D3 | Confidence indicator on S2 not in spec | spec.md 2.3 S2 updated; ADR-010 created |
| D4 | Reduced opacity for cards ≤ 65% not in spec | spec.md 2.2 F04 and 2.3 S3 updated; ADR-011 created |
| D5 | "Suggest method" link on S3 not in spec | spec.md 2.3 S3 updated; ADR-012 created |

1 elaboration (no ADR): S3 horizontal filter bar vs S4 sidebar distinction — spec was silent, not contradicted.

**Open question before M3:** visual tone (warm off-white vs. plain white) — show Ethos templates (`entrada_de_protocolo`, `relat_rio_de_an_lise`) to 2–3 researchers/CEUAs in Karynn's network before implementing.

## M2.5 — Ethos theme adoption

- **Decision:** Ethos Research System adopted as canonical visual base (replaces Pass B `pass-b-visual.html` for implementation).
- **Token sync:** `docs/design-tokens.md` reconciled with `UI design templates/Ethos Theme/ethos_research_system/DESIGN.md`. Implementation artifacts: `design/tokens.css`, `design/ethos-theme.css` (Tailwind v4), `design/tailwind.preset.js` (reference).
- **Component inventory:** `design/components.md` — 4 Ethos templates mapped to S1–S6 with P0–P4 priority.
- **Frontend scaffold:** `frontend/` — Vite + React + Tailwind v4, Ethos tokens wired, preview components (`TopNav`, `ResultCard`).

**Token deltas from Pass B:** `--bg` `#F7F6F2` → `#faf9f5`; `--text-2` `#6B6960` → `#494740` (Ethos `on-surface-variant`). Legacy aliases preserved in `design/tokens.css`.

## M3 — Backend scaffold

- `backend/` FastAPI app scaffolded per spec 2.8 (layered: routes → services → adapters/repositories).
- Working endpoints: `GET /health`, `POST /analyze` (stub LLM when `ANTHROPIC_API_KEY` unset).
- ~~SQLite schema in `app/db/schema.sql`; auto-init on startup.~~ Superseded — PostgreSQL only (see M3 Database / ADR-013).
- Smoke test: `backend/scripts/smoke_test.py`. Unit tests: `backend/tests/`.

## M3 — Database (methods + application tables)

**Infrastructure deviation (current):** **PostgreSQL only** — SQLite/Turso fully replaced (ADR-013 supersedes ADR-004). Dev and prod use PostgreSQL (Neon branch or local instance / Neon Vercel Postgres). Driver: `asyncpg`. Triggers: Vercel deployment context; single-driver simplicity; JSONB and pgvector path for Phase 3. Cost impact: zero — Neon free tier. Any earlier M3 notes about SQLite schema files are historical only.

**Env var changes:** `TURSO_URL` and `TURSO_AUTH_TOKEN` removed. Single `DATABASE_URL` replaces both. `.env.example` updated.

**Methods database — source reconciliation:**

Two CONCEA normative resolutions and corresponding OECD documents reviewed (RN 18/2014 + OECD GD 129/2010). Key findings:

| Finding | Impact |
|---|---|
| RN 18/2014 recognizes 17 methods across 7 endpoints | 10 methods added to seed (TG 435, 438, 460, 428, 429, 442A, 442B, 420, 423, 425) |
| 5 jurisdiction corrections required | `niceatm-cytotox`: `international` → `both` (GD 129 named in RN 18 Art. 2 VI-d); TG 492 + TG 442C/D/E: `both` → `international` (postdate RN 18) |
| TG 420/423/425 are in vivo refinement methods, not replacements | `category_3r = 'refinement'`; included because RN 18 recognizes them and CEUAs evaluate protocol humaneness |

**Parameter model defined** (`docs/parameter_model.md`):
- 7 extracted fields; 4 used for matching (`endpoint_category`, `route`, `application_area`, `procedure_text`), 3 display-only (`species`, `n_animals`, `regulatory`).
- `routes_applicable` column added to `methods` table — enables route-based pre-filtering in `RetrievalService`.
- Minimum Results Rule: relax filters if fewer than 3 methods pass, to preserve the binary success criterion (≥3 recommendations per query).

**Migration artifacts:**
- `db/migrations/001_initial.sql` — `methods` + `method_keywords` tables, 25 methods, 117 keywords. All entries `active = FALSE` pending Karynn review.
- `db/migrations/002_app_tables.sql` — `users`, `magic_link_tokens`, `queries`, `feedback`, `suggestions`.
- `scripts/embed_methods.py` — rewritten for `asyncpg`; reads `DATABASE_URL`; registers JSONB codec.
- `docs/karynn_review_checklist.md` — per-method review checklist; Karynn sets `active = TRUE` after confirming `[VERIFY]` fields.

**Assumption status update:**

| # | Prior status | Current status |
|---|---|---|
| H2 | Untested | **Partially addressed** — Karynn's source analysis confirms coverage for 8 endpoints from RN 18 + ECVAM DB-ALM. Formal check (download DB-ALM, count entries, verify terms of use) still required before declaring Tested. |
| H5 | Untested | **Partially addressed** — curation of 25 methods from 2 documents completed. Time-per-entry estimate needed to project full database maintenance cost. Formal check still required. |

H2 and H5 remain formally Untested in `assumption-log.md` until the structured check (§13.2) is completed. Do not mark as Tested based on partial evidence.

**Open items before methods go live:**
- Karynn: complete `karynn_review_checklist.md` (confirm `[VERIFY]` fields, set `active = TRUE`)
- Karynn: confirm MAT jurisdiction (Farmacopeia Brasileira chapter reference)
- Karynn: decision on TG 420/423/425 inclusion (in vivo refinement vs. out of scope)
- Leo: rewrite `db/connection.py` for `asyncpg`; remove Turso dependency from `requirements.txt`
- Both: process remaining 4 CONCEA RNs — TG 442C/D/E and TG 492 jurisdiction may change

---

*M3+ entries added during development.*

## M3+ — Phase 1 core pipeline (extraction → search → results)

**Implemented (2026):**

| Area | Change |
|---|---|
| Extraction contract | ADR-015–018 synced: `study_type` → lookup; per-field `{field}_confidence`; `AnimalCounts`; prompt §9 aligned |
| Lookup table §4.1 | Subacute blocklist; EVEIT / ex vivo eye / BCOP → `ocular_irritation` |
| Live reliability tests | 9 protocol fixtures; `@pytest.mark.live`; weighted scoring |
| `POST /search` | ADR-019: retrieval after S2; filter relaxation |
| `POST /analyze` | Extraction only |
| S2 UI | Experiment tabs; protocol side panel; per-field confidence + evidence |
| S3 UI | Live `ResultCard` results; experiment tabs; Match score; OECD on regulatory link |

**Still open for pilot:** methods `active = TRUE`; S3 export / F11 query ratings / suggest links; `QueryRepository`; H1/H2/H5 formal checks.

---

## M3+ — Schema evolution, Explore, general feedback (2026-08)

| Area | Change |
|---|---|
| Methods columns | `animal_use`, `test_system`, localized `*_rationale`, `validation_status` on methods (migrations 037–042) |
| Feedback split | `feedback` → `query_feedback` (F11); new `feedback` for general comments (043–044); ADR-024 |
| Explore (S4) | `/explore` Methods / Regulations / Documents; `/buscar` redirect; nav + Glossary / Info |
| F11b UI | Explore card ! → `FeedbackModal` → `POST /feedback` |
| Result cards | Detail rows: animal use, test system, endpoint, routes, study domain |

**Still open for pilot:** methods `active = TRUE`; S3 export / F11 ratings / suggest; `QueryRepository`; H1/H2/H5 formal checks.
