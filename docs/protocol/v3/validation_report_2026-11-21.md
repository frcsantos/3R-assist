# Stratum B query v3 — live PubMed validation

Run 2026-11-21 against live PubMed (NCBI E-utilities, ESearch/ESummary via POST, generic client name, no contact email sent).
Inputs: `v3/manifest.json` (generated 2026-11-20T20:10:03Z, seed 20261113), `v3/query.txt`, `pubmed_extratum/stratum_B/stratum_B_screening.csv` (40 drawn PMIDs).
Scope: checks listed in execution log §7, items 1–2. Not a re-run of the sampler.

## Result: query behaves as designed; no defect found

| Check | Result |
|---|---|
| Manifest `query_sha256` | equals SHA-256 of `query_base` (c33d0322…). It is **not** the hash of `query.txt` (c9b4aca7…, the file hash in the log) or of `full_query`. Record both hashes. |
| Frame count | 1,323,432 now vs 1,323,438 in manifest (−6). PubMed is mutable; record the drift. |
| Translated query | identical to the manifest's `base_query_translation` (48,501 chars) |
| ESearch warnings | 13 unmatched phrases (same as manifest: poutings, chaffinchs, monotremates, coiidae, fivebeard, foulmart, foumart, grasskeet, ibices, millionfish, muguliformes, peewit, rupicapras — species names from the SYRCLE filter) and `"a beginner's guide"[Title]` not found. No field errors. |
| Drawn PMIDs inside the frame | 40 of 40 |
| Sentinel PMID 35499796 (review, pubtype Journal Article + Review) ∩ frame | 0 (correctly excluded) |
| Frame ∩ review[pt], systematic review[pt], meta-analysis[pt], editorial[pt], comment[pt], letter[pt], review[ti] | 0 each |
| Publication types of the 40 draws | 40 Journal Article; 0 Review/Meta-analysis/Editorial/Comment; 3 Preprint |
| Review-like records in the third draw | 0 of 40 (v2 draw was 40/40 review-like) |

## Things the frame still contains (by design of the query, not defects)

- Title exclusions are only the exact phrases listed at the end of `query_base`; single words are not excluded: frame ∩ overview[ti] = 229, guide[ti] = 750.
- Preprints are in the frame: 19,126 records (1.4%); 3 of the 40 draws. Includes Summers 2023 (bioRxiv, draw 36), currently `include_proposed`.
- Case reports: 16,643 records in the frame.
- Many sampled records are not experimental animal studies (surveys, chemistry, taxonomy, in vitro): abstract-level screening proposed excluding 16 of 40. The SYRCLE filter is sensitive, not specific.

## PMID 41144169 (draw 33, pubdate 2026May)

PubMed `pubdate` 2026 May, `epubdate` 2025 Oct 27. The query's `[Date - Publication]` window includes the electronic date, so PubMed correctly places it in the 2020–2025 frame (frame ∩ uid = 1). Whether to keep it is a protocol decision (frame membership vs printed date); do not drop it silently.

## Not verified here

- UID-partition additivity and coverage (recorded in `consistency_checked_splits` in the manifest; not re-run).
- Uniformity of the draw and reproducibility of seed 20261113 (would need a sampler re-run; the index has drifted by 6 records).
- Whether to freeze: manifest status is still `unverified_candidate_draw`.
