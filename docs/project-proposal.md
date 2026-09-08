# Project Proposal — Assist3R

**Team:** Karynn (animal ethics & welfare, 4h/week) · Leo (software development & AI, 4h/week)   
**Institutional backing:** Fórum Animal

---

## 1\. Problem

Globally, an estimated 200 million animals are used annually for scientific purposes, with official figures in Brazil indicating approximately 2 million animals per year. This use spans basic and applied research, safety and efficacy testing, and educational activities, involving a wide range of sentient species, including rodents, fish, birds, as well as dogs, cats, rabbits, and non-human primates. Because these practices frequently entail confinement, physical restraint, and invasive procedures, often under constraints of economic feasibility, the use of animals in science is intrinsically associated with the generation of suffering, in many cases reaching high levels of severity. Scientific researchers in Brazil and worldwide continue relying on animal models despite the growing availability of validated alternatives. The barriers are multifactorial, including structural issues:

- **Fragmented knowledge.** Databases of alternative methods (ALT Web, EURL ECVAM, OECD guidelines, peer-reviewed literature) are siloed, use inconsistent vocabularies, and are not designed for decision-support workflows.  
- **Discovery gap.** To find an alternative, a researcher typically needs to already know what to look for. Existing tools are built as reference databases, not as recommendation systems.  
- **Contextual friction.** Standard search results don't indicate regulatory validity, jurisdictional acceptance, or suitability for a specific experimental endpoint. This forces time-intensive manual evaluation.  
- **Structural pressures.** Funding and publication incentives reinforce established practices, compounding the cost of exploring alternatives.

**The Brazilian context makes this urgent.** More than 1,000 Animal Research Ethics Committees (CEUAs) operate in Brazil, most without access to integrated decision-support resources. The gap between the existence of validated alternatives and their effective adoption is wide, and no accessible tool currently bridges it.

---

## 2\. Why now

Two conditions have converged that make this project timely:

1. **AI has matured for this task.** Natural language processing and semantic matching are now robust enough to translate heterogeneous scientific descriptions into structured, actionable recommendations — a capability that did not exist at production quality even three years ago.  
     
2. **Neither the animal advocacy movement nor the Animal Research Ethics Committees have yet applied these capabilities systematically.** This is a neglected, high-impact application area. Well-resourced AI projects tend to target commercial markets; the gap here is an opportunity.

---

## 3\. Proposed solution

An AI-powered decision-support web application that:

1. Accepts a free-text description of an experimental protocol in English or Portuguese.  
2. Extracts core experimental parameters using an LLM, including: *biological model type · objective · procedure · endpoint · application area.*  
3. Matches those parameters against a curated database of alternative methods using semantic similarity plus structured filters, backed by a synonym dictionary to bridge vocabulary gaps.  
4. Returns ranked recommendations with:  
   - Classification under the 3Rs framework (Replacement / Reduction / Refinement)  
   - Jurisdictional validity indicators (Brazil / International / Both)  
   - Confidence scores  
   - The specific parameters that drove each match (for user calibration)  
   - Links to primary literature and regulatory guidelines  
5. Allows direct database search with advanced filters for users who know what they are looking for.  
6. Collects structured feedback on each query to drive iteration.  
7. Accepts user-submitted suggestions for new methods (queued for manual curation).

**Core differentiator:** the tool analyzes the protocol *before* searching. Existing resources (ALT Web, ECVAM's TSAR, OECD guidelines) require the researcher to already know the relevant vocabulary. This tool reduces that prerequisite.

---

## 4\. Value proposition

| For whom | Value delivered |
| :---- | :---- |
| Scientific researchers (academia, pharma R\&D) | Discovery of relevant alternatives they didn't know about, with full traceability to primary sources |
| CEUA members (ethics committees) | Consolidated, citable reference during protocol review |
| Regulatory and institutional review bodies | Structured basis for requiring consideration of alternatives |
| Advocates for the 3Rs principle | Evidence-based tool to support engagement with researchers and institutions |

---

## 5\. Target users

**Primary:**

- Scientific researchers at universities and research institutes  
- R\&D professionals in the pharmaceutical industry  
- Members of Animal Research Ethics Committees (CEUAs)

**Secondary:**

- Regulatory bodies and institutional review boards  
- Animal advocacy organizations  
- Educators teaching research methodology

**User profile assumptions:**

- Scientific training at the graduate level or equivalent  
- Obligation (regulatory or institutional) to consider alternatives to animal use  
- Not necessarily a specialist in alternative methods — needs guided discovery  
- Comfortable with scientific search interfaces and terminology

---

## 6\. Data sources

| Source | Type | Access strategy |
| :---- | :---- | :---- |
| ALT Web (Johns Hopkins CAAT) | Structured database of validated methods | Manual curation from published records |
| EURL ECVAM / TSAR | EU-validated methods | Manual curation from published records |
| OECD Test Guidelines | Regulatory standards | Reference documents, manual extraction |
| PubMed (method reviews) | Peer-reviewed literature | Public API for future automation |
| CONCEA | Brazilian regulatory context | Manual extraction for jurisdictional tagging |

Access terms for each source will be verified before any automated ingestion is considered. For the MVP, all data will be manually curated by Karynn.

---

## 7\. Scope

**Selected tier: Minimal (MVP)** — a working end-to-end product sufficient for pilot validation, not a reference platform.

### Minimal — MVP (Phases 1–2, months 0–6)

- Free-text protocol input, with parameter extraction across the core fields  
- Parameter display on the results screen for user confirmation and correction  
- 25 manually curated methods covering the most common CEUA use cases in Brazil, sourced from CONCEA normative resolutions (RN 18/2014 and subsequent) and corresponding OECD guidelines  
- Ranked recommendations with 3Rs classification and jurisdictional indicators  
- Direct database search with advanced filters  
- Simple user accounts via email magic link, with visible anonymous bypass  
- Query history and PDF/CSV export (for registered users)  
- Structured feedback questionnaire after each query  
- Method suggestion form (submissions queued for manual review)  
- Bilingual interface (Portuguese / English)

### Full — Phase 3 (months 6–9)

- Expanded database (hundreds of methods)  
- Checklist of method requirements by endpoint and application area  
- Side-by-side method comparison  
- User profiles with research area and preferences

### Extended — Phase 4+ (months 9–12)

- Real-time literature ingestion (PubMed monitoring)  
- Collaborative curation platform  
- Integration with funding databases and regulatory reporting  
- Public API for protocol management systems

**Rationale for the minimal tier:** the highest-risk hypothesis is that AI-based parameter extraction from free-text protocols produces recommendations researchers find relevant and trustworthy. The MVP must be complete enough to test this hypothesis in a real pilot — hence the inclusion of accounts, history, export, and feedback tooling — but small enough to build and maintain with 8 hours per week.

---

## 8\. Success metrics

**Binary success definition** (used as the filter for every design decision):

A researcher with no prior knowledge of alternative methods describes a real protocol in free text, and receives at least 3 relevant recommendations with verifiable source references in under 60 seconds.

**Primary metrics:**

- 500 registered researchers by end of year 1  
- Active use frequency (sessions per registered user per month)  
- Structured feedback on relevance and accuracy (target: ≥60% of recommendations rated "relevant" or better across the pilot cohort)

**Explicitly not a success metric:** direct attribution to ethics approvals or specific protocol changes. This chain of causation is not easily traceable at scale.

**Pilot gate (end of Phase 3):**

- 5–10 researchers / CEUA members complete the pilot protocol  
- ≥3 of 5 rate the recommendations as relevant or better

---

## 9\. Roadmap (12 months)

| Phase | Months | Focus |
| :---- | :---- | :---- |
| 1 | 0–3 | Refine scope, curate initial database, validate data access, prototype RAG pipeline locally |
| 2 | 3–6 | Build production web app (frontend \+ backend), deploy, run internal tests |
| 3 | 6–9 | Pilot testing with 5–10 users, structured feedback collection, iteration |
| 4 | 9–12 | Database expansion, Phase 2 features, publication and dissemination |

**Prototype cycle within Phases 1–2:** 3 days to build, 3 days to test internally, 3 days to analyze — a 9-day cycle per iteration on the core pipeline.

---

## 10\. Budget

Apart from the team compensation the project operates on a minimal budget: server infrastructure and LLM API usage. All architectural decisions in the specification prioritize zero fixed infrastructure cost at MVP (Render free tier, Vercel free tier, Neon/Vercel Postgres free tier, local embeddings model). The only variable cost is the Anthropic API for protocol analysis, estimated at a fraction of a cent per query.

---

## 11\. Team and position

| Role | Contributor | Commitment |
| :---- | :---- | :---- |
| Animal ethics and welfare, regulatory processes, alternatives advocacy, data curation | Karynn | 4h / week |
| Software development, AI integration, architecture | Leo | 4h / week |

**Institutional backing:** the project has formal endorsement from Fórum Animal, an organization with standing credibility in the Brazilian animal protection movement. This endorsement strengthens legitimacy when engaging with researchers and ethics committees, particularly during the pilot phase.

**Combined strengths:**

- Domain expertise to curate data correctly and recruit credible pilot users  
- Technical capability to deliver the system end-to-end at low cost  
- Access to a target user community (Brazilian CEUAs) 

**Honest constraints:**

- Combined 8h/week caps the complexity that can be delivered; architectural simplicity is therefore a non-negotiable constraint, not an aesthetic choice  
- No dedicated designer or product manager — mockups generated with AI assistance  
- No marketing budget — pilot recruitment will rely on the Fórum Animal network

---

## 12\. Expected impact

This project targets a neglected bottleneck in animal advocacy and animal research ethical committees: the inability for researchers and ethics committees to easily identify and apply existing alternatives.

**If successful, expected outcomes include:**

- Increased adoption of non-animal methods in Brazilian research  
- Improved quality and consistency of ethical review processes in CEUAs  
- Reduction in animal use over time, correlated (though not directly attributable) to tool usage  
- Strengthened capacity for advocacy organizations and institutions to engage with researchers using evidence-based tools

**Scalability path:** if the pilot validates the approach, the tool is positioned to scale internationally. The architecture (bilingual from day one, jurisdiction as a first-class data field, manually curated base with a clear expansion path) is designed to make that scaling feasible without structural rewrites.

---

## 13\. Risks and critical assumptions

This section consolidates qualitative risks (severity-framed) with the testable assumptions that drive them. Each high-severity risk is backed by a hypothesis with a concrete, cheap validation test. Status is tracked over time and referenced at every review gate (Modules 4 and 5).

### 13.1 Risk overview

| Severity | Risk | Driving assumption (see 13.2) |
| :---- | :---- | :---- |
| **High** | Data credibility — inadequate or unvalidated recommendations undermine trust irreversibly | H2, H5 |
| **High** | Parameter extraction accuracy — if the LLM misidentifies protocol parameters, results are irrelevant | H1, H3 |
| **High** | Researcher resistance — established practices and funding pressures may resist AI-driven recommendations | H4 |
| **Medium** | Jurisdictional conformity — validation standards vary by region | H5 |
| **Medium** | Team capacity — 8h/week total is a hard constraint on scope | (operational, not a testable assumption) |
| **Low** | Usability across skill levels — interface must serve novices and experts | tested in pilot (Module 5\) |

### 13.2 Critical assumptions — test plan

| \# | Assumption | Why it matters | How to test cheaply | Status |
| :---- | :---- | :---- | :---- | :---- |
| **H1** | Users can describe protocols in free text in a way that is useful for the AI | If they can't, the free-text input path fails and a guided form becomes necessary — a fundamental architecture change | Ask 5 researchers to describe a real protocol in free text; verify whether the key parameters (biological model, endpoint, procedure) appear without structured prompting | Not tested |
| **H2** | ALT Web, ECVAM, and OECD together provide sufficient and accessible data to cover common endpoints | If coverage is low or access is blocked, the MVP has no viable database | Manually check 10 representative protocols against these sources and count matches; verify terms of use for permitted automation | Not tested |
| **H3** | LLM-based text analysis can extract experimental parameters with sufficient precision for relevant retrieval | If extraction is imprecise, recommendations are irrelevant — this is the core product risk | Build a minimal prototype (prompt \+ 20 seed records) and test with 5 real protocols; measure precision | Not tested |
| **H4** | Researchers trust recommendations when primary-source traceability is provided | If they don't, the tool is unusable in any regulatory or review context | Show 3 potential users a mockup with recommendation \+ reference; ask "would you cite this in an ethics submission?" | Not tested |
| **H5** | Building and maintaining a curated methods database at adequate quality is tractable for the team | If curation is unsustainable, the product degrades quickly post-launch | Estimate in 2 hours: how many candidate entries exist, update frequency, exportable format | Not tested |

### 13.3 Assumption most likely to be wrong

"LLM-based text analysis can extract experimental parameters with sufficient precision for relevant retrieval."

The parameter-correction step on the results screen is the insurance against this — but if correction is frequently needed, the tool shifts from "AI-powered" to "AI-assisted form fill," which is a less compelling pitch. The pilot (Module 5\) will tell us which one it actually is.

### 13.4 Team fit checks

- [ ] Access (or a realistic path to access) potential users in the scientific community for validation — covered by Karynn’s network  
- [ ] Technical capability to build the MVP (RAG \+ public APIs \+ basic frontend) — covered by Leo's 4h/week  
- [ ] Realistic time budget: 40–60 hours of development for the MVP  
- [ ] Genuine interest beyond the technical aspect

### 13.5 Technical risks flagged forward to the specification

These became explicit constraints in `spec.md` (Module 2):

- **Database access.** Terms of use of ALT Web, ECVAM, and OECD must be verified before any automated ingestion is assumed. Manual periodic download is the safe fallback and the baseline for the MVP.  
- **Data quality.** Source data is inconsistent in format and completeness; the ingestion pipeline requires a normalization layer (addressed by manual curation in the MVP, automation deferred to Phase 4).  
- **Language.** Protocols may be submitted in Portuguese or English. The architecture supports both from day one — deferring this would be expensive to retrofit.  
- **Database updates.** New methods are published continuously. The architecture must support re-ingestion without rebuilding from scratch (handled by manual update + re-deploy in the MVP; incremental pipeline in later phases).
- **Database infrastructure.** **PostgreSQL only** for both development and production (Neon/Vercel Postgres free tier, or local PostgreSQL in dev). Not SQLite. Replaces the original SQLite/Turso plan (ADR-013 supersedes ADR-004). Single `DATABASE_URL` (`postgresql://`); driver `asyncpg`; no fixed cost at MVP scale.

### 13.6 Simpler alternative (explicitly considered, kept as fallback)

A structured form (fields for biological model, endpoint, etc.) plus semantic search over the curated base — no free-text extraction. Less ambitious, more predictable, easier to validate. The current design keeps the free-text path as the default but preserves the structured form as a fallback if H1 or H3 fail in the pilot.

---

