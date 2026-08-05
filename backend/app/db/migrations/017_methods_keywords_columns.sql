-- methods: move text_for_embedding immediately left of embedding_json;
-- fold method_keywords into keywords_en / keywords_pt JSONB lists; drop method_keywords.

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
  has_method_keywords boolean;
  old_en_count integer := 0;
  old_pt_count integer := 0;
  new_en_count integer := 0;
  new_pt_count integer := 0;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'methods'
      AND column_name = 'category_3r'
  ) INTO has_category_3r;

  SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name = 'method_keywords'
  ) INTO has_method_keywords;

  IF has_method_keywords THEN
    SELECT
      COUNT(*) FILTER (WHERE language = 'en'),
      COUNT(*) FILTER (WHERE language = 'pt')
    INTO old_en_count, old_pt_count
    FROM method_keywords;
  END IF;

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
          category_3r            JSONB       NOT NULL,
          replacement_rationale  TEXT,
          reduction_rationale    TEXT,
          refinement_rationale   TEXT,
          text_for_embedding     TEXT        NOT NULL,
          keywords_en            JSONB       NOT NULL DEFAULT '[]'::jsonb,
          keywords_pt            JSONB       NOT NULL DEFAULT '[]'::jsonb,
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
          replacement_rationale  TEXT,
          reduction_rationale    TEXT,
          refinement_rationale   TEXT,
          text_for_embedding     TEXT        NOT NULL,
          keywords_en            JSONB       NOT NULL DEFAULT '[]'::jsonb,
          keywords_pt            JSONB       NOT NULL DEFAULT '[]'::jsonb,
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
  END IF;

  IF has_method_keywords THEN
    IF has_category_3r THEN
      EXECUTE $sql$
        INSERT INTO methods_new (
            id, slug, active, name_en, name_pt, description_en, description_pt,
            category_3r,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, keywords_en, keywords_pt, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        )
        SELECT
            m.id, m.slug, m.active, m.name_en, m.name_pt,
            m.description_en, m.description_pt,
            m.category_3r,
            m.replacement_rationale, m.reduction_rationale, m.refinement_rationale,
            m.text_for_embedding,
            COALESCE(kw.keywords_en, '[]'::jsonb),
            COALESCE(kw.keywords_pt, '[]'::jsonb),
            m.embedding_json,
            m.created_at, m.updated_at,
            m.endpoint_category, m.routes_applicable, m.study_domain,
            m.oecd_ref, m.ncit_id, m.source_db
        FROM methods m
        LEFT JOIN (
            SELECT
                method_id,
                COALESCE(
                    jsonb_agg(keyword ORDER BY id) FILTER (WHERE language = 'en'),
                    '[]'::jsonb
                ) AS keywords_en,
                COALESCE(
                    jsonb_agg(keyword ORDER BY id) FILTER (WHERE language = 'pt'),
                    '[]'::jsonb
                ) AS keywords_pt
            FROM method_keywords
            GROUP BY method_id
        ) kw ON kw.method_id = m.id
      $sql$;
    ELSE
      EXECUTE $sql$
        INSERT INTO methods_new (
            id, slug, active, name_en, name_pt, description_en, description_pt,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, keywords_en, keywords_pt, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        )
        SELECT
            m.id, m.slug, m.active, m.name_en, m.name_pt,
            m.description_en, m.description_pt,
            m.replacement_rationale, m.reduction_rationale, m.refinement_rationale,
            m.text_for_embedding,
            COALESCE(kw.keywords_en, '[]'::jsonb),
            COALESCE(kw.keywords_pt, '[]'::jsonb),
            m.embedding_json,
            m.created_at, m.updated_at,
            m.endpoint_category, m.routes_applicable, m.study_domain,
            m.oecd_ref, m.ncit_id, m.source_db
        FROM methods m
        LEFT JOIN (
            SELECT
                method_id,
                COALESCE(
                    jsonb_agg(keyword ORDER BY id) FILTER (WHERE language = 'en'),
                    '[]'::jsonb
                ) AS keywords_en,
                COALESCE(
                    jsonb_agg(keyword ORDER BY id) FILTER (WHERE language = 'pt'),
                    '[]'::jsonb
                ) AS keywords_pt
            FROM method_keywords
            GROUP BY method_id
        ) kw ON kw.method_id = m.id
      $sql$;
    END IF;
  ELSE
    IF has_category_3r THEN
      EXECUTE $sql$
        INSERT INTO methods_new (
            id, slug, active, name_en, name_pt, description_en, description_pt,
            category_3r,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, keywords_en, keywords_pt, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        )
        SELECT
            id, slug, active, name_en, name_pt, description_en, description_pt,
            category_3r,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, '[]'::jsonb, '[]'::jsonb, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        FROM methods
      $sql$;
    ELSE
      EXECUTE $sql$
        INSERT INTO methods_new (
            id, slug, active, name_en, name_pt, description_en, description_pt,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, keywords_en, keywords_pt, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        )
        SELECT
            id, slug, active, name_en, name_pt, description_en, description_pt,
            replacement_rationale, reduction_rationale, refinement_rationale,
            text_for_embedding, '[]'::jsonb, '[]'::jsonb, embedding_json,
            created_at, updated_at,
            endpoint_category, routes_applicable, study_domain,
            oecd_ref, ncit_id, source_db
        FROM methods
      $sql$;
    END IF;
  END IF;

  SELECT
    COALESCE(SUM(jsonb_array_length(keywords_en)), 0),
    COALESCE(SUM(jsonb_array_length(keywords_pt)), 0)
  INTO new_en_count, new_pt_count
  FROM methods_new;

  IF old_en_count IS DISTINCT FROM new_en_count
     OR old_pt_count IS DISTINCT FROM new_pt_count THEN
    RAISE EXCEPTION
      'Keyword migration count mismatch: en %→%, pt %→%',
      old_en_count, new_en_count, old_pt_count, new_pt_count;
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

DROP TABLE IF EXISTS method_keywords;
