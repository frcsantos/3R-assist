# Architecture Decision Records — 3R Assist

> ADR log. Every significant architectural, infrastructure, or pattern choice is recorded here.
> Format: `ADR-[NNN]`. Near-impossible decisions are flagged explicitly.
> Updated throughout M2, M2.5, M3, and M3 Database.

---

## ADR-000 — ADR Tooling Choice

**Decision:** Plain markdown ADRs maintained in this file (`decisions.md`).

**Context:** Needed to establish how architectural decisions are recorded before any project work begins (M0 requirement).

**Alternatives evaluated:**

| Option | Trade-off |
|---|---|
| `adr-tools` (CLI) | Generates one .md file per ADR in `/doc/adr/`; cleaner diffs but adds a CLI dependency |
| `Log4brains` | Browsable web UI; overkill for a 2-person Minimal-tier project |
| Inline in this file | Zero tooling; all ADRs in one place; works for a small decision set |

**Rationale:** Minimal scope tier + 2-person team. A single file is easier to reference in prompts and in conversation. If the decision count exceeds ~15, revisit and migrate to `adr-tools`.

**Reversibility:** Easy.

**Consequences:** All ADR entries live here. Each has a unique numeric ID. Search within this file to find decisions.

---

## ADR-001 — Scope Tier Declaration

**Decision:** **Minimal** tier.

**Context:** M0.3 Scope Gate — must be declared before any subsequent module work begins.

**Pattern baseline:** N/A (governance decision, not a software pattern).

**Rationale:** Combined 8h/week hard constraint makes architectural simplicity non-negotiable. The MVP must be complete enough to test the core hypothesis (free-text → relevant recommendations) but no larger. Permitted compressions per the framework:
- Skip M2.5 passes B and C (optional)
- Use a one-page spec *(not applied — detail is needed for the RAG pipeline)*
- Replace formal M5 with 3 informal tests *(deferred — aim for 5+ users given Fórum Animal network access)*
- M3.0 CI is optional — replace with a manual smoke-test script

All compressions applied must be documented in `execution-log.md`.

**Reversibility:** Costly (graduating to Standard tier requires adding skipped artifacts and CI).

**Consequences:** Security findings logged in `assumption-log.md` as known risks, not as ADRs, until the project graduates to Standard tier.

---

## ADR-002 — Backend: Python 3.11 + FastAPI

**Decision:** Python 3.11 + FastAPI.

**Context:** Backend language and framework selection (M2.5 Stack).

**Pattern baseline:** `patterns.md` → Application Architecture (Layered).

**Alternatives:** Node.js + Hono (single JS runtime); Django (more batteries, higher overhead).

**Rationale:** `sentence-transformers`, `anthropic`, and the broader ML ecosystem are Python-native. FastAPI is async by default, generates OpenAPI specs automatically, and has minimal boilerplate. Django adds unnecessary overhead for an API-only backend. Node.js would require a separate ML inference service, adding complexity.

**Reversibility:** Costly (full backend rewrite).

**Consequences:** Frontend and backend are different languages — no code sharing. Acceptable given the clear boundary between API and SPA.

---

## ADR-003 — Frontend: React 18 + Vite

**Decision:** React 18 + Vite, deployed as a static SPA on Vercel.

**Context:** Frontend framework selection (M2.5 Stack).

**Pattern baseline:** `patterns.md` → Frontend State Management.

**Alternatives:** Next.js (SSR/full-stack on Vercel); SvelteKit (lighter bundle, smaller ecosystem).

**Rationale:** Static SPA on Vercel requires no server; reduces infrastructure surface. React ecosystem covers all MVP requirements. Next.js SSR adds deployment complexity with no meaningful benefit given the backend is a separate FastAPI service. Vite is fast and well-supported.

**Reversibility:** Costly.

**Consequences:** CORS configuration required between Vite SPA and FastAPI backend. i18n handled client-side via `react-i18next`.

---

## ADR-004 — Database: SQLite (dev) + Turso (prod) ⚠️ SUPERSEDED by ADR-013

**Decision:** ~~SQLite file for local development; Turso (libSQL) for production.~~

**Superseded by ADR-013.** Retained for history.

**Original rationale:** Turso is SQLite-compatible (libSQL fork), free tier supports the MVP scale, and preserves local SQLite semantics for development.

**Why superseded:** Vercel Postgres (Neon) eliminates the two-driver complexity (sqlite3 locally, libsql-client in prod) and provides the same zero fixed cost constraint. The migration to PostgreSQL was triggered during M3 database work when the additional capabilities (JSONB, BOOLEAN, pgvector path for Phase 3) justified the switch.

---

## ADR-005 — Embeddings: sentence-transformers (local, all-MiniLM-L6-v2)

**Decision:** Local `sentence-transformers` model (`all-MiniLM-L6-v2`, 384 dimensions).

**Context:** Embedding model for semantic similarity between protocol descriptions and curated methods.

**Pattern baseline:** `patterns.md` → External Integrations (ACL); GoF Strategy (swappable provider).

**Alternatives:** OpenAI `text-embedding-3-small` (API cost per call); Cohere embed (API cost); larger local models (higher accuracy, higher resource use).

**Rationale:** Zero variable cost per query. `all-MiniLM-L6-v2` is well-benchmarked for semantic similarity. At 10–20 methods, embedding quality differences between models are unlikely to be decisive. The `EmbedderAdapter` ACL means the model can be swapped without touching the service layer.

**Reversibility:** Easy (swap the adapter implementation).

**Consequences:** Model download (~90MB) must happen at Render build time, not at request time.

---

## ADR-006 — Data Access: Repository for Methods, Active Record for User CRUD

**Decision:** Repository pattern for the Methods domain. Active Record for User, Query, Feedback, and Suggestion entities.

**Context:** Data access pattern selection (M2.6).

**Pattern baseline:** `patterns.md` → Data Access.

**Rationale:** The Methods domain has meaningful query logic (cosine similarity, multi-filter search, embedding management) that warrants encapsulation. User/auth/feedback entities are simple CRUD — Active Record is explicitly permitted by `patterns.md` in this case. Applying Repository to all entities at MVP would be premature abstraction (YAGNI).

**Reversibility:** Easy to promote Active Record entities to Repository later.

**Consequences:** `MethodRepository` is the only Repository interface. All other data access uses SQLAlchemy ORM models directly.

---

## ADR-007 — Layered Architecture with Dependency Inversion at Service/Adapter boundary

**Decision:** Strict Layered architecture; `ExtractionService` and `RetrievalService` receive adapter instances via constructor injection (manual injection, no DI container).

**Context:** Module boundary design (M2.9).

**Pattern baseline:** `patterns.md` → Module Boundaries.

**Rationale:** The two external I/O dependencies (Anthropic API, sentence-transformers) must be injectable to keep services unit-testable. This directly enables testing assumption H3 (extraction precision) — the highest-risk assumption in the project — with a mock LLM adapter.

**Reversibility:** Easy.

**Consequences:** Route handlers instantiate adapters and inject them into services. No DI container at MVP (YAGNI).

---

## ADR-008 — S6 (Method Suggestion) not in primary navigation

**Decision:** S6 is not accessible from the primary navigation bar. It is reached via a "Suggest method not listed" link at the bottom of S3 and a footer link.

**Context:** M2.5 Spec Sync — design diverged from spec, which was silent on nav placement.

**Pattern baseline:** N/A (navigation architecture decision).

**Rationale:** The primary nav has exactly two items: Analisar and Buscar. These represent the two use cases that need zero friction — a researcher who arrives with a protocol, and one who already knows what to look for. S6 is a contribution flow, not a discovery flow — placing it in the primary nav would give it prominence it doesn't merit and add visual complexity to the nav without commensurate value. The S3 placement is contextually correct: a researcher who just received results and finds a gap is the ideal person to suggest a method.

**Reversibility:** Easy.

**Consequences:** S6 is harder to find on first use. Acceptable — method suggestion is a power-user action, not a primary job-to-be-done.

---

## ADR-009 — Export visible-but-locked for anonymous users

**Decision:** The PDF/CSV export button (F10) is rendered and visible on S3 for anonymous users, but clicking it triggers a registration prompt rather than downloading the file.

**Context:** M2.5 Spec Sync — spec said "registered users only" without specifying the anonymous UX.

**Pattern baseline:** N/A (UX interaction pattern).

**Rationale:** Two alternatives were considered: (a) hide the button entirely for anonymous users; (b) show but lock. Option (a) removes a registration incentive and leaves anonymous users unaware that export exists. Option (b) surfaces the feature's value at the moment a user would want it, then converts the friction into a registration motivation. The risk is frustration if the prompt feels like a bait-and-switch — mitigated by the anonymous bypass being clearly visible on S1 (users who choose anonymous know the trade-off upfront).

**Reversibility:** Easy.

**Consequences:** Frontend must check auth state before triggering download. Backend export endpoints remain auth-required — no change to API contracts.

---

## ADR-010 — Confidence indicator on S2 (parameter review screen)

**Decision:** S2 displays a confidence indicator (High / Medium / Low) in the screen header, derived from the LLM extraction response.

**Context:** M2.5 Spec Sync — design added this element; spec 2.3 S2 did not include it.

**Pattern baseline:** N/A (UI element).

**Rationale:** The `POST /analyze` endpoint already returns `"confidence": "high"|"medium"|"low"` (see 2.11 interface contract). Surfacing this on S2 costs nothing technically and gives the user a signal about whether to trust the extraction or scrutinize the fields more carefully. A "Low confidence" indicator makes it immediately obvious why a field is blank or strange — reducing the cognitive load of deciding whether to correct.

**Reversibility:** Easy (remove the indicator element).

**Consequences:** Frontend must render the confidence value from the `/analyze` response. No backend changes.

---

## ADR-011 — Low-score result cards at reduced opacity

**Decision:** Result cards with a relevance score ≤ 65% are rendered at `opacity: 0.65` on S3.

**Context:** M2.5 Spec Sync — design decision not present in spec.

**Pattern baseline:** N/A (visual treatment).

**Rationale:** At MVP, the database has 10–20 methods. Even a query with strong parameters may return low-score matches simply because the corpus is small, not because the method is irrelevant. Hiding low-score results would reduce result counts to near zero in some queries. Rendering them at reduced opacity communicates "present but less confident" without removing information. The threshold of 65% is a first estimate — the pilot feedback (F11 ratings) will reveal whether this calibration is correct.

**Reversibility:** Easy — change or remove the opacity rule.

**Consequences:** The 65% threshold is a frontend-only rule. The backend returns all results sorted by score; the frontend applies the visual treatment. The threshold should be revisited after the pilot based on observed score distributions.

---

## ADR-012 — "Suggest method" link on S3 results screen

**Decision:** S3 includes a contextual link "Método não listado? Sugerir →" at the bottom of the results list, linking to S6.

**Context:** M2.5 Spec Sync — design added this element; spec 2.3 S3 did not include it.

**Pattern baseline:** N/A (navigation/UX element).

**Rationale:** The user who has just received results and found none of them relevant is the highest-value contributor for the method suggestion queue. Placing the link at the moment of disappointment captures the motivation. A generic nav link to S6 would reach users at the wrong moment. This is also consistent with ADR-008 (S6 not in primary nav) — the contextual placement replaces the nav prominence.

**Reversibility:** Easy.

**Consequences:** S3 page component must include the link. No backend changes.

---

## ADR-013 — Database: PostgreSQL (Neon / Vercel Postgres) — supersedes ADR-004

**Decision:** **PostgreSQL only** via Neon (Vercel Postgres) for both development and production. Not SQLite. Single driver (`asyncpg`), single schema dialect.

**Context:** M3 Database — triggered during methods schema implementation when Vercel Postgres emerged as the zero-friction option for the existing Vercel-hosted frontend stack.

**Pattern baseline:** `patterns.md` → Data Access (Repository pattern); 12-Factor App (single `DATABASE_URL` env var).

**Alternatives evaluated:**

| Option | Reason not chosen |
|---|---|
| SQLite (dev) + Turso (prod) — original ADR-004 | Two drivers, two dialects; Turso free tier adequate but adds service dependency with no benefit over Neon |
| Render PostgreSQL add-on | $7/month — breaks zero fixed cost constraint |
| Supabase free tier | Viable, but Vercel Postgres is lower friction given existing Vercel deployment |

**Rationale:** Neon's free tier (0.5 GB storage, branching, serverless) covers MVP scale with no fixed cost. A single `DATABASE_URL` env var replaces the `TURSO_URL` + `TURSO_AUTH_TOKEN` pair. PostgreSQL-native types (`JSONB`, `BOOLEAN`, `TIMESTAMPTZ`) eliminate SQLite workarounds used in the original schema. The pgvector extension (available on Neon) provides a zero-migration path to SQL-level vector search if the corpus exceeds ~200 methods in Phase 3.

**Reversibility:** Moderate — data migration is a `pg_dump` + restore; the driver (`asyncpg`) and schema are standard PostgreSQL with no Neon-specific extensions.

**Consequences:**
- `db/connection.py` must be rewritten to use `asyncpg` with `DATABASE_URL`.
- `embed_methods.py` rewritten for `asyncpg` (done — M3 Database).
- `TURSO_URL` and `TURSO_AUTH_TOKEN` env vars removed from `.env.example`; replaced by single `DATABASE_URL`.
- SQLite dev database removed from repo; local dev uses a Neon branch or a local PostgreSQL instance.
- ADR-004 marked superseded; Turso dependency removed from `requirements.txt`.

**Phase 3 note:** When methods corpus exceeds ~200 entries, enable `pgvector` extension and migrate `embedding_json JSONB` to `embedding vector(384)`. The `MethodRepository` is the only code change; the migration is a single `ALTER TABLE` + `CREATE INDEX ... USING ivfflat`.

---

## ADR-014 — `POST /analyze` response: array output (`experiments[]`) + `notes` field

**Decision:** `POST /analyze` returns `AnalyzeResponse { experiments: ExtractionResult[] }` (min length 1) instead of a single `ExtractionResult`. Each `ExtractionResult` gains a `notes: Optional[str]` field. Phase 1 routes only `experiments[0]` to S2 / RetrievalService / QueryRepository. Full multi-experiment UI deferred to Phase 3 (bundled with F17 side-by-side comparison).

**Context:** Two published Materials & Methods sections processed during spec validation each described multiple distinct studies (acute LD50 + 28-day subacute; 90-day inhalation + recovery cohort). The prior single-object schema either silently dropped secondary studies or forced a false endpoint_category onto a composite protocol. The change was surfaced before Phase 1 implementation, making this the correct point to adjust the contract.

**Pattern baseline:** `patterns.md` → API Design (define the contract before writing any handler code); YAGNI check passed — the array shape resolves a demonstrated real-world failure mode, not an anticipated one.

**Alternatives evaluated:**

| Option | Reason not chosen |
|---|---|
| Single `ExtractionResult` + boolean `additional_experiments_detected` | Discards structured data for secondary experiments; `notes` alone cannot represent a second endpoint_category + route + n_animals cleanly |
| Full multi-experiment S2/S3 now (parallel searches, tabbed results) | Unvalidated scope expansion against hard rule; H1/H3 are still the binding risks; Phase 1 hasn't started |

**Rationale:** Array shape is cheap to implement correctly once at the contract level and avoids a second breaking change in Phase 3. `notes` is display-only (no matching logic), zero retrieval cost, and directly resolves the gap where secondary experiments and unsupported routes (inhalation, repeated-dose) were silently dropped. Deferral of multi-experiment UI to Phase 3 is the explicit scope trade-off required by the hard rule (no additions without equivalent deferral).

**Reversibility:** Moderate — frontend and backend must change together; downstream `QueryRepository.save(extracted_params)` must store `experiments[0]` only until Phase 3.

**Consequences:**
- `app/domain/extraction.py`: `ExtractionResult` gains `notes` field; new `AnalyzeResponse` dataclass wraps `experiments: list[ExtractionResult]`.
- `app/adapters/llm.py`: prompt updated to output `{ "experiments": [...] }` array; segmentation logic added.
- `app/api/routes/analysis.py`: response serialization updated to `AnalyzeResponse`.
- `app/repositories/queries.py`: `QueryRepository.save()` stores `experiments[0].params` in `queries.extracted_params`; full `experiments` array stored in `queries.results_snapshot` for pilot analysis.
- Frontend S2: render `experiments[0]`; add non-blocking banner when `len > 1`; display `notes` when non-null.
- `docs/parameter_model.md` §4, §9, §11 updated (see revision history).
- `spec.md` §2.11 `POST /analyze` contract and F02/F03 feature descriptions updated.
- **Pilot metric added to `assumption-log.md` H1:** log `len(experiments) > 1` occurrences per session. If ≥2/5 pilot sessions produce multiple experiments, pull multi-experiment UI forward from Phase 3 to Phase 2 with explicit equivalent deferral.

**Revision (ADR-019):** Multi-experiment tabs on S2/S3 and per-experiment search are now implemented in Phase 1. The banner-only S2 behaviour described above is superseded. Side-by-side comparison (F17) remains deferred to Phase 3.

---

## ADR-015 — Two-stage extraction: `study_type` (LLM) → `endpoint_category` (application code)

**Decision:** The LLM no longer writes `endpoint_category`. Instead it writes `study_type` as a free-text string describing what kind of study the protocol is. Application code maps `study_type` → `endpoint_category` via a lookup table maintained in `docs/parameter_model.md §4.1`. No second LLM call — single API call, same cost.

**Context:** Test set of 8 real protocol extractions showed that asking the LLM to simultaneously identify the study type AND map it to a 9-value controlled vocabulary was the primary failure mode. Protocols clearly described as "prenatal developmental toxicity study" (OECD TG 414) returned `null` after LLM uncertainty, when the correct output was `null` (not in vocabulary) — but the reasoning path was obscured. Separating identification from classification makes misses explicit (log all `study_type` strings that don't hit the lookup) and makes the lookup table extensible without prompt changes.

**Pattern baseline:** `patterns.md` → Anti-Corruption Layer. The lookup table is the ACL between LLM free text and the domain's controlled vocabulary.

**Alternatives considered:** Two API calls (extract then classify) — rejected: doubles latency and cost. Expanding the vocabulary to cover all observed gaps now — rejected: YAGNI; gaps must be validated by Karynn's H2 check before committing database entries.

**Reversibility:** Easy — lookup table is a dict; adding rows has no downstream impact.

**Consequences:**
- `app/adapters/llm.py`: prompt updated; LLM output no longer contains `endpoint_category` or `confidence`.
- `app/services/extraction.py`: `ExtractionService` runs lookup after LLM call; computes `confidence` via §4.2.
- `docs/parameter_model.md §4.1`: lookup table owned here; Karynn can extend alongside methods DB.
- S2 frontend: displays `study_type` (LLM free text) and `endpoint_category` (lookup result) side by side. "Not covered by database" shown when `endpoint_category` is null.
- All missed `study_type` values logged for H2 gap analysis.

---

## ADR-016 — Evidence field paired with every extracted value; `raw_text_excerpt` removed

**Decision:** Every field in `RawExtraction` has a paired `{field}_evidence: Optional[str]` containing the exact text excerpt that supports the extracted value. The LLM must return `null` for a field (not an inference) when it cannot cite explicit text evidence. `raw_text_excerpt` (previously a single string for the whole object) is removed.

**Context:** `raw_text_excerpt` was tied only to `endpoint_category` and covered only one field. High-risk inference fields (`regulatory`, `animal_counts`, `route`) had no evidence requirement, enabling hallucination. Requiring evidence per field is the highest-leverage single change for extraction reliability — models become measurably more conservative when forced to cite.

**Pattern baseline:** `patterns.md` → Error Handling (typed returns, not exceptions). Evidence fields make the extraction auditable: a null evidence string on a non-null field is a detectable anomaly.

**Reversibility:** Easy — evidence fields are additive; removing them is a prompt change.

**Consequences:**
- LLM output token count increases ~30–40%. Acceptable at Sonnet pricing and sub-cent-per-query cost baseline.
- `app/adapters/llm.py`: prompt updated with evidence requirement per field.
- `app/domain/extraction.py`: `RawExtraction` dataclass gains `{field}_evidence` fields; `raw_text_excerpt` removed.
- S2 frontend: "show evidence" toggle per field reveals the evidence string. Toggle is collapsed by default — evidence behind, not inline.
- Pilot metric: log null evidence rate per field. Fields with consistently null evidence despite non-null values indicate prompt ambiguity.

---

## ADR-017 — `n_animals` replaced by `AnimalCounts`; `confidence` computed in application code

**Decision (n_animals):** `n_animals: Optional[int]` replaced by `animal_counts: Optional[AnimalCounts]` with subfields `female`, `male`, `total`, `per_group` (all `Optional[int]`). LLM populates only subfields explicitly stated in the text; derivation (e.g. female + male = total) is prohibited under ADR-016 strict extraction mode.

**Decision (confidence):** `confidence` removed from LLM output. `ExtractionService` computes it after the `endpoint_category` lookup per §4.2. Rule: `low` if `endpoint_category` is null; `high` if ≥4 non-null non-default fields; `medium` otherwise.

**Context:** `n_animals` as a single integer failed on every multi-cohort protocol in the test set (100F + 60M in D-allulose; generational counts in benzophenone; slaughterhouse-derived corneas in EVEIT). Self-graded `confidence` was redundant once the schema is well-defined and introduced sycophancy risk (models tend to self-grade as high).

**Reversibility:** Easy for confidence (revert to LLM-generated, log comparison). Moderate for animal_counts (schema change requires migration of `queries.extracted_params` JSONB if already in production — not an issue pre-Phase 1).

**Consequences:**
- `app/domain/extraction.py`: `AnimalCounts` dataclass added; `ExtractionResult.confidence` set by service, not adapter.
- `app/adapters/llm.py`: `n_animals` removed from prompt; `animal_counts` object added; `confidence` removed from prompt.
- `app/services/extraction.py`: `compute_confidence()` function added.
- S2 frontend: animal counts displayed as structured object (female / male / total / per group) rather than a single integer field.
- Pilot: after F11 feedback collected, compare computed confidence against researcher relevance ratings to validate §4.2 threshold.

---

## ADR-018 — Per-field confidence replaces overall extraction confidence

**Decision:** Confidence is **per-field only**. `RawExtraction` gains a `{field}_confidence: Optional[Literal["high","medium","low"]]` for every extracted field. The LLM outputs it alongside the evidence string. Each value answers: *how certain is this parameter given the evidence for that specific field?* There is no overall `ExtractionResult.confidence` or retrieval-level aggregate.

**Context:** The EVEIT extraction exposed the gap: route has a direct quote ("applied exactly over the apex of the cornea" → ocular), animal_counts is null (not extracted), and application_area requires interpretation (general, by rule rather than by explicit statement). A single aggregate score communicates none of this. The per-field signal is the actionable one for S2 — it tells the user which fields to scrutinize.

**Per-field confidence scale (LLM-generated, bounded):**
- `"high"` — the evidence string is an explicit, direct statement of the value with no interpretation required (e.g., "p.o." → oral; "60 male Wistar rats" → species rat, male 60)
- `"medium"` — the evidence requires vocabulary mapping or mild inference (e.g., "intragastric administration" → oral; "following OECD guidelines 414" → regulatory True)
- `"low"` — the value is present but evidence is tangential or required significant interpretation; flag for user review
- `null` — field is null; confidence not applicable

**S2 display:**
- Per-field rows: `{field}_confidence` badge (High / Medium / Low) on the left; "show evidence" toggle on the right.
- No header-level confidence badge (supersedes ADR-010 aggregate display for extraction).

**Pattern baseline:** `patterns.md` → Error Handling. Per-field confidence makes each extraction value independently auditable. A null `field_evidence` on a non-null field (ADR-016 violation) is detectable as `confidence = "low"` on that field.

**Alternatives considered:** Programmatic per-field confidence from evidence presence alone (non-null evidence → high, null evidence → low) — rejected: too binary; doesn't distinguish direct synonym match from interpreted inference, which is the useful signal. Aggregate retrieval confidence from matching fields — rejected: conflates field-level certainty with search relevance; user clarified confidence is about parameter certainty given evidence, not overall. Remove confidence entirely — rejected: S2 needs to direct user attention to fields requiring scrutiny.

**Reversibility:** Moderate — schema change to `RawExtraction`; prompt update; S2 frontend per-field indicator; removal of `ExtractionResult.confidence` from API.

**Consequences:**
- `app/models/protocol.py`: `{field}_confidence` on `RawExtraction`; `ExtractionResult.confidence` removed.
- `app/adapters/llm.py`: prompt updated — per-field confidence included in output alongside evidence, with 3-value scale and criteria.
- S2 frontend: per-field confidence indicator per row (collapsed with evidence); header badge removed.
- `docs/parameter_model.md` §4 and §9 updated.

---

## ADR-019 — Separate `POST /search` from extraction; multi-experiment tabs on S2/S3

**Decision:** `POST /analyze` returns extraction only (`experiments[]` + primary `params`). Retrieval runs on a new `POST /search` endpoint after the user confirms parameters on S2. When `len(experiments) > 1`, S2 and S3 show experiment tabs; clicking "Search alternatives" on S2 runs `POST /search` for **all** experiments in parallel and navigates to S3 with per-experiment result sets.

**Context:** Early implementation bundled retrieval into `/analyze`, which violated workflow W1 (search must use **confirmed** params). S2 showed only a non-blocking banner for secondary experiments (ADR-014 deferral). Pilot prep and the Parthenium test fixture demonstrated that researchers need to review and search each detected study independently.

**Alternatives considered:**

| Option | Reason not chosen |
|---|---|
| Keep retrieval on `/analyze` | Ignores S2 edits; wrong timing in W1 |
| Search only the active S2 tab | Secondary experiments silently skipped on S3 |
| Full side-by-side comparison (F17) | Out of scope; tabs sufficient for Phase 1 |

**Consequences:**
- `app/api/routes/search.py`: `POST /search` with `SearchRequest { params, filters?, lang? }` → `SearchResponse { query_id, results, filter_relaxation }`.
- `app/api/routes/analysis.py`: retrieval removed from `/analyze`.
- Frontend S2: `ExperimentTabs` component; `searchAllExperiments()` on search CTA.
- Frontend S3: real `ResultCard` list from API (replaces mock assessment report); matching tabs; OECD ref on regulatory link; **Match** label on score.
- `query_id` returns `null` until Phase 2 query persistence.
- Supersedes ADR-014 deferral of multi-experiment UI to Phase 3 for S2/S3 tabs (side-by-side comparison remains Phase 3 / F17).

---

## ADR-020 — Campo `application_area` renomeado para `study_domain`

**Decision:** O campo `application_area` em `RawExtraction`, na tabela `methods`, e em todos os contratos de API é renomeado para `study_domain`.

**Context:** O nome `application_area` era ambíguo em dois sentidos: (a) podia ser confundido com "área anatômica de aplicação" (onde a substância é aplicada no organismo), conflitando com o campo `route`; (b) podia ser interpretado como "área de aplicação do método" em vez de "domínio em que o estudo existe". A ambiguidade foi identificada durante revisão de vocabulário em M3+.

Adicionalmente, o vocabulário original de 4 valores (`pharma`, `cosmetics`, `chemical_safety`, `general`) não cobria domínios não-regulatórios relevantes em CEUAs brasileiras — especificamente neurociência comportamental (modelos de ansiedade, dor, cognição) e protocolos educacionais (treinamento cirúrgico). O campo `application_area` com o nome antigo implicava que um framework regulatório sempre existia, o que é falso para esses casos.

**Rationale do novo nome:** `study_domain` responde à pergunta "em qual domínio de aplicação este estudo existe?" sem implicar que um contexto regulatório necessariamente existe. É inequívoco tanto para pesquisadores quanto para o LLM.

**Vocabulário MVP (Phase 1–2):** `pharma` · `cosmetics` · `chemical_safety` · `general` — inalterado.

**Vocabulário Phase 3 (candidatos — pendente validação Karynn):** `behavioral` · `education` · `basic_research`. Não adicionar ao vocabulário ativo até que (a) Karynn confirme que protocolos do piloto os requerem e (b) existam métodos correspondentes no banco. Adicionar valores sem cobertura gera expectativa falsa no S2.

**Alternatives considered:**
- `regulatory_context` — rejeitado: implica que um framework regulatório sempre existe; não cobre modelos comportamentais ou educacionais.
- `application_context` — rejeitado: "contexto de aplicação" ainda pode ser lido como "como o método é aplicado", apenas parcialmente mais claro que o original.
- `experimental_context` — rejeitado: mais amplo que o campo realmente é; não comunica que os valores MVP são domínios de aplicação setorial.

**Reversibility:** Moderada — afeta contrato de API, schema de banco, e prompt.

**Consequences:**
- `parameter_model.md`: campo renomeado em §2 (tabela), §3.3 (seção de vocabulário — expandida com candidatos Phase 3), §4 (dataclass `RawExtraction`), §5 (embedding template), §7 (exemplo protótipo), §9 (prompt), §11.1–11.3 (exemplos reais).
- `spec.md`: renomeado em §2.2 F02/F03, §2.3 S2, §2.6 schema `methods`, §2.6 retrieval approach, §2.10 W1, §2.11 `POST /analyze` response e `POST /search` request body.
- `db/migrations/001_initial.sql`: `application_area TEXT` → `study_domain TEXT`. Migration necessária antes de ativar métodos (`active = TRUE`); sem dado persistido a converter até Phase 1 entrar em produção.
- `app/models/protocol.py`: campo renomeado em `RawExtraction`.
- `app/adapters/llm.py`: prompt atualizado.
- `app/api/routes/search.py`: `params.application_area` → `params.study_domain` no `SearchRequest`.
- `embed_methods.py`: coluna `application_area` → `study_domain` na query de leitura.
- Frontend S2: label PT "Área de aplicação" → "Domínio do estudo" / EN "Study domain".

---

## ADR-021 — `category_3r` de TEXT para JSONB (múltiplos Rs por método)

**Status:** Superseded by [ADR-023](#adr-023--colunas-text-de-rationale-por-r-substitui-category_3r-jsonb).

**Decision:** `category_3r TEXT NOT NULL` substituído por `category_3r JSONB NOT NULL` — array de strings, mesmo padrão de `routes_applicable`.

**Context:** Um método pode satisfazer múltiplos Rs simultaneamente: TG 420/423/425 reduzem o número de animais (reduction) E refinam o procedimento eliminando a letalidade como endpoint obrigatório (refinement). LLNA:DA e LLNA:BrdU eliminam radioatividade em relação ao TG 429 (refinement) e substituem os testes em cobaia (replacement). O campo TEXT forçava uma escolha arbitrária que perdia informação auditável e afetava o filtro do S3.

**Formato:** `'["replacement"]'` | `'["reduction","refinement"]'` | `'["replacement","refinement"]'` etc.

**Filtro no RetrievalService:** `WHERE category_3r @> '["replacement"]'::jsonb` (PostgreSQL JSONB contains). Semântica OR — retorna métodos que têm *qualquer* R selecionado.

**Classificações ambíguas — pendentes de confirmação Karynn:**

| Método | Proposta | Questão |
|---|---|---|
| TG 429 LLNA | `["replacement"]` ou `["reduction","refinement"]` | Substitui cobaia (replacement) mas ainda usa camundongo — depende do referencial |
| TG 442A/B | `["refinement"]` ou `["replacement","refinement"]` | Mesmo dilema do LLNA + eliminação de radioatividade |
| TG 420/423/425 | `["reduction","refinement"]` | Reduz animais E refina — parece claro |
| NICEATM cytotox | `["replacement","reduction"]` | Substitui dose-ranging in vivo E reduz animais no estudo principal |

**Reversibility:** Moderada — schema change + frontend.

**Consequences:**
- `001_initial.sql`: tipo da coluna + INSERTs como arrays JSON.
- `app/repositories/methods.py`: query de filtro via `@>` operator.
- Frontend S3 `ResultCard`: iterar array para múltiplos badges 3R.
- `karynn_review_checklist.md`: campo `category_3r` adicionado como item de revisão para os casos ambíguos.
- `spec.md` §2.6 schema `Method` + §2.3 S3 description.

**Superseded because:** flags JSONB sem justificativa auditável; ADR-023 move cada R para uma coluna TEXT nullable cujo valor *é* a rationale.

---

## ADR-022 — `method_regulatory_contexts`: validação por método × domínio × jurisdição; jurisdições específicas

**Decision:** (a) `validation_status`, `jurisdiction`, `jurisdiction_notes`, `regulatory_url` removidos da tabela `methods` e migrados para nova tabela `method_regulatory_contexts`. (b) Vocabulário de jurisdição substituído: `'brazil' | 'international' | 'both'` → `'brazil' | 'eu' | 'us' | 'oecd'`.

**Context:** `jurisdiction = 'both'` e `validation_status = 'validated'` eram propriedades do método, quando na realidade são propriedades da combinação método × domínio de aplicação × framework regulatório. BCOP (TG 437) é `validated` para cosméticos na UE (Reg 1223/2009), `in_process_of_validation` para químicos sob REACH (ECHA), e `not_validated` quando não há status formal ANVISA para medicamentos. Um único par (validation_status, jurisdiction) comunicava algo que não era verdadeiro para todos os contextos. `international` colapsava EU, US, OECD e outros frameworks sem distinção — um pesquisador precisando de evidência regulatória específica para submissão ANVISA vs. registro CE obtinha a mesma resposta.

**Schema:**
```sql
CREATE TABLE method_regulatory_contexts (
    id                SERIAL PRIMARY KEY,
    method_id         INTEGER NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    study_domain      TEXT    NOT NULL,  -- 'general' | 'pharma' | 'cosmetics' | 'chemical_safety'
    jurisdiction      TEXT    NOT NULL,  -- 'brazil' | 'eu' | 'us' | 'oecd'
    validation_status  TEXT    NOT NULL,  -- 'validated' | 'in_process_of_validation' | 'not_validated'
    regulation_status  TEXT,             -- 'not_approved' | 'approved' | 'recommended' | 'mandatory'
    regulation_date    DATE,             -- date of regulation / recognition / adoption (YYYY-MM-DD)
    regulation_purpose TEXT,             -- what the method is recognized/validated for in this context
    regulatory_body    TEXT,             -- 'CONCEA' | 'ANVISA' | 'ECHA' | 'EMA' | 'EPA' | 'FDA' | 'ICCVAM' | 'OECD'
    regulatory_url     TEXT,
    notes              TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (method_id, study_domain, jurisdiction)
);
```

**Jurisdiction vocabulary:**
- `brazil` — reconhecimento CONCEA / ANVISA / MAPA
- `eu` — ECHA (REACH), EMA (pharma), EU Cosmetics Regulation 1223/2009, EFSA
- `us` — FDA, EPA, ICCVAM/NICEATM
- `oecd` — adotado como OECD Test Guideline; implica aceitação pelos 38 países-membros, sujeita a adoção nacional individual

**Seed strategy MVP:** semear `brazil` (RN 18/2014) + `oecd` (TG number) para métodos confirmados; `us` para NICEATM. Deixar `eu` como [VERIFY] no checklist — requer Karynn verificar contra EU Cosmetics Reg 1223/2009 e REACH Annex.

**RetrievalService query (filtro de jurisdição):**
```sql
SELECT DISTINCT m.*
FROM methods m
WHERE EXISTS (
    SELECT 1 FROM method_regulatory_contexts mvc
    WHERE mvc.method_id = m.id
      AND (mvc.study_domain = :study_domain OR mvc.study_domain = 'general')
      AND mvc.jurisdiction = :jurisdiction   -- filtro opcional
)
```

**POST /search response:** inclui array `regulatory_contexts` com todas as entradas do método para o domínio matchado.

**S3 ResultCard:** exibe badges de jurisdição para todos os contextos retornados (ex: "OECD · Brasil"); `validation_status` exibido do contexto mais relevante (brazil se disponível, senão oecd).

**Reversibility:** Moderada — JOIN adicional no MethodRepository; frontend atualiza display de badges.

**Consequences:**
- `001_initial.sql`: nova tabela + seed de contextos; campos removidos de `methods`.
- `spec.md` §2.6: entidade Method atualizada; nova entidade MethodRegulatoryContext; POST /search filter e response.
- `karynn_review_checklist.md`: seção de validação por método reestruturada como tabela de contextos.
- `app/repositories/methods.py`: JOIN + GROUP BY para agregar contextos por método.
- Frontend S3: múltiplos badges jurisdição/validação por card.
- H5 impact: Karynn deve registrar tempo por entrada incluindo preenchimento de contextos — novo dado para estimativa de manutenção.

---

## ADR-023 — Colunas TEXT de rationale por R (substitui `category_3r` JSONB)

**Decision:** `category_3r JSONB` substituído por três colunas TEXT nullable em `methods`:

- `replacement_rationale`
- `reduction_rationale`
- `refinement_rationale`

Presença de valor não-nulo/não-vazio = o método qualifica para aquele R. O texto *é* a justificativa auditável — não há coluna companion separada de flag.

**Context:** ADR-021 permitia múltiplos Rs, mas só como flags. CEUAs e curadoria precisam de rationale explícita (por que este método conta como replacement vs reduction). Colunas TEXT por R unificam qualificação e auditoria.

**Filtro:** `replacement_rationale IS NOT NULL` (idem reduction/refinement), semântica OR no filtro S3 — métodos com *qualquer* R selecionado. API ainda expõe `category_3r` derivado das colunas preenchidas para compatibilidade.

**Migração em 4 etapas (não combinar DROP+ADD na mesma transação):**

1. `007_add_3r_rationale_columns.sql` — ADD das três colunas; `category_3r` permanece (fonte de verdade de quais Rs precisam de texto). Auto-aplicada por `migrate.py`.
2. `scripts/backfill_3r_rationales.py` — para cada R em `category_3r`, insere placeholder `'[PENDENTE — ver category_3r]'` (não string vazia), distinguindo “precisa preencher” de “não se aplica”.
3. Gate — só prosseguir quando a query de pendências retornar zero linhas (`backfill_3r_rationales.py --check`).
4. ~~`manual/008_drop_category_3r.sql`~~ — superseded by auto-applied `026_methods_drop_category_3r_reorder.sql` (also restores column order so `text_for_embedding` / `embedding_json` follow `keywords`).

**Reversibility:** Moderada — schema + backfill + checklist Karynn.

**Consequences:**
- `app/repositories/methods.py`: SELECT das colunas rationale; qualificação via `IS NOT NULL` / texto não-vazio.
- Frontend S3 `ResultCard`: um badge por coluna não-nula; `title`/tooltip = conteúdo da rationale.
- `karynn_review_checklist.md`: preencher `*_rationale` nos 25 seeded (casos ambíguos 13, 14–15, 23–25 incluídos).
- `spec.md` §2.6, `tables.md`: schema Method atualizado.
- ADR-021 marcado superseded.
