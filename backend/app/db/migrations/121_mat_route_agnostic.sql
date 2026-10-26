-- =============================================================================
-- Migration 121: MAT (method 20) route-agnostic, like the other pyrogen tests.
-- The Monocyte Activation Test had routes_applicable = {intravenous}, while the
-- bacterial endotoxin tests (38 LAL, 56 rFC) are NULL (route-agnostic) and
-- docs/parameter_model.md section 8 expects NULL for the MAT ("detects
-- contamination, route-agnostic"). Only changes the row if it still has
-- exactly the intravenous route.
-- =============================================================================

BEGIN;

UPDATE methods
SET routes_applicable = NULL
WHERE id = 20
  AND routes_applicable = (SELECT ARRAY[id] FROM routes WHERE slug = 'intravenous');

COMMIT;
