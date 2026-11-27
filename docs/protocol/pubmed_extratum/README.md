# Assist3R Stratum B — PubMed random sampler v1.3 (UID partitions)

## Why v1.3?
PubMed publication dates may match both electronic and print dates. A paper can therefore appear in two disjoint *publication-date* intervals. The previous sampler correctly aborted on such overlaps, reporting `INCONSISTENT DATE PARTITION`. Do **not** disable this consistency check or accept the nonuniform date sample.

This revision applies the **same full publication-date filter (2020–2025)** in every query, but partitions the matching articles by **nonoverlapping numerical PMID/UID ranges**. Each PMID belongs to exactly one UID interval. Child counts must add up to the parent; the sampler aborts if not. The initial full-frame count must equal the count restricted to the supported UID range.

NCBI documents that PubMed EDirect now uses UID range queries to retrieve more than 10,000 results: https://ncbiinsights.ncbi.nlm.nih.gov/2022/11/22/updated-pubmed-eutilities-live/

## Run (Windows PowerShell)

1. Replace your old `pubmed_stratum_b.py` with the version in this archive.
2. Keep the fixed `query.txt` unchanged (SYRCLE + language/publication restrictions, **without** publication date restrictions).
3. Run:

```powershell
python pubmed_stratum_b.py --query-file query.txt --email YOUR_EMAIL --out stratum_B --n 40 --seed 20261113
```

Outputs when complete:
- `stratum_B_screening.csv` — citations/abstracts and manual review columns;
- `stratum_B_draw_audit.csv` — random draw offsets and UID ranges;
- `manifest.json` — full base search, date window, UID partition counts, NCBI translations, warnings, and seed.

If 40 is insufficient after eligibility screening, rerun with `--n 80` (same query, seed), and **check draw order consistency**, rather than choosing convenient replacements.

## Offline tests

```powershell
python -m unittest -v test_uid_sampler.py
```

6 new UID-partition tests cover count-weighted selection, without-replacement uniqueness, deterministic draw, nonadditive partition rejection, incomplete UID-range detection, and date/UID query composition.

## Limitations

- **No live NCBI run was performed when packaging this version**. An API incompatibility or unrecognized `[uid]` expression must be investigated; do not delete the guard checks.
- PubMed records and query translations can change over time. A fixed seed only guarantees replication with the **same PubMed index snapshot and result ordering**. Archive output artifacts.
- SYRCLE is a sensitive search filter, not an eligibility classifier. Screen selected records in draw order against the pilot protocol.
- The sample is uniform among the PubMed records matched by the frozen query *conditional on stable ESearch results, disjoint UID partitions, and stable leaf ordering*; it is not a sample of actual Assist3R users.
- Programmatic confidence in the filter is distinct from verifying that it still parses as intended. Review `manifest.json` for unmatched SYRCLE phrases and query translation.
