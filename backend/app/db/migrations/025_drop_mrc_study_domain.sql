-- =============================================================================
-- Migration 025: Drop study_domain from method_regulatory_contexts
-- Contexts are scoped by method × jurisdiction only (study_domain stays on methods).
-- =============================================================================

BEGIN;

-- Collapse duplicate (method_id, jurisdiction) rows before dropping study_domain.
-- Prefer study_domain = 'general', then lowest id.
CREATE TEMP TABLE mrc_keep ON COMMIT DROP AS
SELECT DISTINCT ON (method_id, jurisdiction)
    id
FROM method_regulatory_contexts
ORDER BY
    method_id,
    jurisdiction,
    (study_domain = 'general') DESC,
    id ASC;

DELETE FROM method_regulatory_contexts
WHERE id NOT IN (SELECT id FROM mrc_keep);

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS fk_method_regulatory_contexts_study_domain;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS method_regulatory_contexts_method_id_study_domain_jurisdiction_key;

DROP INDEX IF EXISTS idx_mvc_domain_juris;

ALTER TABLE method_regulatory_contexts
  DROP COLUMN IF EXISTS study_domain;

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT method_regulatory_contexts_method_id_jurisdiction_key
  UNIQUE (method_id, jurisdiction);

COMMENT ON TABLE method_regulatory_contexts IS
  'Regulatory / validation context per method × jurisdiction.';

COMMIT;
