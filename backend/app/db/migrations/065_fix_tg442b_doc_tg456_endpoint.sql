-- =============================================================================
-- Migration 065: fix TG 442B regulatory doc link and TG 456 method endpoint
--
-- 1. The OECD regulation row for TG 442B (LLNA: BrdU-ELISA) pointed at
--    documents.id = 9, which is the TG 492B (RHCE eye hazard) document.
--    Re-point it to documents.id = 25 (Test No. 442B) and refresh
--    regulatory_date, which was backfilled from the old document (047).
--
-- 2. methods.endpoints for TG 456 (H295R Steroidogenesis Assay) was [32]
--    ("Endocrine activity", the generic parent). Correct it to [36]
--    (Steroidogenesis activity), matching its OECD regulation row.
-- =============================================================================

BEGIN;

UPDATE regulations r
SET
  regulatory_doc_id = 25,
  regulatory_date = '2025-06-25'
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 442B'
  AND r.jurisdiction->>'en-us' = 'OECD'
  AND r.regulatory_doc_id = 9;

UPDATE methods
SET endpoints = ARRAY[36]
WHERE oecd_ref = 'TG 456'
  AND endpoints = ARRAY[32];

COMMIT;
