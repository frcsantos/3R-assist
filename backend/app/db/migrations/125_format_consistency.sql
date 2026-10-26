-- =============================================================================
-- Migration 125: format consistency.
--  - regulations.regulatory_body: two OECD rows (ids 47, 103) used "OECD" in
--    en-us; the other 38 use the full name -> aligned to the full name.
--  - methods.oecd_ref: '-' on the four WOAH rabies methods -> NULL
--    (docs/tables.md: NULL for non-OECD methods). The pharmacopoeia methods
--    (20, 38, 56) are already NULL.
-- =============================================================================

BEGIN;

UPDATE regulations
SET regulatory_body = jsonb_set(
      regulatory_body, '{en-us}',
      '"Organisation for Economic Co-operation and Development (OECD)"')
WHERE regulatory_body->>'en-us' = 'OECD';

UPDATE methods
SET oecd_ref = NULL
WHERE oecd_ref = '-';

COMMIT;
