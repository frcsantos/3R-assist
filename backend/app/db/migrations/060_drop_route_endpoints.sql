-- =============================================================================
-- Migration 060: drop route_endpoints
-- Compatibility now lives on routes.compatible_endpoints INTEGER[].
-- =============================================================================

BEGIN;

DROP INDEX IF EXISTS idx_route_endpoints_endpoint;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_route_code_fkey;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_endpoint_id_fkey;

DROP TABLE IF EXISTS route_endpoints;

COMMIT;
