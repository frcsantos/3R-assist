-- =============================================================================
-- Migration 051: methods.endpoint_category INTEGER → methods.endpoints INTEGER[]
-- Each existing id is wrapped as a one-element array.
-- =============================================================================

BEGIN;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_endpoint_category;

DROP INDEX IF EXISTS idx_methods_endpoint;

ALTER TABLE methods
  ADD COLUMN endpoints INTEGER[];

UPDATE methods
SET endpoints = ARRAY[endpoint_category]
WHERE endpoint_category IS NOT NULL;

ALTER TABLE methods
  DROP COLUMN endpoint_category;

ALTER TABLE methods
  ALTER COLUMN endpoints SET NOT NULL;

CREATE INDEX idx_methods_endpoints ON methods USING GIN (endpoints);

COMMENT ON COLUMN methods.endpoints IS
  'Recognized endpoint ids (INTEGER[]) → endpoints.id, ordered.';

COMMIT;
