-- =============================================================================
-- 3R Assist — Migration 004: application_area → study_domain (ADR-020)
-- Assumes: 001_initial.sql applied; 003 may or may not be applied
-- =============================================================================

ALTER TABLE methods
    DROP CONSTRAINT IF EXISTS fk_methods_application_area;

ALTER TABLE methods
    DROP CONSTRAINT IF EXISTS methods_application_area_check;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'methods'
          AND column_name = 'application_area'
    ) THEN
        ALTER TABLE methods RENAME COLUMN application_area TO study_domain;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'application_areas'
    ) THEN
        ALTER TABLE application_areas RENAME TO study_domains;
    END IF;
END $$;

ALTER INDEX IF EXISTS idx_application_areas_active
    RENAME TO idx_study_domains_active;

DROP TRIGGER IF EXISTS application_areas_updated_at ON study_domains;
DROP TRIGGER IF EXISTS study_domains_updated_at ON study_domains;

CREATE TRIGGER study_domains_updated_at
    BEFORE UPDATE ON study_domains
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'study_domains'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_methods_study_domain'
    ) THEN
        ALTER TABLE methods
            ADD CONSTRAINT fk_methods_study_domain
                FOREIGN KEY (study_domain) REFERENCES study_domains(code);
    END IF;
END $$;
