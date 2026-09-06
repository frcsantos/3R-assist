# 3R Assist

AI-powered decision-support tool for researchers and ethics committees to discover validated alternatives to animal use in scientific research.

## What it does

Accepts a free-text description of an experimental protocol → extracts core parameters → returns ranked recommendations classified under the 3Rs framework (Replacement / Reduction / Refinement), with jurisdictional validity indicators and links to primary sources.

## Team

| Role | Contributor | Commitment |
|---|---|---|
| Animal ethics & welfare, data curation | Karynn | 4h/week |
| Software development & AI integration | Leo | 4h/week |
| RAG production, b_2 data ingestion | Felipe | 4h/week |

Institutional backing: **Fórum Animal**

## Scope tier

**Minimal (MVP)** — end-to-end product sufficient for pilot validation with 5–10 researchers/CEUA members. See `spec.md` for full scope definition.

## Binary success definition

> A researcher with no prior knowledge of alternative methods describes a real protocol in free text, and receives at least 3 relevant recommendations with verifiable source references in under 60 seconds.

## Project artifacts

| File | Purpose |
|---|---|
| `docs/spec.md` | Full product specification |
| `docs/decisions.md` | Architecture Decision Records (ADR log) |
| `docs/patterns.md` | Design pattern preference register |
| `docs/assumption-log.md` | Critical assumptions and test status |
| `docs/dev-plan.md` | Phase-by-phase development plan |
| `docs/execution-log.md` | Narrative deviation log (updated during development) |
| `docs/tables.md` | Database schema reference |
| `docs/info.md` | Living product + how-to-run summary |
| `/design/` | Tokens, Ethos theme, component inventory |
| `/notebooks/` | LLM experiment notebooks |

## Status

🟢 Phase 1 core pipeline live (analyze → parameters → search → results). Explore catalogue + general feedback shipped. PubMed literature search module + admin curation tooling shipped. Methods remain inactive pending Karynn review before pilot.

---

*Framework: AI-Assisted Project Development v1.5*
