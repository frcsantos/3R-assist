-- =============================================================================
-- Migration 048: regulations.regulatory_purpose → regulatory_endpoints INTEGER[]
-- Endpoints vocab gets a unique integer id; regulations stores a vector of
-- those ids (recognized endpoints for the method × jurisdiction).
-- Existing purpose text cannot be mapped reliably → NULL.
-- =============================================================================

BEGIN;

ALTER TABLE endpoints
  ADD COLUMN IF NOT EXISTS id INTEGER;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class WHERE relname = 'endpoints_id_seq'
  ) THEN
    CREATE SEQUENCE endpoints_id_seq OWNED BY endpoints.id;
  END IF;
END $$;

ALTER TABLE endpoints
  ALTER COLUMN id SET DEFAULT nextval('endpoints_id_seq');

UPDATE endpoints
SET id = nextval('endpoints_id_seq')
WHERE id IS NULL;

SELECT setval(
  'endpoints_id_seq',
  COALESCE((SELECT MAX(id) FROM endpoints), 1),
  true
);

ALTER TABLE endpoints
  ALTER COLUMN id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS endpoints_id_key ON endpoints(id);

ALTER TABLE regulations
  ADD COLUMN IF NOT EXISTS regulatory_endpoints INTEGER[];

ALTER TABLE regulations
  DROP COLUMN IF EXISTS regulatory_purpose;

COMMENT ON COLUMN endpoints.id IS
  'Unique integer id for referencing endpoints from INTEGER[] columns.';
COMMENT ON COLUMN regulations.regulatory_endpoints IS
  'Recognized endpoint ids (INTEGER[]) → endpoints.id, ordered.';

COMMIT;
