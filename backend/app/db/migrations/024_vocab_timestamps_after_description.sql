-- =============================================================================
-- Migration 024: Reorder vocabulary columns so created_at / updated_at
-- sit after description (docs/tables.md shared shape).
-- After 023, ADD COLUMN left name/description at the physical end.
-- Tables: endpoints, routes, study_domains
-- Target order:
--   code, name, description, sort_order, active, created_at, updated_at
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Drop FKs that reference vocabulary PKs
-- ---------------------------------------------------------------------------

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_endpoint_category;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_study_domain;

ALTER TABLE method_regulatory_contexts
  DROP CONSTRAINT IF EXISTS fk_method_regulatory_contexts_study_domain;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_route_code_fkey;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_endpoint_code_fkey;

-- ---------------------------------------------------------------------------
-- endpoints
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS endpoints_updated_at ON endpoints;
DROP INDEX IF EXISTS idx_endpoints_active;

CREATE TABLE endpoints_new (
    code            TEXT            PRIMARY KEY,
    name            JSONB           NOT NULL,
    description     JSONB,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

INSERT INTO endpoints_new (
    code, name, description, sort_order, active, created_at, updated_at
)
SELECT
    code, name, description, sort_order, active, created_at, updated_at
FROM endpoints;

DROP TABLE endpoints;
ALTER TABLE endpoints_new RENAME TO endpoints;

CREATE INDEX idx_endpoints_active ON endpoints (active) WHERE active = TRUE;

CREATE TRIGGER endpoints_updated_at
    BEFORE UPDATE ON endpoints
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON COLUMN endpoints.name IS
  'Localized display name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN endpoints.description IS
  'Localized description: {"en-us": "...", "pt-br": "..."} (nullable)';

-- ---------------------------------------------------------------------------
-- routes
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS routes_updated_at ON routes;
DROP INDEX IF EXISTS idx_routes_active;

CREATE TABLE routes_new (
    code            TEXT            PRIMARY KEY,
    name            JSONB           NOT NULL,
    description     JSONB,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

INSERT INTO routes_new (
    code, name, description, sort_order, active, created_at, updated_at
)
SELECT
    code, name, description, sort_order, active, created_at, updated_at
FROM routes;

DROP TABLE routes;
ALTER TABLE routes_new RENAME TO routes;

CREATE INDEX idx_routes_active ON routes (active) WHERE active = TRUE;

CREATE TRIGGER routes_updated_at
    BEFORE UPDATE ON routes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON COLUMN routes.name IS
  'Localized display name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN routes.description IS
  'Localized description: {"en-us": "...", "pt-br": "..."} (nullable)';

-- ---------------------------------------------------------------------------
-- study_domains
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS study_domains_updated_at ON study_domains;
DROP INDEX IF EXISTS idx_study_domains_active;

CREATE TABLE study_domains_new (
    code            TEXT            PRIMARY KEY,
    name            JSONB           NOT NULL,
    description     JSONB,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

INSERT INTO study_domains_new (
    code, name, description, sort_order, active, created_at, updated_at
)
SELECT
    code, name, description, sort_order, active, created_at, updated_at
FROM study_domains;

DROP TABLE study_domains;
ALTER TABLE study_domains_new RENAME TO study_domains;

CREATE INDEX idx_study_domains_active ON study_domains (active) WHERE active = TRUE;

CREATE TRIGGER study_domains_updated_at
    BEFORE UPDATE ON study_domains
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON COLUMN study_domains.name IS
  'Localized display name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN study_domains.description IS
  'Localized description: {"en-us": "...", "pt-br": "..."} (nullable)';

-- ---------------------------------------------------------------------------
-- Restore FKs
-- ---------------------------------------------------------------------------

ALTER TABLE route_endpoints
  ADD CONSTRAINT route_endpoints_route_code_fkey
  FOREIGN KEY (route_code) REFERENCES routes(code) ON DELETE CASCADE;

ALTER TABLE route_endpoints
  ADD CONSTRAINT route_endpoints_endpoint_code_fkey
  FOREIGN KEY (endpoint_code) REFERENCES endpoints(code) ON DELETE CASCADE;

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_endpoint_category
  FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT fk_method_regulatory_contexts_study_domain
  FOREIGN KEY (study_domain) REFERENCES study_domains(code);

COMMIT;
