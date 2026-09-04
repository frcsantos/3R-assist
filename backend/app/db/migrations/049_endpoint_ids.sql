-- =============================================================================
-- Migration 049: methods.endpoint_category and route_endpoints.endpoint_code
-- become integer FKs → endpoints.id (from 048).
-- =============================================================================

BEGIN;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_endpoint_category;

ALTER TABLE methods
  ADD COLUMN endpoint_category_id INTEGER;

UPDATE methods m
SET endpoint_category_id = e.id
FROM endpoints e
WHERE e.code = m.endpoint_category;

ALTER TABLE methods
  DROP COLUMN endpoint_category;

ALTER TABLE methods
  RENAME COLUMN endpoint_category_id TO endpoint_category;

ALTER TABLE methods
  ALTER COLUMN endpoint_category SET NOT NULL;

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(id);

COMMENT ON COLUMN methods.endpoint_category IS
  'Toxicological endpoint; FK → endpoints(id).';

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_endpoint_code_fkey;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_pkey;

ALTER TABLE route_endpoints
  ADD COLUMN endpoint_id INTEGER;

UPDATE route_endpoints re
SET endpoint_id = e.id
FROM endpoints e
WHERE e.code = re.endpoint_code;

ALTER TABLE route_endpoints
  DROP COLUMN endpoint_code;

ALTER TABLE route_endpoints
  ALTER COLUMN endpoint_id SET NOT NULL;

ALTER TABLE route_endpoints
  ADD PRIMARY KEY (route_code, endpoint_id);

ALTER TABLE route_endpoints
  ADD CONSTRAINT route_endpoints_endpoint_id_fkey
  FOREIGN KEY (endpoint_id) REFERENCES endpoints(id) ON DELETE CASCADE;

DROP INDEX IF EXISTS idx_route_endpoints_endpoint;
CREATE INDEX idx_route_endpoints_endpoint ON route_endpoints (endpoint_id);

COMMENT ON COLUMN route_endpoints.endpoint_id IS
  'FK → endpoints(id) ON DELETE CASCADE. Part of composite PK.';

COMMIT;
