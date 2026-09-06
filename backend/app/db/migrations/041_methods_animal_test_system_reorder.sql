-- =============================================================================
-- Migration 041: move methods.animal_use + test_system left of endpoint_category
-- Order: … description, animal_use, test_system, endpoint_category, …
-- =============================================================================

BEGIN;

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

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_source_doc;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_animal_use_check;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_test_system_is_array;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_test_system_values_check;

-- ---------------------------------------------------------------------------
-- Rebuild methods with animal_use / test_system before endpoint_category
-- ---------------------------------------------------------------------------

CREATE TABLE methods_new (
    id                     SERIAL      PRIMARY KEY,
    slug                   TEXT        NOT NULL UNIQUE,
    active                 BOOLEAN     NOT NULL DEFAULT FALSE,
    name                   JSONB       NOT NULL,
    description            JSONB       NOT NULL,
    animal_use             TEXT,
    test_system            JSONB,
    endpoint_category      TEXT        NOT NULL,
    routes_applicable      JSONB,
    study_domain           TEXT        NOT NULL,
    oecd_ref               TEXT,
    ncit_id                TEXT,
    source_citation        TEXT,
    source_doc_id          INTEGER     REFERENCES documents(id) ON DELETE SET NULL,
    source_db              TEXT        NOT NULL,
    replacement_rationale  JSONB,
    reduction_rationale    JSONB,
    refinement_rationale   JSONB,
    keywords               JSONB       NOT NULL DEFAULT '{"en-us": [], "pt-br": []}'::jsonb,
    text_for_embedding     TEXT        NOT NULL,
    embedding_json         JSONB,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT methods_animal_use_check CHECK (
      animal_use IS NULL
      OR animal_use IN (
        'none',
        'animal_derived_material',
        'slaughterhouse_byproduct',
        'animals_killed_for_tissue',
        'live_animals',
        'mixed_or_variable'
      )
    ),
    CONSTRAINT methods_test_system_is_array CHECK (
      test_system IS NULL
      OR jsonb_typeof(test_system) = 'array'
    ),
    CONSTRAINT methods_test_system_values_check CHECK (
      test_system IS NULL
      OR test_system <@ '[
        "in_silico",
        "in_chemico",
        "in_vitro",
        "ex_vivo",
        "in_vivo",
        "hybrid",
        "unclear"
      ]'::jsonb
    )
);

INSERT INTO methods_new (
    id, slug, active, name, description,
    animal_use, test_system,
    endpoint_category, routes_applicable, study_domain,
    oecd_ref, ncit_id, source_citation, source_doc_id, source_db,
    replacement_rationale, reduction_rationale, refinement_rationale,
    keywords, text_for_embedding, embedding_json, created_at, updated_at
)
SELECT
    id, slug, active, name, description,
    animal_use, test_system,
    endpoint_category, routes_applicable, study_domain,
    oecd_ref, ncit_id, source_citation, source_doc_id, source_db,
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
DROP INDEX IF EXISTS idx_methods_source_doc;
DROP INDEX IF EXISTS idx_methods_test_system;

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
CREATE INDEX IF NOT EXISTS idx_methods_test_system ON methods USING gin (test_system);

COMMENT ON COLUMN methods.animal_use IS
  'How the method uses animals or animal materials: '
  'none | animal_derived_material | slaughterhouse_byproduct | '
  'animals_killed_for_tissue | live_animals | mixed_or_variable.';
COMMENT ON COLUMN methods.test_system IS
  'Test system kinds (multi-select JSON array): '
  'in_silico | in_chemico | in_vitro | ex_vivo | in_vivo | hybrid | unclear.';
COMMENT ON COLUMN methods.source_citation IS
  'Bibliographic citation for the primary source document.';
COMMENT ON COLUMN methods.source_doc_id IS
  'FK → documents(id); primary source document for this method.';
COMMENT ON COLUMN methods.replacement_rationale IS
  'Localized replacement rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as replacement (ADR-023).';
COMMENT ON COLUMN methods.reduction_rationale IS
  'Localized reduction rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as reduction.';
COMMENT ON COLUMN methods.refinement_rationale IS
  'Localized refinement rationale: {"en-us":"...","pt-br":"..."}. '
  'Non-null with non-empty locale text ⇒ qualifies as refinement.';

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

-- ---------------------------------------------------------------------------
-- Restore FKs that reference methods(id)
-- ---------------------------------------------------------------------------

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'regulations'
  ) THEN
    ALTER TABLE regulations
      ADD CONSTRAINT regulations_method_id_fkey
      FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE;
  END IF;

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

  IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'suggestions'
  ) AND EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'suggestions'
      AND column_name = 'method_id'
  ) THEN
    ALTER TABLE suggestions
      ADD CONSTRAINT suggestions_method_id_fkey
      FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE;
  END IF;
END $$;

COMMIT;
