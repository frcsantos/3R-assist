-- =============================================================================
-- Migration 057: backfill methods.endpoints
-- =============================================================================

BEGIN;

UPDATE methods m
SET endpoints = v.ids
FROM (VALUES
  (1, ARRAY[10]::int[]),
  (3, ARRAY[10]::int[]),
  (4, ARRAY[10]::int[]),
  (5, ARRAY[10]::int[]),
  (6, ARRAY[14]::int[]),
  (7, ARRAY[14]::int[]),
  (8, ARRAY[14]::int[]),
  (9, ARRAY[14]::int[]),
  (10, ARRAY[20]::int[]),
  (11, ARRAY[20]::int[]),
  (12, ARRAY[20]::int[]),
  (13, ARRAY[20]::int[]),
  (14, ARRAY[20]::int[]),
  (15, ARRAY[20]::int[]),
  (16, ARRAY[12]::int[]),
  (17, ARRAY[23]::int[]),
  (18, ARRAY[23]::int[]),
  (19, ARRAY[22]::int[]),
  (20, ARRAY[48]::int[]),
  (21, ARRAY[3]::int[]),
  (22, ARRAY[17]::int[]),
  (23, ARRAY[17]::int[]),
  (24, ARRAY[17]::int[]),
  (25, ARRAY[17]::int[]),
  (30, ARRAY[54]::int[]),
  (33, ARRAY[54]::int[]),
  (34, ARRAY[54]::int[]),
  (35, ARRAY[54]::int[]),
  (36, ARRAY[25]::int[]),
  (37, ARRAY[25]::int[]),
  (38, ARRAY[48]::int[]),
  (39, ARRAY[15]::int[]),
  (40, ARRAY[14]::int[]),
  (41, ARRAY[33]::int[]),
  (42, ARRAY[33]::int[]),
  (43, ARRAY[32]::int[]),
  (44, ARRAY[34]::int[]),
  (45, ARRAY[23]::int[]),
  (46, ARRAY[23]::int[]),
  (47, ARRAY[14, 15]::int[]),
  (49, ARRAY[14, 15]::int[]),
  (50, ARRAY[37]::int[]),
  (51, ARRAY[38]::int[]),
  (53, ARRAY[38]::int[]),
  (54, ARRAY[38]::int[]),
  (55, ARRAY[38]::int[]),
  (56, ARRAY[50]::int[])
) AS v(id, ids)
WHERE m.id = v.id;

COMMIT;
