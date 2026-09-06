-- =============================================================================
-- Migration 055: regulations.endpoint_quote TEXT
-- Supporting quotation for the recognized endpoints on a regulation row.
-- =============================================================================

BEGIN;

ALTER TABLE regulations
  ADD COLUMN IF NOT EXISTS endpoint_quote TEXT;

COMMENT ON COLUMN regulations.endpoint_quote IS
  'Supporting quotation (plain text) for regulatory_endpoints.';

COMMIT;
