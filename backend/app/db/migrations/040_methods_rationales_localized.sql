-- =============================================================================
-- Migration 040: methods.*_rationale TEXT → localized JSONB
-- Shape: {"en-us": "...", "pt-br": "..."}  (NULL = does not qualify for that R)
-- =============================================================================

BEGIN;

ALTER TABLE methods
  ALTER COLUMN replacement_rationale TYPE JSONB
  USING (
    CASE
      WHEN replacement_rationale IS NULL OR BTRIM(replacement_rationale) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', replacement_rationale,
        'pt-br', replacement_rationale
      )
    END
  );

ALTER TABLE methods
  ALTER COLUMN reduction_rationale TYPE JSONB
  USING (
    CASE
      WHEN reduction_rationale IS NULL OR BTRIM(reduction_rationale) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', reduction_rationale,
        'pt-br', reduction_rationale
      )
    END
  );

ALTER TABLE methods
  ALTER COLUMN refinement_rationale TYPE JSONB
  USING (
    CASE
      WHEN refinement_rationale IS NULL OR BTRIM(refinement_rationale) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', refinement_rationale,
        'pt-br', refinement_rationale
      )
    END
  );

COMMENT ON COLUMN methods.replacement_rationale IS
  'Localized replacement rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as replacement (ADR-023).';
COMMENT ON COLUMN methods.reduction_rationale IS
  'Localized reduction rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as reduction.';
COMMENT ON COLUMN methods.refinement_rationale IS
  'Localized refinement rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as refinement.';

COMMIT;
