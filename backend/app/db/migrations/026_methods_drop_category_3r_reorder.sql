-- =============================================================================
-- Migration 026: methods — drop category_3r; restore column order after 023
-- Target order (docs/tables.md / ADR-023):
--   id, slug, active, name, description,
--   endpoint_category, routes_applicable, study_domain,
--   oecd_ref, ncit_id, source_citation, source_url, source_date, source_db,
--   replacement_rationale, reduction_rationale, refinement_rationale,
--   keywords, text_for_embedding, embedding_json, created_at, updated_at
-- category_3r is fully inferred from non-null/non-empty *_rationale columns.
-- =============================================================================

-- Drop every FK that references methods(id) before rebuild.
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
    source_url             TEXT,
    source_date            TIMESTAMPTZ,
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
    oecd_ref, ncit_id, source_citation, source_url, source_date, source_db,
    replacement_rationale, reduction_rationale, refinement_rationale,
    keywords, text_for_embedding, embedding_json, created_at, updated_at
)
SELECT
    id, slug, active, name, description,
    endpoint_category, routes_applicable, study_domain,
    oecd_ref, ncit_id, source_citation, source_url, source_date, source_db,
    replacement_rationale, reduction_rationale, refinement_rationale,
    keywords, text_for_embedding, embedding_json, created_at, updated_at
FROM methods;

SELECT setval(
    pg_get_serial_sequence('methods_new', 'id'),
    COALESCE((SELECT MAX(id) FROM methods_new), 1),
    true
);

DROP INDEX IF EXISTS idx_methods_category_3r;
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
END $$;

CREATE INDEX IF NOT EXISTS idx_methods_endpoint ON methods(endpoint_category);
CREATE INDEX IF NOT EXISTS idx_methods_active ON methods(active);

COMMENT ON COLUMN methods.name IS
  'Localized method name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN methods.description IS
  'Localized method description: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN methods.keywords IS
  'Localized synonym lists for search bridging: {"en-us": [...], "pt-br": [...]}';
COMMENT ON COLUMN methods.source_citation IS
  'Bibliographic citation for the primary source document of this method.';
COMMENT ON COLUMN methods.source_url IS
  'URL of the primary source document for this method.';
COMMENT ON COLUMN methods.source_date IS
  'Publication / adoption datetime of the primary source document.';
COMMENT ON COLUMN methods.replacement_rationale IS
  'Non-null/non-empty ⇒ qualifies as replacement; value is the auditable rationale (ADR-023).';
COMMENT ON COLUMN methods.reduction_rationale IS
  'Non-null/non-empty ⇒ qualifies as reduction.';
COMMENT ON COLUMN methods.refinement_rationale IS
  'Non-null/non-empty ⇒ qualifies as refinement.';

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT method_regulatory_contexts_method_id_fkey
  FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE;

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
