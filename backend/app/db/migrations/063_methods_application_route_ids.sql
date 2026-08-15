-- =============================================================================
-- Migration 063: methods.application → application_ids INTEGER[];
-- methods.routes_applicable JSONB slugs → INTEGER[] of routes.id
-- NULL routes_applicable remains route-agnostic.
-- =============================================================================

BEGIN;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_application;

ALTER TABLE methods
  ADD COLUMN IF NOT EXISTS application_ids INTEGER[];

UPDATE methods m
SET application_ids = ARRAY[a.id]
FROM applications a
WHERE a.slug = m.application
  AND m.application_ids IS NULL;

UPDATE methods
SET application_ids = '{}'::int[]
WHERE application_ids IS NULL;

ALTER TABLE methods
  DROP COLUMN IF EXISTS application;

ALTER TABLE methods
  ALTER COLUMN application_ids SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_methods_application_ids
  ON methods USING GIN (application_ids);

ALTER TABLE methods
  ADD COLUMN routes_applicable_ids INTEGER[];

UPDATE methods m
SET routes_applicable_ids = sub.ids
FROM (
  SELECT
    m2.id,
    ARRAY(
      SELECT r.id
      FROM jsonb_array_elements_text(m2.routes_applicable)
        WITH ORDINALITY AS t(slug, ord)
      JOIN routes r ON r.slug = t.slug
      ORDER BY t.ord
    ) AS ids
  FROM methods m2
  WHERE m2.routes_applicable IS NOT NULL
) sub
WHERE m.id = sub.id;

ALTER TABLE methods
  DROP COLUMN routes_applicable;

ALTER TABLE methods
  RENAME COLUMN routes_applicable_ids TO routes_applicable;

UPDATE methods
SET routes_applicable = NULL
WHERE routes_applicable = '{}'::int[];

CREATE INDEX IF NOT EXISTS idx_methods_routes_applicable
  ON methods USING GIN (routes_applicable);

COMMENT ON COLUMN methods.application_ids IS
  'Application ids (INTEGER[]) → applications.id, ordered.';
COMMENT ON COLUMN methods.routes_applicable IS
  'Applicable route ids (INTEGER[]) → routes.id. NULL = route-agnostic.';

COMMIT;
