-- =============================================================================
-- Migration 058: routes.compatible_endpoints INTEGER[]
-- Backfill from existing route_endpoints compatibility matrix.
-- =============================================================================

BEGIN;

ALTER TABLE routes
  ADD COLUMN IF NOT EXISTS compatible_endpoints INTEGER[];

UPDATE routes r
SET compatible_endpoints = sub.ids
FROM (
  SELECT
    re.route_code,
    array_agg(re.endpoint_id ORDER BY re.endpoint_id) AS ids
  FROM route_endpoints re
  GROUP BY re.route_code
) sub
WHERE r.code = sub.route_code;

COMMENT ON COLUMN routes.compatible_endpoints IS
  'Compatible endpoint ids (INTEGER[]) → endpoints.id, ordered.';

COMMIT;
