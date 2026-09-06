# Pattern Preference Register — 3R Assist

> Copied from Framework v1.5 Appendix A at Bootstrap (M0.4).
> Reviewed against the expected stack: Python backend, RAG pipeline, **PostgreSQL**
> (not SQLite — ADR-013), local embeddings model, Anthropic API, React/Vite frontend.
>
> **N/A entries** = not applicable to this stack.
> **Deviations** = require an ADR entry naming the standard being replaced and the gap.
> This file is updated whenever a pattern decision is made — not only at spec time.

---

## Application Architecture

**Default:** Layered — Presentation / Service / Repository / Data.

Escalate to **Event-driven** only if async decoupling is the core value proposition (not a performance optimization).

Escalate to **Microservices** only if independent deployment of components is a present, real requirement — not anticipated future scale.

> **3R Assist context:** The RAG pipeline (extraction → embedding → retrieval → ranking) maps naturally to a Service layer. No async decoupling requirement at MVP. Microservices: N/A.

---

## Module Boundaries

**Default:** Single Responsibility Principle per module; Dependency Inversion for wiring.

- Domain logic does not import infrastructure (databases, HTTP clients, file system) directly. These are injected.
- **Heuristic:** If a module is hard to unit test without a real database or network call, the boundary is wrong.

> **3R Assist context:** The LLM client (provider-agnostic `LLMAdapter`: llmcall / Ollama / stub) and the embedding model are infrastructure — they must be injected into the extraction and retrieval services, not imported directly. This keeps both testable with mocks.

---

## Data Access

**Default:** Repository pattern — abstract the data source behind an interface. Domain logic calls the repository; the repository owns all query logic, ORM method calls, and database-specific types.

**Acceptable shortcut:** Active Record for simple CRUD apps with no meaningful domain logic. Must be declared explicitly if chosen.

> **3R Assist context:** Two data domains:
> 1. **Methods database** (curated alternatives) — Repository pattern with **raw SQL over asyncpg** (no ORM; see ADR-006). Query logic (semantic search + structured filters) is encapsulated in `app/repositories/methods.py`.
> 2. **User data** (accounts, query history, feedback) — simple repositories (`users.py` is currently a stub; auth not wired). Active Record acceptable given simple CRUD nature.

---

## API Design (HTTP)

**Default:** REST + OpenAPI spec — resource-oriented URLs, HTTP verb semantics, consistent error envelope defined once.

Escalate to **GraphQL** if client-driven query flexibility is the core value proposition.

Escalate to **gRPC** if schema enforcement and binary performance are critical.

In all cases: define the contract before writing any handler code.

> **3R Assist context:** REST is appropriate. GraphQL: N/A. gRPC: N/A. API contracts are defined in `spec.md` §2.11; OpenAPI is auto-generated from FastAPI route type annotations. Error envelope: `{error: {code, message, detail}}`.

---

## Frontend State Management

**Default:** Escalate progressively.

```
Local component state → Context API / Zustand → Redux / Jotai
```

Start at local state. Move up only when complexity justifies it.

> **3R Assist context:** Frontend is React 19 + Vite (ADR-003). State stays at local component level and flows through router `location.state`; no global store is used. Escalate only when a real pain point appears.

---

## Error Handling

**Default:** Typed error returns (Result / Either pattern, or typed union returns) inside domain and service layers. Exceptions permitted only at I/O boundaries.

> **3R Assist context:** LLM extraction failures and retrieval misses are expected, not exceptional — they must be typed return values, not exceptions, so the service layer can handle them gracefully (e.g., return "no results found" rather than a 500).

---

## Configuration

**Default:** 12-Factor App — all config via environment variables.

- `.env.example` committed with every required key documented and no values.
- No hardcoded config values anywhere in source.
- Secrets managed via GitHub Secrets / Doppler / Infisical — never committed.

> **3R Assist context:** `.env.example` initialized at M0 with known keys. See `.env.example`.

---

## Async

**Default:** async/await throughout.

Event emitters only for genuinely event-driven flows. Callbacks only when wrapping legacy APIs.

> **3R Assist context:** LLM and embedding calls are I/O-bound — async/await is correct. No event emitter use anticipated at MVP.

---

## Testing

**Default:** Test pyramid — unit > integration > E2E (more units, fewer E2E).

Within tests: AAA (Arrange-Act-Assert) structure, one assertion concept per test. Test observable behavior, not implementation details.

> **3R Assist context (Minimal tier):** CI is optional per ADR-001. Manual smoke-test script is the baseline (`backend/scripts/smoke_test.py`). Testing framework: **pytest**; live LLM tests behind the `@pytest.mark.live` marker; frontend uses Node's built-in test runner (`npm test`). Priority test surfaces: parameter extraction (H3), retrieval ranking, feedback submission.

---

## UI Components

**Default:** Composition over inheritance. Co-locate state with the component that owns it.

> **3R Assist context:** No dedicated designer (noted in proposal). AI-assisted mockups in M2.5. Component inventory in `/design/components.md` before M3 implementation.

---

## External Integrations (Anti-Corruption Layer)

**Default:** Define an interface in your domain that represents what you need from the external service — not what the service provides. Implement an adapter that translates between the two.

> **3R Assist context:** Two external integrations requiring ACL:
> 1. **Anthropic API** — the domain needs "extracted protocol parameters," not raw LLM message objects. The adapter translates.
> 2. **Data sources (ALT Web, ECVAM, OECD)** — the domain needs a normalized `Method` entity. The ingestion pipeline is the adapter; external data shapes must not leak into the domain model.

---

## GoF Patterns — Use When the Problem Fits

| Pattern | Use when | 3R Assist applicability |
|---|---|---|
| **Strategy** | Multiple interchangeable implementations | LLM provider (Anthropic / fallback); embedding model (local / API) — **applicable** |
| **Observer / Event** | Components react to state changes without tight coupling | N/A at MVP |
| **Factory** | Object creation logic is complex or varies by context | Method entity construction from heterogeneous sources — **possibly applicable** |
| **Decorator** | Add behavior without modifying existing objects | Retry / logging on LLM calls — **applicable** |
| **Command** | Operations need to be queued, undone, logged, or retried | N/A at MVP |
| **Repository** | See Data Access above | **Applicable** |
| **Adapter** | See Anti-Corruption Layer above | **Applicable** |

---

## YAGNI

Do not build for requirements that do not exist yet.

> **3R Assist context:** High-risk YAGNI temptations for this project:
> - Building a real-time PubMed ingestion pipeline (Phase 4 feature)
> - Multi-tenant / organization-level accounts (not in MVP)
> - Configurable LLM provider switching (over-engineering for MVP with a single provider)
> - Caching layers before any performance measurement
>
> Invoke YAGNI by name in prompts: *"Before implementing, verify this passes the YAGNI check in patterns.md."*

---

## Performance Optimization

**Default:** Measure before optimizing. No caching, denormalization, or query restructuring without a profiling result or observed regression.

> **3R Assist context:** Embedding generation is the most likely performance hotspot. Do not pre-optimize. If the 60-second success threshold is missed during pilot, profile first.

---

*Initialized at M0. Updated throughout M2 Phase B, M3, and M4.2.*
