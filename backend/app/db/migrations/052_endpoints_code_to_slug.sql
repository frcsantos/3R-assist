-- =============================================================================
-- Migration 052: endpoints.code → slug; underscores → hyphens in values
-- =============================================================================

BEGIN;

ALTER TABLE endpoints
  RENAME COLUMN code TO slug;

UPDATE endpoints
SET slug = replace(slug, '_', '-');

COMMENT ON COLUMN endpoints.slug IS
  'URL-safe unique key (hyphenated), e.g. skin-irritation, acute-toxicity.';

COMMIT;
