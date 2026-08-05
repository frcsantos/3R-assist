-- =============================================================================
-- Migration 028: document FKs on methods + method_regulatory_contexts
-- methods: drop source_url/source_date; add source_doc_id after source_citation
-- method_regulatory_contexts: add regulatory_doc_id after regulatory_body;
--   replace regulatory_url with regulatory_citation
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Drop FKs that reference methods(id)
-- ---------------------------------------------------------------------------

DO $$
DECLARE
  rec record;
BEGIN
  FOR rec IN
    SELECT con.conname, rel.relname AS table_name
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class ref ON ref.oid = con.confrelid
    WHERE con.contype = 'f'
      AND ref.relname = 'methods'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I DROP CONSTRAINT IF EXISTS %I',
      rec.table_name,
      rec.conname
    );
  END LOOP;
END $$;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_endpoint_category;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_study_domain;

-- ---------------------------------------------------------------------------
-- Rebuild methods
-- ---------------------------------------------------------------------------

CREATE TABLE methods_new (
    id                     SERIAL      PRIMARY KEY,
    slug                   TEXT        NOT NULL UNIQUE,
    active                 BOOLEAN     NOT NULL DEFAULT FALSE,
    name                   JSONB       NOT NULL,
    description            JSONB       NOT NULL,
    endpoint_category      TEXT        NOT NULL,
    routes_applicable      JSONB,
    study_domain           TEXT        NOT NULL,
    oecd_ref               TEXT,
    ncit_id                TEXT,
    source_citation        TEXT,
    source_doc_id          INTEGER     REFERENCES documents(id) ON DELETE SET NULL,
    source_db              TEXT        NOT NULL,
    replacement_rationale  TEXT,
    reduction_rationale    TEXT,
    refinement_rationale   TEXT,
    keywords               JSONB       NOT NULL DEFAULT '{"en-us": [], "pt-br": []}'::jsonb,
    text_for_embedding     TEXT        NOT NULL,
    embedding_json         JSONB,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO methods_new (
    id, slug, active, name, description,
    endpoint_category, routes_applicable, study_domain,
    oecd_ref, ncit_id, source_citation, source_db,
    replacement_rationale, reduction_rationale, refinement_rationale,
    keywords, text_for_embedding, embedding_json, created_at, updated_at
)
SELECT
    id, slug, active, name, description,
    endpoint_category, routes_applicable, study_domain,
    oecd_ref, ncit_id, source_citation, source_db,
    replacement_rationale, reduction_rationale, refinement_rationale,
    keywords, text_for_embedding, embedding_json, created_at, updated_at
FROM methods;

SELECT setval(
    pg_get_serial_sequence('methods_new', 'id'),
    COALESCE((SELECT MAX(id) FROM methods_new), 1),
    true
);

DROP INDEX IF EXISTS idx_methods_endpoint;
DROP INDEX IF EXISTS idx_methods_active;

DROP TABLE methods;
ALTER TABLE methods_new RENAME TO methods;
ALTER SEQUENCE methods_new_id_seq RENAME TO methods_id_seq;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'methods_new_pkey'
  ) THEN
    ALTER TABLE methods RENAME CONSTRAINT methods_new_pkey TO methods_pkey;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'methods_new_slug_key'
  ) THEN
    ALTER TABLE methods RENAME CONSTRAINT methods_new_slug_key TO methods_slug_key;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'methods_new_source_doc_id_fkey'
  ) THEN
    ALTER TABLE methods
      RENAME CONSTRAINT methods_new_source_doc_id_fkey
      TO fk_methods_source_doc;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_methods_endpoint ON methods(endpoint_category);
CREATE INDEX IF NOT EXISTS idx_methods_active ON methods(active);
CREATE INDEX IF NOT EXISTS idx_methods_source_doc ON methods(source_doc_id);

COMMENT ON COLUMN methods.source_citation IS
  'Bibliographic citation for the primary source document.';
COMMENT ON COLUMN methods.source_doc_id IS
  'FK → documents(id); primary source document for this method.';

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

-- ---------------------------------------------------------------------------
-- Rebuild method_regulatory_contexts
-- ---------------------------------------------------------------------------

CREATE TABLE method_regulatory_contexts_new (
    id                   SERIAL      PRIMARY KEY,
    method_id            INTEGER     NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    jurisdiction         TEXT        NOT NULL,
    validation_status    TEXT        NOT NULL,
    regulation_status    TEXT,
    regulation_date      DATE,
    regulation_purpose   TEXT,
    regulatory_body      TEXT,
    regulatory_doc_id    INTEGER     REFERENCES documents(id) ON DELETE SET NULL,
    regulatory_citation  TEXT,
    notes                TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (method_id, jurisdiction),
    CONSTRAINT method_regulatory_contexts_regulation_status_check CHECK (
      regulation_status IS NULL
      OR regulation_status IN (
        'not_approved',
        'approved',
        'recommended',
        'mandatory'
      )
    )
);

INSERT INTO method_regulatory_contexts_new (
    id, method_id, jurisdiction, validation_status,
    regulation_status, regulation_date, regulation_purpose,
    regulatory_body, regulatory_citation, notes, created_at
)
SELECT
    id, method_id, jurisdiction, validation_status,
    regulation_status, regulation_date, regulation_purpose,
    regulatory_body, regulatory_url, notes, created_at
FROM method_regulatory_contexts;

SELECT setval(
    pg_get_serial_sequence('method_regulatory_contexts_new', 'id'),
    COALESCE((SELECT MAX(id) FROM method_regulatory_contexts_new), 1),
    true
);

DROP INDEX IF EXISTS idx_mvc_method;
DROP INDEX IF EXISTS idx_mvc_jurisdiction;

DROP TABLE method_regulatory_contexts;
ALTER TABLE method_regulatory_contexts_new RENAME TO method_regulatory_contexts;
ALTER SEQUENCE method_regulatory_contexts_new_id_seq
  RENAME TO method_regulatory_contexts_id_seq;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_new_pkey'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_regulatory_contexts_new_pkey
      TO method_regulatory_contexts_pkey;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_new_method_id_jurisdiction_key'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_regulatory_contexts_new_method_id_jurisdiction_key
      TO method_regulatory_contexts_method_id_jurisdiction_key;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_new_method_id_fkey'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_regulatory_contexts_new_method_id_fkey
      TO method_regulatory_contexts_method_id_fkey;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'method_regulatory_contexts_new_regulatory_doc_id_fkey'
  ) THEN
    ALTER TABLE method_regulatory_contexts
      RENAME CONSTRAINT method_regulatory_contexts_new_regulatory_doc_id_fkey
      TO fk_mrc_regulatory_doc;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_mvc_method
  ON method_regulatory_contexts(method_id);
CREATE INDEX IF NOT EXISTS idx_mvc_jurisdiction
  ON method_regulatory_contexts(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_mvc_regulatory_doc
  ON method_regulatory_contexts(regulatory_doc_id);

COMMENT ON TABLE method_regulatory_contexts IS
  'Regulatory / validation context per method × jurisdiction.';
COMMENT ON COLUMN method_regulatory_contexts.regulatory_doc_id IS
  'FK → documents(id); regulatory document for this context.';
COMMENT ON COLUMN method_regulatory_contexts.regulatory_citation IS
  'Bibliographic citation / short reference for the regulatory recognition.';

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'feedback'
  ) AND EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'feedback'
      AND column_name = 'method_id'
  ) THEN
    ALTER TABLE feedback
      ADD CONSTRAINT feedback_method_id_fkey
      FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE;
  END IF;
END $$;
