-- Rename method_regulatory_contexts → regulations.

ALTER TABLE IF EXISTS method_regulatory_contexts
  RENAME TO regulations;

ALTER SEQUENCE IF EXISTS method_regulatory_contexts_id_seq
  RENAME TO regulations_id_seq;

ALTER INDEX IF EXISTS idx_mrc_method RENAME TO idx_regulations_method;
ALTER INDEX IF EXISTS idx_mrc_jurisdiction RENAME TO idx_regulations_jurisdiction;
ALTER INDEX IF EXISTS idx_mrc_regulatory_doc RENAME TO idx_regulations_regulatory_doc;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_pkey'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT method_regulatory_contexts_pkey
      TO regulations_pkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_method_id_fkey'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT method_regulatory_contexts_method_id_fkey
      TO regulations_method_id_fkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_method_id_jurisdiction_key'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT method_regulatory_contexts_method_id_jurisdiction_key
      TO regulations_method_id_jurisdiction_key;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_validation_status_check'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT method_regulatory_contexts_validation_status_check
      TO regulations_validation_status_check;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_regulation_status_check'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT method_regulatory_contexts_regulation_status_check
      TO regulations_regulation_status_check;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'fk_mrc_regulatory_doc'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT fk_mrc_regulatory_doc
      TO fk_regulations_regulatory_doc;
  END IF;
END $$;

COMMENT ON TABLE regulations IS
  'Regulatory / validation context per method × jurisdiction.';
