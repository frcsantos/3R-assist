-- =============================================================================
-- Migration 023: Fold paired *_en / *_pt columns into localized JSONB objects
-- Shape: {"en-us": ..., "pt-br": ...}
-- Tables: methods, endpoints, routes, study_domains, suggestions
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- methods: name, description, keywords
-- ---------------------------------------------------------------------------

ALTER TABLE methods
  ADD COLUMN IF NOT EXISTS name JSONB,
  ADD COLUMN IF NOT EXISTS description JSONB,
  ADD COLUMN IF NOT EXISTS keywords JSONB;

UPDATE methods
SET
  name = jsonb_build_object('en-us', name_en, 'pt-br', name_pt),
  description = jsonb_build_object(
    'en-us', description_en,
    'pt-br', description_pt
  ),
  keywords = jsonb_build_object(
    'en-us', COALESCE(keywords_en, '[]'::jsonb),
    'pt-br', COALESCE(keywords_pt, '[]'::jsonb)
  )
WHERE name IS NULL
   OR description IS NULL
   OR keywords IS NULL;

ALTER TABLE methods
  ALTER COLUMN name SET NOT NULL,
  ALTER COLUMN description SET NOT NULL,
  ALTER COLUMN keywords SET NOT NULL,
  ALTER COLUMN keywords SET DEFAULT '{"en-us": [], "pt-br": []}'::jsonb;

ALTER TABLE methods
  DROP COLUMN IF EXISTS name_en,
  DROP COLUMN IF EXISTS name_pt,
  DROP COLUMN IF EXISTS description_en,
  DROP COLUMN IF EXISTS description_pt,
  DROP COLUMN IF EXISTS keywords_en,
  DROP COLUMN IF EXISTS keywords_pt;

COMMENT ON COLUMN methods.name IS
  'Localized method name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN methods.description IS
  'Localized method description: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN methods.keywords IS
  'Localized synonym lists for search bridging: {"en-us": [...], "pt-br": [...]}';

-- ---------------------------------------------------------------------------
-- vocabulary tables: endpoints, routes, study_domains
-- ---------------------------------------------------------------------------

DO $$
DECLARE
  tbl text;
BEGIN
  FOREACH tbl IN ARRAY ARRAY['endpoints', 'routes', 'study_domains']
  LOOP
    EXECUTE format(
      'ALTER TABLE %I ADD COLUMN IF NOT EXISTS name JSONB',
      tbl
    );
    EXECUTE format(
      'ALTER TABLE %I ADD COLUMN IF NOT EXISTS description JSONB',
      tbl
    );

    EXECUTE format(
      $sql$
      UPDATE %I
      SET
        name = jsonb_build_object('en-us', name_en, 'pt-br', name_pt),
        description = CASE
          WHEN description_en IS NULL AND description_pt IS NULL THEN NULL
          ELSE jsonb_build_object(
            'en-us', COALESCE(description_en, ''),
            'pt-br', COALESCE(description_pt, '')
          )
        END
      WHERE name IS NULL
      $sql$,
      tbl
    );

    EXECUTE format(
      'ALTER TABLE %I ALTER COLUMN name SET NOT NULL',
      tbl
    );

    EXECUTE format(
      'ALTER TABLE %I DROP COLUMN IF EXISTS name_en',
      tbl
    );
    EXECUTE format(
      'ALTER TABLE %I DROP COLUMN IF EXISTS name_pt',
      tbl
    );
    EXECUTE format(
      'ALTER TABLE %I DROP COLUMN IF EXISTS description_en',
      tbl
    );
    EXECUTE format(
      'ALTER TABLE %I DROP COLUMN IF EXISTS description_pt',
      tbl
    );

    EXECUTE format(
      $sql$
      COMMENT ON COLUMN %I.name IS
        'Localized display name: {"en-us": "...", "pt-br": "..."}'
      $sql$,
      tbl
    );
    EXECUTE format(
      $sql$
      COMMENT ON COLUMN %I.description IS
        'Localized description: {"en-us": "...", "pt-br": "..."} (nullable)'
      $sql$,
      tbl
    );
  END LOOP;
END $$;

-- ---------------------------------------------------------------------------
-- suggestions: name only (description stays monolingual free text)
-- ---------------------------------------------------------------------------

ALTER TABLE suggestions
  ADD COLUMN IF NOT EXISTS name JSONB;

UPDATE suggestions
SET name = jsonb_build_object(
  'en-us', name_en,
  'pt-br', COALESCE(name_pt, '')
)
WHERE name IS NULL;

ALTER TABLE suggestions
  ALTER COLUMN name SET NOT NULL;

ALTER TABLE suggestions
  DROP COLUMN IF EXISTS name_en,
  DROP COLUMN IF EXISTS name_pt;

COMMENT ON COLUMN suggestions.name IS
  'Localized suggested method name: {"en-us": "...", "pt-br": "..."}';

COMMIT;
