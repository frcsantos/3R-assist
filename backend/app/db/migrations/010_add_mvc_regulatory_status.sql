-- =============================================================================
-- 3R Assist — Migration 010: add regulatory_status to method_validation_contexts
-- Options: not_approved | approved | recommended | mandatory
-- Column sits immediately before regulatory_body (after purpose).
-- =============================================================================

ALTER TABLE method_validation_contexts
  ADD COLUMN IF NOT EXISTS regulatory_status TEXT;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'method_validation_contexts_regulatory_status_check'
  ) THEN
    ALTER TABLE method_validation_contexts
      ADD CONSTRAINT method_validation_contexts_regulatory_status_check
      CHECK (
        regulatory_status IS NULL
        OR regulatory_status IN (
          'not_approved',
          'approved',
          'recommended',
          'mandatory'
        )
      );
  END IF;
END $$;

DO $$
DECLARE
  status_pos INT;
  body_pos INT;
BEGIN
  SELECT ordinal_position INTO status_pos
  FROM information_schema.columns
  WHERE table_schema = 'public'
    AND table_name = 'method_validation_contexts'
    AND column_name = 'regulatory_status';

  SELECT ordinal_position INTO body_pos
  FROM information_schema.columns
  WHERE table_schema = 'public'
    AND table_name = 'method_validation_contexts'
    AND column_name = 'regulatory_body';

  IF status_pos IS NULL OR body_pos IS NULL OR status_pos < body_pos THEN
    RETURN;
  END IF;

  CREATE TABLE method_validation_contexts_new (
      id                SERIAL      PRIMARY KEY,
      method_id         INTEGER     NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
      study_domain      TEXT        NOT NULL,
      jurisdiction      TEXT        NOT NULL,
      validation_status TEXT        NOT NULL,
      purpose           TEXT,
      regulatory_status TEXT,
      regulatory_body   TEXT,
      regulatory_ref    TEXT,
      regulatory_url    TEXT,
      notes             TEXT,
      created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      UNIQUE (method_id, study_domain, jurisdiction),
      CONSTRAINT method_validation_contexts_regulatory_status_check CHECK (
        regulatory_status IS NULL
        OR regulatory_status IN (
          'not_approved',
          'approved',
          'recommended',
          'mandatory'
        )
      )
  );

  INSERT INTO method_validation_contexts_new (
      id, method_id, study_domain, jurisdiction, validation_status,
      purpose, regulatory_status, regulatory_body, regulatory_ref,
      regulatory_url, notes, created_at
  )
  SELECT
      id, method_id, study_domain, jurisdiction, validation_status,
      purpose, regulatory_status, regulatory_body, regulatory_ref,
      regulatory_url, notes, created_at
  FROM method_validation_contexts;

  PERFORM setval(
      pg_get_serial_sequence('method_validation_contexts_new', 'id'),
      COALESCE((SELECT MAX(id) FROM method_validation_contexts_new), 1),
      true
  );

  DROP TABLE method_validation_contexts;
  ALTER TABLE method_validation_contexts_new RENAME TO method_validation_contexts;
  ALTER SEQUENCE method_validation_contexts_new_id_seq
      RENAME TO method_validation_contexts_id_seq;

  CREATE INDEX IF NOT EXISTS idx_mvc_method
      ON method_validation_contexts(method_id);
  CREATE INDEX IF NOT EXISTS idx_mvc_jurisdiction
      ON method_validation_contexts(jurisdiction);
  CREATE INDEX IF NOT EXISTS idx_mvc_domain_juris
      ON method_validation_contexts(study_domain, jurisdiction);
END $$;
