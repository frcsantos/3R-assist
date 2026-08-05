-- Rename MVC purpose/regulatory_status and reorder regulation columns.
-- Target order after validation_status:
--   regulation_status, regulation_date, regulation_purpose, regulatory_body, ...

ALTER TABLE method_validation_contexts
  DROP CONSTRAINT IF EXISTS method_validation_contexts_regulatory_status_check;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'method_validation_contexts'
      AND column_name = 'purpose'
  ) AND NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'method_validation_contexts'
      AND column_name = 'regulation_purpose'
  ) THEN
    ALTER TABLE method_validation_contexts
      RENAME COLUMN purpose TO regulation_purpose;
  END IF;

  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'method_validation_contexts'
      AND column_name = 'regulatory_status'
  ) AND NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'method_validation_contexts'
      AND column_name = 'regulation_status'
  ) THEN
    ALTER TABLE method_validation_contexts
      RENAME COLUMN regulatory_status TO regulation_status;
  END IF;
END $$;

ALTER TABLE method_validation_contexts
  DROP CONSTRAINT IF EXISTS method_validation_contexts_regulation_status_check;

ALTER TABLE method_validation_contexts
  ADD CONSTRAINT method_validation_contexts_regulation_status_check
  CHECK (
    regulation_status IS NULL
    OR regulation_status IN (
      'not_approved',
      'approved',
      'recommended',
      'mandatory'
    )
  );

CREATE TABLE method_validation_contexts_new (
    id                 SERIAL      PRIMARY KEY,
    method_id          INTEGER     NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    study_domain       TEXT        NOT NULL,
    jurisdiction       TEXT        NOT NULL,
    validation_status  TEXT        NOT NULL,
    regulation_status  TEXT,
    regulation_date    DATE,
    regulation_purpose TEXT,
    regulatory_body    TEXT,
    regulatory_url     TEXT,
    notes              TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (method_id, study_domain, jurisdiction),
    CONSTRAINT method_validation_contexts_regulation_status_check CHECK (
      regulation_status IS NULL
      OR regulation_status IN (
        'not_approved',
        'approved',
        'recommended',
        'mandatory'
      )
    )
);

INSERT INTO method_validation_contexts_new (
    id, method_id, study_domain, jurisdiction, validation_status,
    regulation_status, regulation_date, regulation_purpose,
    regulatory_body, regulatory_url, notes, created_at
)
SELECT
    id, method_id, study_domain, jurisdiction, validation_status,
    regulation_status, regulation_date, regulation_purpose,
    regulatory_body, regulatory_url, notes, created_at
FROM method_validation_contexts;

DO $$
BEGIN
  PERFORM setval(
      pg_get_serial_sequence('method_validation_contexts_new', 'id'),
      COALESCE((SELECT MAX(id) FROM method_validation_contexts_new), 1),
      true
  );
END $$;

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

COMMENT ON COLUMN method_validation_contexts.regulation_purpose IS
  'What the method is recognized/validated for in this context (endpoint, use, or regulatory purpose).';

COMMENT ON COLUMN method_validation_contexts.regulation_status IS
  'Regulatory standing: not_approved | approved | recommended | mandatory.';

COMMENT ON COLUMN method_validation_contexts.regulation_date IS
  'Date of the regulation / recognition / adoption for this context (YYYY-MM-DD).';
