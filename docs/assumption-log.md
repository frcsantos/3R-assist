# Assumption Log — 3R Assist

> **Binary success definition:**
> A researcher with no prior knowledge of alternative methods describes a real protocol in free text, and receives at least 3 relevant recommendations with verifiable source references in under 60 seconds.

Updated at: M1.5 (initial), M2 Phase A checkpoint, M3.4, M4, M5.

---

| # | Assumption | Why it matters | How to test cheaply | Status |
|---|---|---|---|---|
| H1 | Users can describe experimental protocols in free text in a way that yields useful parameters without structured prompting | If false, the free-text input path fails and a guided form becomes necessary — a fundamental architecture change | Ask 5 researchers to describe a real protocol in free text; verify whether biological model, endpoint, and procedure appear without prompting. **Additional metric (ADR-014):** log `len(experiments) > 1` per session — if ≥2/5 sessions produce multiple experiments, multi-experiment S2/S3 UI must be pulled forward from Phase 3 to Phase 2 with explicit equivalent deferral | Untested |
| H2 | ALT Web, ECVAM, and OECD together provide sufficient and accessible data to cover common Brazilian CEUA endpoints | If coverage is low or access is blocked, the MVP has no viable database | Manually check 10 representative protocols against these sources and count matches; verify terms of use for permitted automation | **Partially addressed** — see note |
| H3 | LLM-based text analysis can extract experimental parameters with sufficient precision for relevant retrieval | If extraction is imprecise, recommendations are irrelevant — this is the core product risk | Build a minimal prototype (prompt + 20 seed records) and test with 5 real protocols; measure precision | Untested |
| H4 | Researchers trust recommendations when primary-source traceability is provided | If false, the tool is unusable in any regulatory or ethics-committee context | Show 3 potential users a mockup with recommendation + reference; ask "would you cite this in an ethics submission?" | Untested |
| H5 | Building and maintaining a curated methods database at adequate quality is tractable for the team | If curation is unsustainable, the product degrades quickly post-launch | Estimate in 2 hours: how many candidate entries exist, update frequency, exportable format | **Partially addressed** — see note |

---

## Notes

**Assumption most likely to be wrong (H3):** The parameter-correction step on the results screen is the insurance — but if correction is frequently needed, the tool shifts from "AI-powered" to "AI-assisted form fill," which weakens the value proposition. The pilot (Module 5) will resolve this.

**Structural fallback (H1 + H3):** A structured form (fields for biological model, endpoint, etc.) plus semantic search is preserved as an explicit fallback. If H1 or H3 fail in the pilot, this path is activated without a full architecture rewrite.

**Known operational risk (not a testable assumption):** Combined 8h/week is a hard scope ceiling. This is tracked as a scope constraint, not an assumption.

**H3 progress note (Phase 1, 2026):** the extraction reliability suite (`backend/tests/test_extraction_reliability.py`, `@pytest.mark.live`) now runs 9 published-protocol fixtures through the real LLM with weighted scoring, and extraction-prompt tests (`test_extraction_prompt.py`) guard the prompt contract. This is **evidence for H3 but not a pilot result** — the formal check remains 5 real protocols described by researchers, measuring precision of resulting recommendations. Do not mark H3 as Tested until the pilot runs.

**H1 progress note:** multi-experiment S2/S3 UI is implemented (ADR-014/019); the `len(experiments) > 1` pilot metric stays as specified.

**H2 — Partially addressed (M3 Database):** Karynn's source analysis confirmed that ECVAM DB-ALM + NICEATM + Farmacopeia Brasileira cover 8 common CEUA endpoints (skin irritation/corrosion, ocular irritation, skin sensitisation, phototoxicity, genotoxicity, pyrogenicity, acute toxicity). Two CONCEA normative resolutions (RN 18/2014) and one OECD guidance document (GD 129/2010) were reviewed; 25 methods curated across those endpoints. **The formal structured check required to declare H2 Tested is still pending:** download ECVAM DB-ALM export, filter by toxicology category, count entries with validated OECD TG, and verify terms of use for automated ingestion. Do not mark H2 as Tested until this check is completed and documented.

**H5 — Partially addressed (M3 Database):** Curation of 25 methods from two source documents completed. This establishes that the content is accessible and structurable. **The formal check required to declare H5 Tested is still pending:** time the curation of a single DB-ALM entry end-to-end against the 3R Assist schema, then multiply by 20 to project maintenance cost. The `karynn_review_checklist.md` review process (confirming [VERIFY] fields per method) will provide this estimate as a side effect. Do not mark H5 as Tested until the per-entry time is recorded.

---

## Revision history

| Date | Module | Changes |
|---|---|---|
| *(bootstrap)* | M0 | Initialized from `project-proposal.md` section 13 |
| M3 Database | M3 | H2 and H5 status updated to "Partially addressed"; notes added with remaining steps to reach Tested |
| ADR-014 | pre-Phase 1 | H1 test description updated: added `len(experiments) > 1` pilot metric per ADR-014 |
| 2026-09 | Phase 1.5 | H3/H1 progress notes added (live reliability suite; multi-experiment UI shipped). Statuses unchanged — pilot still pending |
