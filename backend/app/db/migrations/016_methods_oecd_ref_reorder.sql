-- methods: rename oecd_tg_ref → oecd_ref; reorder
--   endpoint_category, routes_applicable, study_domain, oecd_ref, ncit_id, source_db

ALTER TABLE methods
  RENAME COLUMN oecd_tg_ref TO oecd_ref;

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

DO $$
DECLARE
  has_category_3r boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'methods'
      AND column_name = 'category_3r'
  ) INTO has_category_3r;

  IF has_category_3r THEN
    EXECUTE $sql$
      CREATE TABLE methods_new (
          id                     SERIAL      PRIMARY KEY,
          slug                   TEXT        NOT NULL UNIQUE,
          active                 BOOLEAN     NOT NULL DEFAULT FALSE,
          name_en                TEXT        NOT NULL,
          name_pt                TEXT        NOT NULL,
          description_en         TEXT        NOT NULL,
          description_pt         TEXT        NOT NULL,
          text_for_embedding     TEXT        NOT NULL,
          category_3r            JSONB       NOT NULL,
          replacement_rationale  TEXT,
          reduction_rationale    TEXT,
          refinement_rationale   TEXT,
          embedding_json         JSONB,
          created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          endpoint_category      TEXT        NOT NULL,
          routes_applicable      JSONB,
          study_domain           TEXT        NOT NULL,
          oecd_ref               TEXT,
          ncit_id                TEXT,
          source_db              TEXT        NOT NULL
      )
    $sql$;

    EXECUTE $sql$
      INSERT INTO methods_new (
          id, slug, active, name_en, name_pt, description_en, description_pt,
          text_for_embedding, category_3r,
          replacement_rationale, reduction_rationale, refinement_rationale,
          embedding_json, created_at, updated_at,
          endpoint_category, routes_applicable, study_domain,
          oecd_ref, ncit_id, source_db
      )
      SELECT
          id, slug, active, name_en, name_pt, description_en, description_pt,
          text_for_embedding, category_3r,
          replacement_rationale, reduction_rationale, refinement_rationale,
          embedding_json, created_at, updated_at,
          endpoint_category, routes_applicable, study_domain,
          oecd_ref, ncit_id, source_db
      FROM methods
    $sql$;
  ELSE
    EXECUTE $sql$
      CREATE TABLE methods_new (
          id                     SERIAL      PRIMARY KEY,
          slug                   TEXT        NOT NULL UNIQUE,
          active                 BOOLEAN     NOT NULL DEFAULT FALSE,
          name_en                TEXT        NOT NULL,
          name_pt                TEXT        NOT NULL,
          description_en         TEXT        NOT NULL,
          description_pt         TEXT        NOT NULL,
          text_for_embedding     TEXT        NOT NULL,
          replacement_rationale  TEXT,
          reduction_rationale    TEXT,
          refinement_rationale   TEXT,
          embedding_json         JSONB,
          created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          endpoint_category      TEXT        NOT NULL,
          routes_applicable      JSONB,
          study_domain           TEXT        NOT NULL,
          oecd_ref               TEXT,
          ncit_id                TEXT,
          source_db              TEXT        NOT NULL
      )
    $sql$;

    EXECUTE $sql$
      INSERT INTO methods_new (
          id, slug, active, name_en, name_pt, description_en, description_pt,
          text_for_embedding,
          replacement_rationale, reduction_rationale, refinement_rationale,
          embedding_json, created_at, updated_at,
          endpoint_category, routes_applicable, study_domain,
          oecd_ref, ncit_id, source_db
      )
      SELECT
          id, slug, active, name_en, name_pt, description_en, description_pt,
          text_for_embedding,
          replacement_rationale, reduction_rationale, refinement_rationale,
          embedding_json, created_at, updated_at,
          endpoint_category, routes_applicable, study_domain,
          oecd_ref, ncit_id, source_db
      FROM methods
    $sql$;
  END IF;

  PERFORM setval(
      pg_get_serial_sequence('methods_new', 'id'),
      COALESCE((SELECT MAX(id) FROM methods_new), 1),
      true
  );
END $$;

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

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'methods'
      AND column_name = 'category_3r'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_methods_category_3r
      ON methods USING gin(category_3r);
  END IF;
END $$;

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

ALTER TABLE method_keywords
  ADD CONSTRAINT method_keywords_method_id_fkey
  FOREIGN KEY (method_id) REFERENCES methods(id) ON DELETE CASCADE;

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
