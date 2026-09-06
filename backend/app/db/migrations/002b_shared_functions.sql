-- Shared PL/pgSQL trigger function used by vocabulary table triggers in 003+.
-- Must run before 003_vocabulary_tables.sql.

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
