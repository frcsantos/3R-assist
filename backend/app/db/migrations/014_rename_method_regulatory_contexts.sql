-- Rename method_validation_contexts → method_regulatory_contexts.

ALTER TABLE IF EXISTS method_validation_contexts
  RENAME TO method_regulatory_contexts;

ALTER SEQUENCE IF EXISTS method_validation_contexts_id_seq
  RENAME TO method_regulatory_contexts_id_seq;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS method_validation_contexts_regulation_status_check;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS method_validation_contexts_regulatory_status_check;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_regulation_status_check'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      ADD CONSTRAINT method_regulatory_contexts_regulation_status_check
      CHECK (
        regulation_status IS NULL
        OR regulation_status IN (
          'not_approved',
          'approved',
          'recommended',
          'mandatory'
        )
      );
  END IF;
END $$;

ALTER INDEX IF EXISTS idx_mvc_method RENAME TO idx_mrc_method;
ALTER INDEX IF EXISTS idx_mvc_jurisdiction RENAME TO idx_mrc_jurisdiction;
ALTER INDEX IF EXISTS idx_mvc_domain_juris RENAME TO idx_mrc_domain_juris;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_validation_contexts_pkey'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_validation_contexts_pkey
      TO method_regulatory_contexts_pkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_validation_contexts_method_id_fkey'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_validation_contexts_method_id_fkey
      TO method_regulatory_contexts_method_id_fkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_validation_contexts_method_id_study_domain_jurisdiction_key'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_validation_contexts_method_id_study_domain_jurisdiction_key
      TO method_regulatory_contexts_method_id_study_domain_jurisdiction_key;
  END IF;
END $$;

COMMENT ON TABLE method_regulatory_contexts IS
  'Regulatory / validation context per method × study_domain × jurisdiction.';

COMMENT ON COLUMN method_regulatory_contexts.regulation_purpose IS
  'What the method is recognized/validated for in this context (endpoint, use, or regulatory purpose).';

COMMENT ON COLUMN method_regulatory_contexts.regulation_status IS
  'Regulatory standing: not_approved | approved | recommended | mandatory.';

COMMENT ON COLUMN method_regulatory_contexts.regulation_date IS
  'Date of the regulation / recognition / adoption for this context (YYYY-MM-DD).';
