-- =============================================================================
-- 3R Assist — Migration 021: FK method_regulatory_contexts.study_domain
-- Align regulatory contexts with the study_domains vocabulary (same as methods).
-- =============================================================================

-- Reject orphan domain codes before adding the FK.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM method_regulatory_contexts mrc
    LEFT JOIN study_domains sd ON sd.code = mrc.study_domain
    WHERE sd.code IS NULL
  ) THEN
    RAISE EXCEPTION
      'method_regulatory_contexts.study_domain has values not present in study_domains';
  END IF;
END $$;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS fk_method_regulatory_contexts_study_domain;

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT fk_method_regulatory_contexts_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

COMMENT ON COLUMN method_regulatory_contexts.study_domain IS
  'Study domain for this validation context; FK → study_domains(code).';
