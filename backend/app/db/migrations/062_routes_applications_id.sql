-- =============================================================================
-- Migration 062: add unique integer id to routes and applications
-- slug remains the primary key (same pattern as endpoints.id).
-- =============================================================================

BEGIN;

ALTER TABLE routes
  ADD COLUMN IF NOT EXISTS id INTEGER;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class WHERE relname = 'routes_id_seq'
  ) THEN
    CREATE SEQUENCE routes_id_seq OWNED BY routes.id;
  END IF;
END $$;

ALTER TABLE routes
  ALTER COLUMN id SET DEFAULT nextval('routes_id_seq');

UPDATE routes r
SET id = s.rn
FROM (
  SELECT slug, ROW_NUMBER() OVER (ORDER BY sort_order, slug) AS rn
  FROM routes
) s
WHERE r.slug = s.slug
  AND r.id IS NULL;

SELECT setval(
  'routes_id_seq',
  COALESCE((SELECT MAX(id) FROM routes), 1),
  true
);

ALTER TABLE routes
  ALTER COLUMN id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS routes_id_key ON routes(id);

ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS id INTEGER;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class WHERE relname = 'applications_id_seq'
  ) THEN
    CREATE SEQUENCE applications_id_seq OWNED BY applications.id;
  END IF;
END $$;

ALTER TABLE applications
  ALTER COLUMN id SET DEFAULT nextval('applications_id_seq');

UPDATE applications a
SET id = s.rn
FROM (
  SELECT slug, ROW_NUMBER() OVER (ORDER BY sort_order, slug) AS rn
  FROM applications
) s
WHERE a.slug = s.slug
  AND a.id IS NULL;

SELECT setval(
  'applications_id_seq',
  COALESCE((SELECT MAX(id) FROM applications), 1),
  true
);

ALTER TABLE applications
  ALTER COLUMN id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS applications_id_key ON applications(id);

COMMENT ON COLUMN routes.id IS
  'Unique integer id for referencing routes.';
COMMENT ON COLUMN applications.id IS
  'Unique integer id for referencing applications.';

COMMIT;
