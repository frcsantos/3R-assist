# Assist3R — Pilot execution log: Basket 1, Stratum B

**Log version:** 1.0  
**Compiled:** 2026-11-20  
**Protocol:** *Protocolo Piloto de Calibração e Validação*, v2.3, dated 2026-11-06  
**Scope:** Collection and sampling of published animal-experiment source articles for Stratum B; related context for Basket 1  
**Record status:** Retrospective reconstruction from conversation, attached code, search files, CSVs and audit notes. **Not** a completed validation report.

> **Evidentiary convention:** **Observed** = supported by attached file, provided traceback or recorded execution output; **reported** = prior conversation claim without independent raw run log; **hypothesis** = potential explanation not verified by live NCBI query translation; **pending** = not yet done. File modification/mount timestamps are not treated as sampling dates.

## 1. Aim and prespecified sampling rules

The pilot prescribes **20 eligible Stratum B procedures** sampled from a frozen PubMed animal-literature frame (2020–2025 proposed), with 40 PMIDs initially drawn, eligibility screened **in random order**, logging all exclusions; procedures must have identifiable aim/endpoints, accessible Methods, and English/Portuguese text. Stratum B is explicitly a *publication proxy*, **not** a representative sample of real Assist3R user queries. It will contribute 20 of Basket 1's 55 cases (20 A, 20 B, 15 C), each to be matched against 47 catalog methods. Method-directed Stratum A sampling is separate.

### Design adopted in conversation

- Search: updated SYRCLE PubMed animal literature filter (2021 source PDF), expanded with English/Portuguese, `journal article` publication type, and later review-related exclusions.
- Period added by script: publication dates 2020-01-01 through 2025-12-31 (inclusive).
- Initial draw: 40 distinct PMIDs; seed **20261113**. Extend the ordered draw if 20 eligible studies are not found.
- Source unit: select one qualifying animal procedure per included article where practical; source/laboratory-project duplicates must be tracked.
- The PubMed sampling frame is **conditional on query interpretation and the index at the time of execution**. No PubMed snapshot was archived in files supplied for this log.

## 2. Chronological execution and decisions

Exact dates for every failed run are **not established** from the uploaded logs; the sequence is reconstructed from the conversation. The diagnostic v3 document itself is dated 2026-11-20.

| Seq. | Event | Evidence and outcome | Status / consequence |
|---:|---|---|---|
| 1 | Scope chosen | User chose automated probability sampling for B over handpicked papers. | Design decision |
| 2 | Initial collector | `assist3r_stratum_B_pubmed_sampler.zip`: basic seeded sampler; original example query explicitly **not** validated SYRCLE. | Superseded |
| 3 | SYRCLE query supplied | `PubMed.pdf` contains the complete long animal filter; user created `Pasted text(1).txt` with language and publication restrictions. | Source retained |
| 4 | HTTP 414 | User traceback: `urllib.error.HTTPError: HTTP Error 414: Request-URI Too Long`, during `esearch.fcgi` request. | Observed failure |
| 5 | POST transport patch | `assist3r_stratum_B_pubmed_sampler_POST_fix.zip` changed long searches to HTTP POST. Previous assistant reported 6/6 offline tests. | Observed artifact; offline-test count reported |
| 6 | Unrecognized phrases | User traceback listed 13 `phrasesnotfound` (e.g. `poutings`, `chaffinchs`, `monotremates`, `millionfish`). | Observed error response |
| 7 | Phrase-warning patch | `...phrase_fix.zip` downgraded unmatched terms to logged warnings where a valid count/translation exists; other query errors still fatal. Previous assistant reported 8/8 offline tests. | Observed artifact; semantic effect on query must be recorded |
| 8 | Boolean grouping fix | `assist3r_stratum_B_query_fixed.txt` enclosed the full OR filter and included publication restrictions. It contained `AND NOT (...)`. | Query artifact preserved; live equivalence not verified |
| 9 | Date-partition failure | User traceback: full 2020–2025 count **214,453**, child counts **98,088 + 118,963 = 217,051**, excess **2,598**. The sampler aborted. | Observed failure; no valid date-partition sample |
| 10 | UID-range sampler v1.3 | `...UID_fix_v1_3.zip` uses nonoverlapping numerical PMID ranges while keeping the publication-date filter constant. It checks count additivity and UID-frame coverage. Previous assistant reported 10/10 offline tests. | Current sampling implementation; live behavior inferred from successful CSV production |
| 11 | First successful 40-record draw | `stratum_B_screening.csv`: **40 rows; 40 unique PMIDs**; screening fields all pending. | Observed records; full inclusion not assessed |
| 12 | Preliminary automated screening | `stratum_B_preliminary_screened.csv` initially classed 39 as likely excludes and 1 as needs-full-text. | **Superseded as too categorical**, not expert screening |
| 13 | Revised initial-draw diagnosis | `stratum_B_query_diagnostic_v2.md`: 16 self-identified reviews in abstract, 9 explicit review-like titles, 14 needing manual review, 1 likely primary; **zero full-text-verified eligible**. | Best available provisional triage; not a validated eligibility count |
| 14 | Query v2 | `stratum_B_query_v2_title_exclusions.txt` added review/overview/guide title exclusions on top of publication-type exclusions. It used `AND NOT` twice. | New sampling frame; unvalidated change |
| 15 | Second 40-record draw | `stratum_B_screening(1).csv`: **40 rows; 40 unique PMIDs**; **40/40** have review-like wording by local title detector. Screening remains pending in CSV. | Observed anomaly; not suitable for inclusion yet |
| 16 | Query v3 correction proposed | `stratum_B_query_v3_boolean_fix.txt` replaces both `AND NOT` forms with binary `NOT` and retains exclusions. `stratum_B_query_audit_v3.md` calls incorrect Boolean parsing a **hypothesis**, not proven cause. | **Pending live query sanity test**; no v3 draw on record |

## 3. Search strategy and version control

| Query ID | File | Change from prior query | Evidentiary status |
|---|---|---|---|
| Early user query | `Pasted text(1).txt` | Complete copied SYRCLE with English/Portuguese and journal-article restriction, plus publication-type `NOT` | User-supplied, pre-grouping version |
| B-v1 fixed | `assist3r_stratum_B_query_fixed.txt` | Added outer parentheses; contained `AND NOT` review publication-type exclusions | Original sampled search **appears** related, but query–draw linkage cannot be proven without original manifest |
| B-v2 | `stratum_B_query_v2_title_exclusions.txt` | Adds explicit review/meta-analysis/overview/guide **title** exclusions; two `AND NOT` constructs | Candidate new frame; second sample associated by conversation |
| B-v3 | `stratum_B_query_v3_boolean_fix.txt` | Converts `AND NOT` to `NOT` for both exclusion blocks | **Proposed**, no observed ESearch validation or draw |

**Important:** The exact binary `NOT` interpretation in long PubMed searches must be confirmed using the server-returned query translation and known excluded PMIDs. The 40/40 review-heavy v2 result strongly signals a serious mismatch, but **does not prove that `AND NOT` alone caused it**. Avoid promoting that hypothesis to a confirmed root cause in publication.

**Filter limitations:** SYRCLE is designed for sensitive retrieval of animal-related literature, not proof that each record reports an original *in vivo* experiment. Article type metadata and title exclusion filters can exclude eligible original research or retain reviews. Captured records therefore describe the selected PubMed *search frame*, not all experimental-animal publications.

## 4. Observed sampling data and screening

| Audit statistic | Initial draw | Second draw |
|---|---:|---:|
| CSV rows | 40 | 40 |
| Distinct PMIDs | 40 | 40 |
| Records currently marked `pending` in original CSV | 40 | 40 |
| Titles matching *local indicative detector* `review/reviews/overview/meta-analysis/beginner's guide` | 9 | 40 |
| Verified eligible animal procedures by full Methods review | **0 documented** | **0 documented** |

The review-like title detector is a coarse local regex, **not** the PubMed title filter nor a reliable study-type label. The initial diagnostic counted 9 explicit review-like titles and 16 review-indicative abstracts; an earlier v3 audit used a narrower title detector (8/40), explaining small discrepancies in reported title counts. Do not use 39/40 as a confirmed exclusion rate.

**Initial draw manual follow-up priority (not yet completed):** draw #40, PMID **41083088**, was flagged as likely original experimental work; Methods must verify any live-animal procedure and full-text access. Draw #28, PMID **40201819**, appears observational/veterinary, not a qualifying experimental animal procedure; draw #34, PMID **32131674**, needs clarification whether there is a qualifying *in vivo* procedure rather than solely cell research. Other uncertain records should not be permanently excluded based only on the preliminary CSV.

The second draw's PMID **35499796** (review title) was proposed as a *negative control* for testing v3 query exclusion. It has not been documented as tested.

## 5. Software and reproducibility conditions

- Original and patched sampler archives are listed in the artifact manifest below.
- v1.3 calls NCBI ESearch with long terms via POST, applies a fixed publication-date window, and partitions on disjoint UID ranges; checks parent/child count consistency and full UID-range count coverage; draws PMIDs with `random.Random(20261113)`.
- The scripts' sampling claims depend on stable NCBI counts, query semantics and consistent result ordering. Duplicate draws are rejected. A fixed seed **alone is insufficient** for exact reruns against a changing PubMed index.
- Standard command used in previous instructions (replace email and output path):

```powershell
python pubmed_stratum_b.py --query-file query.txt --email YOUR_EMAIL --out stratum_B --n 40 --seed 20261113
```

- **Not present in materials for this reconstruction:** live `manifest.json`, draw-audit CSV(s), complete server-side translated query, timestamped execution logs, and the precise exact query file used during each run. These should be retrieved from the user's local `stratum_B*` output folders before the study report is finalized.
- Offline tests were reported for successive versions; they **are not** evidence that the live PubMed search semantics were correct. No live NCBI calls were executed while compiling this log.

## 6. Deviations, corrective actions, and reporting risks

| Issue | Impact | Action/status |
|---|---|---|
| Example filter was illustrative | Could define the wrong target population if used for data collection | Replaced with user-supplied complete SYRCLE filter; compare official source text |
| HTTP GET query too long (414) | Search failed | POST patch provided |
| PubMed unmatched words | Search parser diagnostics interrupted collection | Warning-logging patch; preserve translations and exact unmatched terms |
| Overlapping date partitions | Invalidates date-based uniformity claim | Aborted; changed to PMID ranges with additivity checks |
| First sample review-heavy | Large screening effort; unclear original-study eligibility | Retain 40 in draw order; re-screen uncertain cases rather than count blanket exclusions |
| Query v2 all review-like titles | Major search interpretation/frame concern | Quarantine draw; verify v3 with negative controls before any new draw |
| Repeated query edits | Selection bias / post hoc population changes | Treat each as a distinct query version and frame, with clear exploratory vs final sampling |
| Missing query/run manifest | Limits audit of exact live search | Recover manifest, draw-audit file and run timestamp from local machine |
| No full Methods screening | Cannot claim 20 eligible B cases | Perform independent eligibility check and capture reasons |

## 7. Conditions to restart and freeze Stratum B

1. **Freeze query v3 only after validation**, without unrecorded edits. Save its exact bytes, hash, PubMed ESearch `querytranslation`/warnings, full count, UTC timestamp, date window and sampler script hash.
2. Check excluded sentinel **PMID 35499796** by applying the full query plus UID constraint. Confirm `review[Title]` intersection gives zero (subject to PubMed's actual field behavior). Also check a known included primary animal experiment to avoid an unintentionally empty/overrestrictive frame.
3. Check UID partition additivity and total UID-frame coverage; retain `manifest.json` and draw-audit CSV.
4. Draw 40 unique PMIDs, preserve random order, screen **all** sampled records until 20 genuinely eligible animal procedures. Continue the same draw sequence if needed; maintain exclusions and source-group deduplication.
5. Preserve Methods passages, PMIDs/DOIs, study aims, endpoints, language, full-text access provenance and selected procedure spans. Do not treat automatic abstracts as final expert screening.
6. For the extraction benchmark, reserve 10 development and 20 held-out reference procedures **across A/B/C**; the full 20 B cases are not all necessarily benchmark-reference cases. Avoid leakage by article or source group.

## 8. Current status and report-ready statement

**As of 2026-11-20:** Two 40-record PubMed CSVs were generated, with no duplicate PMIDs within either file. Both retain `pending` human-screening status. The first draw produced many review-like articles; automated exclusion of 39 papers was revised as overconfident. The second draw yielded 40/40 titles matching an indicative review detector, prompting investigation of Boolean query semantics. An updated v3 query has been authored but **has not been confirmed against live PubMed or sampled successfully in the supplied evidence**. No Stratum B article has yet been established as eligible through examination of its full Methods section.

> **Suggested methods-report wording:** “We developed a reproducible PubMed sampling workflow using the updated SYRCLE animal-literature search filter, publication/language restrictions, seeded random selection, and disjoint PMID-range partitioning. Early runs exposed server constraints (long URL requests, unmatched query phrases) and invalid date-partition assumptions caused by possible duplicate publication-date indexing. Two exploratory 40-record draws revealed unexpectedly high review-like content and motivated query-semantics checks. We retained these iterations in the audit trail and did not include unverified records in the final evaluation sample.”

## 9. Artifact manifest (files available at log compilation)

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `Protocolo de teste piloto v2_3 (1)(1).md` | 23,311 | `2cfcc4854d9bfdb36a50973e744f12a33903dafcf67e9d24aa04abc701e4eb58` |
| `Tabelas (9).xlsx` | 320,129 | `59b547f1e3fcc38b6d2857c1c7aad358d318d34a4357d00ea782c635e4021668` |
| `assist3r_basket1_execution_ledger_v0_1.md` | 7,484 | `9304e28b2224302c72e6624fbe8c9d7d39ad776a46000bfc9fa6b07bc66e90e2` |
| `PubMed.pdf` | 72,151 | `828cc638e11236de1fa2663ce738cf4fbb9e1dae8ea04bab8c79e065e4285569` |
| `Pasted text(1).txt` | 28,175 | `a50c333b6b8573c5d93faa65252eb69c9e2ab16a35beb91e1ead4c8b6fb9eada` |
| `assist3r_stratum_B_query_fixed.txt` | 27,940 | `8d037e2a41da1c831c24f1b1de55abaf0697eb58dcc504b29c7e6181b4870639` |
| `stratum_B_query_v2_title_exclusions.txt` | 28,257 | `43a1f6ec7a5201e1d1d11dc9631b92b2aada1265b903f21da3e6d52711c49add` |
| `stratum_B_query_v3_boolean_fix.txt` | 28,249 | `c9b4aca716229eb5be3c9e82d02bb4f5090e3e14f3403b6515b36b2f616bfc37` |
| `stratum_B_screening.csv` | 65,297 | `bc5574365111956eed418be7630e98325e696647700c0ff0c130847092ec289c` |
| `stratum_B_screening(1).csv` | 70,860 | `cfafc8c5858c6c6857a954c202c9f5fd7e35f24e0e84383968bb78418de2be86` |
| `stratum_B_preliminary_screened.csv` | 71,762 | `890f191b95d3f6bed9b85e982a15f43e427b79bd73ffc78f47c1fd3b451185f2` |
| `stratum_B_query_diagnostic_v2.md` | 9,261 | `e9417c10948c4421533b44b05c8c398c2e915307177f75899ef50f8ca0f9ae47` |
| `stratum_B_query_audit_v3.md` | 2,202 | `e216c9faf89d9520a8ec5ab65d003fb06f2c458b7e601e333ab1466dd18621dc` |
| `assist3r_stratum_B_pubmed_sampler.zip` | 7,734 | `ceda5f10c71f49145162ce7db34ec4a2276ab9300044b7feccbdaa4edcce7eaf` |
| `assist3r_stratum_B_pubmed_sampler_POST_fix.zip` | 8,338 | `3a03cf56752d25593b9b157de984aeeb0485c7340cc72620faed6e2bd278ae51` |
| `assist3r_stratum_B_pubmed_sampler_phrase_fix.zip` | 8,965 | `9537d4aab40f61d4e820a53f2ffa1b210309a77274da12bfc266100f0698b3a0` |
| `assist3r_stratum_B_pubmed_sampler_UID_fix_v1_3.zip` | 9,504 | `dece6fde4b5290833ff39c3e9c559c4d40ed5facf9e43d5fced2799672a9e689` |

### Missing artifacts to preserve as soon as available

- Live `manifest.json` for each successful draw, including complete frozen query and translated query.
- `*_draw_audit.csv` output for each draw (partition ranges and offsets).
- Screened decision logs with dates and reviewer identities (or blinded IDs).
- Original Methods/full-text source evidence, plus copyright/access metadata.
- A changelog tying every run explicitly to a query hash and a sampler archive.

### Relation to the rest of the pilot

Stratum A's 20-method provisional stratified selection is described separately in `assist3r_basket1_execution_ledger_v0_1.md`; it is **not** evidence of collected experimental articles. P2 was selected as the intended richer extraction schema; the user is implementing it. No comparison of DeepSeek Flash vs Claude Sonnet or reference extractions has been run as part of this record. Final B1 evaluation requires full case collection, frozen method database, model executions and independent expert labels.


---

## 10. Update — 2026-11-20: Third draw (candidate query v3) and source-method follow-up

**Inputs:** `stratum_B_screening(2).csv` (40 distinct PMIDs in recorded draw order), `stratum_B_v3_abstract_triage.csv`. The v3 run manifest and draw audit have not been supplied, so the exact live query translation, partition count, seed actually used and software identity are **not independently verified** from the run outputs. Do not treat this sample as a frozen final probability sample until those records are preserved.

**Abstract-level triage:** 20 likely in-vivo experimental cases, 2 uncertain, 18 likely exclusions. These are not human-confirmed eligibility decisions. The current source-method audit located method-level animal evidence for 10 records and support for animal procedures but incomplete individual-procedure selection for 2 more; 8 abstract-positive cases remain to be checked at source-method level.

**Source methods supported:** draw #1 (RapidCaP mouse prostate cancer imaging), #3 (rat induced EAE, treatment regimens), #7 (mouse bile duct ligation), #9 (Prrx1 mouse genetic lineage tracing), #15 (mouse ovarian xenografts), #20 (beagle surgical force), #23 (rat hypoxic-hypercapnic challenge), #27 (mouse inflammatory pain model), #28 (dietary mouse MASH model), #32 (mouse intracardiac cell injection and PET). See `stratum_B_v3_fulltext_followup.csv` for references and evidence notes. Draw #31 (CART-amygdala animal experiment) and #40 (mouse bleomycin fibrosis) are supported as animal experimental studies but specific case boundaries and source methods need closer verification. These are **source-evidence milestones**, not final included cases: exact Methods passages, source group independence, publication eligibility and selected protocol still need review.

**Critical date inconsistency:** draw #33 (PMID 41144169) has `pubdate = 2026May` even though the claimed sampler window is 2020–2025. This may reflect the distinction between PubMed publication-date indexing and displayed date; whether it is eligible cannot be resolved from CSV alone. Verify the PubMed translation, record dates and the actual query predicate. Do not drop/reassign this PMID without documenting the rationale.

**Next:** (1) obtain the v3 manifest/draw audit; (2) resolve date discrepancy; (3) complete full Methods inspection for all 40 records in draw order, including provisional exclusions, and record one identified procedure per included article; (4) require accessible source text and source-group deduplication before human marking of `include`; (5) continue identical frozen random draw sequence if fewer than 20 qualify. No definitive final eligible count claimed yet.

**Reproducible follow-up:** `stratum_B_v3_fulltext_followup.csv`, preserving original fields and appending `followup_evidence_status`, `followup_evidence_summary`, `followup_source_url`, `final_human_eligibility`, `selected_procedure_text_status`, and `date_range_flag`.


## Addendum — 2026-11-20: source retrieval extension

Further searches against the frozen third draw produced an additional `stratum_B_v3_source_retrieval_audit_v1.csv` and `.md` with the original randomized order preserved. Fourteen sampled articles have accessible original article pages and identifiable animal procedures, while seven further candidates remain abstract-supported without original full Methods retrieval. One date-discrepancy record remains on hold. These are **source leads**, not 14 formally accepted cases; original Methods texts still need to be frozen locally and a final human eligibility check applied. No claim is made that complete copyrighted Methods sections were downloaded.

This addendum supersedes any earlier assumption that source availability or the abstract triage score establishes final eligibility.
