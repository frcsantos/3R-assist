-- Migration 034: allow documents.category = 'other'

DO $$
DECLARE
  rec record;
BEGIN
  FOR rec IN
    SELECT c.conname
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE c.contype = 'c'
      AND n.nspname = 'public'
      AND t.relname = 'documents'
      AND pg_get_constraintdef(c.oid) ILIKE '%category%'
  LOOP
    EXECUTE format(
      'ALTER TABLE documents DROP CONSTRAINT IF EXISTS %I',
      rec.conname
    );
  END LOOP;
END $$;

ALTER TABLE documents
  ADD CONSTRAINT documents_category_check CHECK (
    category IN (
      'method_protocol',
      'guideline',
      'regulation',
      'other'
    )
  );

COMMENT ON COLUMN documents.category IS
  'Document kind: method_protocol | guideline | regulation | other.';
