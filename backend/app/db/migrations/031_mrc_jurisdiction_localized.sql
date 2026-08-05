-- =============================================================================
-- Migration 031: method_regulatory_contexts.jurisdiction → localized JSONB
-- Shape: {"en-us": "...", "pt-br": "..."}
-- =============================================================================

BEGIN;

-- Collapse case-variant duplicates (e.g. brazil / Brazil) before remapping.
DELETE FROM method_regulatory_contexts mrc
USING method_regulatory_contexts keep
WHERE mrc.method_id = keep.method_id
  AND lower(btrim(mrc.jurisdiction)) = lower(btrim(keep.jurisdiction))
  AND mrc.id > keep.id;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS method_regulatory_contexts_method_id_jurisdiction_key;

DROP INDEX IF EXISTS idx_mrc_jurisdiction;
DROP INDEX IF EXISTS idx_mvc_jurisdiction;

ALTER TABLE method_regulatory_contexts
  ALTER COLUMN jurisdiction TYPE JSONB
  USING (
    CASE lower(BTRIM(jurisdiction))
      WHEN 'brazil' THEN '{"en-us":"Brazil","pt-br":"Brasil"}'::jsonb
      WHEN 'oecd' THEN '{"en-us":"OECD","pt-br":"OCDE"}'::jsonb
      WHEN 'eu' THEN '{"en-us":"EU","pt-br":"UE"}'::jsonb
      WHEN 'us' THEN '{"en-us":"US","pt-br":"EUA"}'::jsonb
      ELSE jsonb_build_object('en-us', jurisdiction, 'pt-br', jurisdiction)
    END
  );

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT method_regulatory_contexts_method_id_jurisdiction_key
  UNIQUE (method_id, jurisdiction);

CREATE INDEX idx_mrc_jurisdiction
  ON method_regulatory_contexts (jurisdiction);

COMMENT ON COLUMN method_regulatory_contexts.jurisdiction IS
  'Localized regulatory jurisdiction: {"en-us":"...","pt-br":"..."} '
  '(Brazil/Brasil, EU/UE, US/EUA, OECD/OCDE).';

COMMIT;
