-- =============================================================================
-- 3R Assist — Migration 005: ADR-021/022 schema upgrade
-- Upgrades databases created from pre-rewrite 001_initial.sql:
--   category_3r TEXT → JSONB
--   method_validation_contexts table
--   removes jurisdiction/validation columns from methods
-- Assumes: 001–004 already applied on legacy schema
-- Fresh installs: use rewritten 001_initial.sql (this migration no-ops safely)
-- =============================================================================

CREATE TABLE IF NOT EXISTS method_validation_contexts (
    id                SERIAL      PRIMARY KEY,
    method_id         INTEGER     NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    study_domain      TEXT        NOT NULL,
    jurisdiction      TEXT        NOT NULL,
    validation_status TEXT        NOT NULL,
    purpose           TEXT,
    regulatory_status TEXT,
    regulatory_body   TEXT,
    regulatory_ref    TEXT,
    regulatory_url    TEXT,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (method_id, study_domain, jurisdiction),
    CONSTRAINT method_validation_contexts_regulatory_status_check CHECK (
        regulatory_status IS NULL
        OR regulatory_status IN (
            'not_approved',
            'approved',
            'recommended',
            'mandatory'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_mvc_method
    ON method_validation_contexts(method_id);
CREATE INDEX IF NOT EXISTS idx_mvc_jurisdiction
    ON method_validation_contexts(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_mvc_domain_juris
    ON method_validation_contexts(study_domain, jurisdiction);

ALTER TABLE methods
    ADD COLUMN IF NOT EXISTS ncit_id TEXT;

ALTER TABLE methods
    DROP CONSTRAINT IF EXISTS methods_category_3r_check;

-- category_3r TEXT → JSONB
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'methods'
          AND column_name = 'category_3r'
          AND data_type = 'text'
    ) THEN
        ALTER TABLE methods
            ALTER COLUMN category_3r TYPE JSONB
            USING to_jsonb(ARRAY[category_3r::text]);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_methods_category_3r
    ON methods USING gin(category_3r);

-- Migrate legacy jurisdiction/validation columns into method_validation_contexts
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'methods'
          AND column_name = 'jurisdiction'
    ) THEN
        INSERT INTO method_validation_contexts (
            method_id, study_domain, jurisdiction, validation_status,
            regulatory_body, regulatory_ref, regulatory_url, notes
        )
        SELECT
            m.id,
            m.study_domain,
            mapped.jurisdiction,
            m.validation_status,
            NULL,
            m.oecd_tg_ref,
            m.regulatory_url,
            m.jurisdiction_notes
        FROM methods m
        CROSS JOIN LATERAL (
            SELECT 'brazil' AS jurisdiction
            WHERE m.jurisdiction IN ('brazil', 'both')
            UNION ALL
            SELECT 'oecd'
            WHERE m.jurisdiction IN ('international', 'both')
        ) AS mapped
        ON CONFLICT (method_id, study_domain, jurisdiction) DO NOTHING;
    END IF;
END $$;

ALTER TABLE methods DROP COLUMN IF EXISTS validation_status;
ALTER TABLE methods DROP COLUMN IF EXISTS jurisdiction;
ALTER TABLE methods DROP COLUMN IF EXISTS jurisdiction_notes;
ALTER TABLE methods DROP COLUMN IF EXISTS primary_lit_url;
ALTER TABLE methods DROP COLUMN IF EXISTS regulatory_url;
