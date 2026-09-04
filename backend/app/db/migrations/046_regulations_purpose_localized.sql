-- =============================================================================
-- Migration 046: regulations.regulation_purpose → localized JSONB
-- Shape: {"en-us": "...", "pt-br": "..."}
-- =============================================================================

BEGIN;

ALTER TABLE regulations
  ALTER COLUMN regulation_purpose TYPE JSONB
  USING (
    CASE
      WHEN regulation_purpose IS NULL OR BTRIM(regulation_purpose) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', regulation_purpose,
        'pt-br', regulation_purpose
      )
    END
  );

COMMENT ON COLUMN regulations.regulation_purpose IS
  'Localized recognition purpose: {"en-us":"...","pt-br":"..."}.';

COMMIT;
