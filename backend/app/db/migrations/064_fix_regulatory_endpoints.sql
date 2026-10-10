-- =============================================================================
-- Migration 064: correct endpoint values on regulations and methods
--
-- Data correction per curation sheet review (2026-09-04). Each UPDATE is
-- guarded by the current value so the migration is idempotent and only
-- touches rows that still hold the old, incorrect endpoints.
--
-- regulations.regulatory_endpoints (OECD rows from sheet):
--   TG 439 [14]→[10] | TG 460 [22]→[14] | TG 492 [17]→[14]
--   TG 442E [12]→[20] | TG 429 [25]→[20] | TG 442B [48]→[20]
--   TG 432 [10]→[12] | TG 471 [3]→[23] | TG 476 [17]→[23]
--   TG 487 [17]→[22] | TG 428 [25]→[3] | TG 420 [14]→[17]
--   TG 423 [20]→[17] | TG 425 [20]→[17] | GD 129 [14]→[17]
--   TG 421 [38]→[25,26] | TG 492B [48]→[15] | TG 455 [17]→[33]
--   TG 493 [23]→[33] | TG 456 [23]→[36] | TG 458 [33]→[34]
--   TG 473 [32]→[23] | TG 490 [33]→[23] | TG 494 [23]→[14,15]
--   TG 496 [23]→[14,15] | TG 495 [14,15]→[37] | TG 212 [14,15]→[41]
--   TG 236 [37]→[41] | TG 422 [38]→[18,25,26] | TG 491 NULL→[14]
--
-- regulations.regulatory_endpoints (remaining rows flagged in sheet):
--   TG 421 [25]→[25,26] | TG 422 [25]→[18,25,26]
--   TG 212 [38]→[41] | TG 236 [38]→[41]
--   TG 319A [38]→[5] | TG 319B [38]→[5]
--
-- methods.endpoints:
--   TG 421 [25]→[25,26] | TG 422 [25]→[18,25,26]
--   TG 212 [38]→[41] | TG 236 [38]→[41]
--   TG 319A [38]→[5] | TG 319B [38]→[5]
-- =============================================================================

BEGIN;

-- ── regulations: OECD rows (sheet, first table) ────────────────────────────

UPDATE regulations r
SET regulatory_endpoints = ARRAY[10]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 439'
  AND r.regulatory_endpoints = ARRAY[14];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[14]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 460'
  AND r.regulatory_endpoints = ARRAY[22];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[14]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 492'
  AND r.regulatory_endpoints = ARRAY[17];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[20]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 442E'
  AND r.regulatory_endpoints = ARRAY[12];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[20]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 429'
  AND r.regulatory_endpoints = ARRAY[25];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[20]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 442B'
  AND r.regulatory_endpoints = ARRAY[48];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[12]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 432'
  AND r.regulatory_endpoints = ARRAY[10];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[23]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 471'
  AND r.regulatory_endpoints = ARRAY[3];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[23]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 476'
  AND r.regulatory_endpoints = ARRAY[17];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[22]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 487'
  AND r.regulatory_endpoints = ARRAY[17];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[3]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 428'
  AND r.regulatory_endpoints = ARRAY[25];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[17]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 420'
  AND r.regulatory_endpoints = ARRAY[14];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[17]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 423'
  AND r.regulatory_endpoints = ARRAY[20];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[17]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 425'
  AND r.regulatory_endpoints = ARRAY[20];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[17]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'GD 129'
  AND r.regulatory_endpoints = ARRAY[14];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[25, 26]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 421'
  AND r.regulatory_endpoints = ARRAY[38];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[15]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 492B'
  AND r.regulatory_endpoints = ARRAY[48];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[33]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 455'
  AND r.regulatory_endpoints = ARRAY[17];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[33]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 493'
  AND r.regulatory_endpoints = ARRAY[23];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[36]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 456'
  AND r.regulatory_endpoints = ARRAY[23];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[34]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 458'
  AND r.regulatory_endpoints = ARRAY[33];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[23]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 473'
  AND r.regulatory_endpoints = ARRAY[32];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[23]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 490'
  AND r.regulatory_endpoints = ARRAY[33];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[14, 15]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 494'
  AND r.regulatory_endpoints = ARRAY[23];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[14, 15]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 496'
  AND r.regulatory_endpoints = ARRAY[23];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[37]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 495'
  AND r.regulatory_endpoints = ARRAY[14, 15];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[41]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 212'
  AND r.regulatory_endpoints = ARRAY[14, 15];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[41]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 236'
  AND r.regulatory_endpoints = ARRAY[37];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[18, 25, 26]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 422'
  AND r.regulatory_endpoints = ARRAY[38];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[14]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 491'
  AND r.regulatory_endpoints IS NULL;

-- ── regulations: remaining rows flagged in sheet (second table) ────────────

UPDATE regulations r
SET regulatory_endpoints = ARRAY[25, 26]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 421'
  AND r.regulatory_endpoints = ARRAY[25];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[18, 25, 26]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 422'
  AND r.regulatory_endpoints = ARRAY[25];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[41]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 212'
  AND r.regulatory_endpoints = ARRAY[38];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[41]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 236'
  AND r.regulatory_endpoints = ARRAY[38];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[5]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 319A'
  AND r.regulatory_endpoints = ARRAY[38];

UPDATE regulations r
SET regulatory_endpoints = ARRAY[5]
FROM methods m
WHERE r.method_id = m.id
  AND m.oecd_ref = 'TG 319B'
  AND r.regulatory_endpoints = ARRAY[38];

-- ── methods.endpoints ──────────────────────────────────────────────────────

UPDATE methods SET endpoints = ARRAY[25, 26]
WHERE oecd_ref = 'TG 421' AND endpoints = ARRAY[25];

UPDATE methods SET endpoints = ARRAY[18, 25, 26]
WHERE oecd_ref = 'TG 422' AND endpoints = ARRAY[25];

UPDATE methods SET endpoints = ARRAY[41]
WHERE oecd_ref = 'TG 212' AND endpoints = ARRAY[38];

UPDATE methods SET endpoints = ARRAY[41]
WHERE oecd_ref = 'TG 236' AND endpoints = ARRAY[38];

UPDATE methods SET endpoints = ARRAY[5]
WHERE oecd_ref = 'TG 319A' AND endpoints = ARRAY[38];

UPDATE methods SET endpoints = ARRAY[5]
WHERE oecd_ref = 'TG 319B' AND endpoints = ARRAY[38];

COMMIT;
