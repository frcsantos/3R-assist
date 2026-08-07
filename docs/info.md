# 3R Assist — Info

## General info

### Concept

**3R Assist** is an AI-powered decision-support tool for researchers and Animal Research Ethics Committees (CEUAs) to discover validated alternatives to animal use.

A user describes an experimental protocol in free text (Portuguese or English). The system extracts core parameters, matches them against a curated methods database, and returns ranked recommendations classified under the **3Rs** (Replacement / Reduction / Refinement), with jurisdictional validity and links to primary sources.

**Core differentiator:** the tool analyzes the protocol *before* searching. Existing resources (ALT Web, ECVAM TSAR, OECD guidelines) require the researcher to already know the relevant vocabulary.

**Binary success definition:** a researcher with no prior knowledge of alternative methods describes a real protocol in free text and receives at least 3 relevant recommendations with verifiable source references in under 60 seconds.

### Team

| Role | Contributor | Commitment |
|---|---|---|
| Animal ethics & welfare, data curation | Karynn | 4h/week |
| Software development & AI integration | Leo | 4h/week |

Institutional backing: **Fórum Animal**.

### Scope & current stage

**Scope tier:** Minimal (MVP) — end-to-end product for pilot validation with 5–10 researchers/CEUA members.

| Area | Status |
|---|---|
| Spec (Phases A–D) | Complete |
| UI design (Ethos theme) | Adopted; S1–S3 implemented |
| Backend (FastAPI + PostgreSQL) | Scaffolded; core pipeline live |
| Phase 1 pipeline | Extraction → parameter review → search → results |
| Methods database | 25 curated methods; `active = FALSE` pending Karynn review |
| Auth, history, export, feedback | Specced; not yet fully wired for pilot |

**Still open before pilot:** activate methods after review (`docs/karynn_review_checklist.md`); formal H1/H2/H5 assumption checks; export/feedback/suggest-method links on results.

Framework: AI-Assisted Project Development v1.5.

---

## How to use

### Product flow (end user)

1. **Analisar (S1)** — Paste a free-text protocol; submit.
2. **Parameters (S2)** — Review extracted fields, confidence badges, and evidence highlights; edit if needed; confirm.
3. **Results (S3)** — Browse ranked alternatives (3Rs class, Match %, jurisdiction, sources). Filter by 3Rs / jurisdiction when needed.
4. **Buscar (S4)** — Direct database search with structured filters (for users who already know what to look for).

Anonymous use is allowed. Accounts (magic link), query history, and export are for registered users when enabled.

### Local development

**Prerequisites:** Python 3.11+, Node.js, PostgreSQL (`DATABASE_URL`).

1. **Backend**
   - Copy `backend/.env.example` → `backend/.env` and set `DATABASE_URL`.
   - Create venv, install deps: `pip install -r requirements.txt`.
   - Run migrations: `python scripts/migrate.py` (from `backend/`).
   - Start: `run_backend.bat` or `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
   - Leave LLM API keys empty to use the stub adapter (no API cost).

2. **Frontend**
   - Copy `frontend/.env.example` if needed.
   - Start: `run_frontend.bat` or `npm run dev` in `frontend/` (default Vite port, e.g. `http://localhost:5173`).

3. **Smoke / tests**
   - Backend smoke: `backend/scripts/smoke_test.py`.
   - Unit tests: `pytest` under `backend/tests/` (live LLM tests marked `@pytest.mark.live`).

### Key docs map

| File | Purpose |
|---|---|
| `docs/spec.md` | Product specification |
| `docs/decisions.md` | Architecture Decision Records (ADRs) |
| `docs/patterns.md` | Design pattern preferences |
| `docs/parameter_model.md` | Extraction & matching fields |
| `docs/assumption-log.md` | Critical hypotheses and test status |
| `docs/execution-log.md` | Deviations from plan |
| `docs/dev-plan.md` | Phase-by-phase development plan |
| `docs/glossary_en.md` / `glossary_pt.md` | Domain terminology |
| `docs/karynn_review_checklist.md` | Methods curation checklist |
| `design/` | Tokens, Ethos theme, component inventory |

---

## Conventions

### Architecture & code

- **Layered stack:** Presentation (routes / React) → Service → Repository / Adapter → Data.
- **Backend:** Python + FastAPI; domain logic does not import infrastructure directly — inject LLM and DB clients.
- **Data:** PostgreSQL only (`DATABASE_URL`, `asyncpg`). Repository pattern for methods; Active Record acceptable for simple user CRUD.
- **API:** REST + OpenAPI; typed/expected failures in services (e.g. extraction miss), not bare 500s.
- **Frontend:** React + Vite + Tailwind (Ethos tokens). Prefer local component state; escalate only when needed.
- **Embeddings:** `sentence-transformers` / `all-MiniLM-L6-v2`; `SEMANTIC_RANKING=false` uses filter/keyword ranking (MVP default).

### Product & UX

- Nav primary items only: **Analisar** and **Buscar**. Method suggestion (S6) is via results/footer, not primary nav.
- S2 is a **gate** — search runs only after the user confirms/edits parameters.
- Multi-experiment protocols use tabs on S2/S3 (`experiments[]`).
- Extraction: LLM returns `study_type` + evidence; app maps to `endpoint_category` via lookup (no LLM inference for DB category).
- Result cards with Match ≤ 65% render at reduced opacity.
- UI copy is bilingual (PT/EN).

### Domain language

Use glossary terms consistently (see `glossary_en.md` / `glossary_pt.md`):

| Term | Meaning |
|---|---|
| **Endpoint** | Biological effect / measurable response the study evaluates (not the substance or method) |
| **Method** | Discrete, validatable technique for one `endpoint_category` |
| **Methodology** | Broader experimental strategy (may combine methods) |
| **Route** | How the test substance contacts the biological system; `null` = any route |

Prefer `study_domain` over the deprecated name `application_area` (ADR-020).

### Process

- **Scope:** Minimal tier — keep scope under the ~8h/week team ceiling; compressions go in `execution-log.md`.
- **Decisions:** Significant architecture/UX choices → ADR in `decisions.md` (`ADR-NNN`).
- **Assumptions:** Track in `assumption-log.md`; do not mark Tested on partial evidence.
- **Curation:** Karynn owns methods quality; seed entries stay inactive until checklist review.
- **Secrets:** Never commit `.env`; use `.env.example` as the contract.
- **Commits / PRs:** Only when explicitly requested; follow repo git safety rules.
