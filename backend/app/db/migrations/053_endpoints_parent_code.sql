-- =============================================================================
-- Migration 053: endpoints.parent_id + endpoints.code (nullable)
-- =============================================================================

BEGIN;

ALTER TABLE endpoints
  ADD COLUMN IF NOT EXISTS parent_id INTEGER;

ALTER TABLE endpoints
  ADD COLUMN IF NOT EXISTS code TEXT;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'fk_endpoints_parent'
  ) THEN
    ALTER TABLE endpoints
      ADD CONSTRAINT fk_endpoints_parent
      FOREIGN KEY (parent_id) REFERENCES endpoints(id) ON DELETE SET NULL;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_endpoints_parent ON endpoints (parent_id);

COMMENT ON COLUMN endpoints.parent_id IS
  'Optional parent endpoint id (self-FK → endpoints.id).';
COMMENT ON COLUMN endpoints.code IS
  'Optional short / legacy code (nullable).';

COMMIT;
