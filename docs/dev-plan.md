# dev-plan.md — 3R Assist

> Status: � Phase 1 core pipeline + Explore + PubMed module implemented.
> Input: `spec.md` + `decisions.md` + `patterns.md` + `/design/`
> Detailed status and deviations live in `execution-log.md`; assumptions in `assumption-log.md`.

---

## 3.0 Development Prerequisites

- [x] Testing framework selected (pytest; live LLM tests behind `@pytest.mark.live` marker)
- [x] Smoke-test script created (`backend/scripts/smoke_test.py`; CI optional per ADR-001)
- [x] `.env.example` committed with all required keys (`backend/.env.example`, `frontend/.env.example`)
- [x] Secrets management approach confirmed (env vars only; no committed secrets)
- [ ] Environments confirmed accessible (dev + staging/prod) — Neon DB confirmed; Vercel/Render deploy not yet verified end-to-end
- [x] `patterns.md` reviewed before writing implementation code

---

## Phase 1 — Core pipeline ✅ implemented

**Goal:** Free-text protocol → extracted parameters → ranked 3R alternatives with sources.
**Status:** Live locally. Methods seed remains `active = FALSE` pending Karynn review.

### Tasks

- [x] `POST /analyze` — LLM extraction (two-stage `study_type` → `endpoint_category`)
- [x] `POST /search` — retrieval with endpoint/route filters + Minimum Results Rule
- [x] S1–S3 frontend: input, parameter review (confidence + evidence), ranked results
- [x] Multi-experiment protocols (tabs on S2/S3, parallel search)
- [x] Explore catalogue (S4) + general feedback (F11b)
- [x] Curation support: admin DB browser + LLM extraction toolchain
- [ ] Karynn review of 25 seeded methods → `active = TRUE` (`docs/karynn_review_checklist.md`)

### Tests

- [x] Unit tests for extraction, retrieval, search, catalogues (`backend/tests/`)
- [x] Live extraction reliability suite (`test_extraction_reliability.py`, `@pytest.mark.live`)
- [ ] Pilot protocol (5 researchers) — H1/H2/H3/H4/H5 evidence

### Success Criteria

- [x] Binary success definition achievable locally (≥3 relevant recommendations < 60s)
- [ ] Verified with real researchers in pilot (Phase 3)

---

## Phase 1.5 — Literature search (PubMed) ✅ implemented

**Goal:** For each experiment, surface supporting literature and a necessity verdict.

- [x] PubMed ingestion pipeline (`scripts/run_pubmed_ingestion.py`, pgvector)
- [x] `POST /pubmed/analyze` + `GET /pubmed/status`
- [x] Frontend: `/literature` (from Results) + `/literature-search` (standalone)

---

## Phase 2 — Production web app (months 3–6) — in progress

**Goal:** Full MVP feature set deployed; internal testing complete.

- [ ] Deploy frontend (Vercel) + backend (Render) + Neon production branch
- [ ] Auth (magic link, F08) — routes not yet implemented
- [ ] Query history (F09) — `QueryRepository` deferred; `queries` table exists
- [ ] Export PDF/CSV (F10) — `export.py` stub; admin CSV export only
- [ ] Query ratings UI (F11) — table + contract reserved
- [ ] Method suggestion form (F12)
- [ ] Admin panel access control (currently open)

---

## Phase 3 — Pilot (months 6–9)

- 5–10 users complete pilot protocol; ≥3/5 rate recommendations relevant
- Formal H1/H2/H5 checks (see `assumption-log.md`)

## Phase 4 — Iteration & expansion (months 9–12)

- Expanded database (F15); comparison (F17); profiles (F18); full-scope features per `spec.md` §2.15

