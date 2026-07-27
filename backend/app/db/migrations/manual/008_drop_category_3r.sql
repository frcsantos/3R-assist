-- ADR-023 step 4 (historical): drop category_3r after rationales are filled.
-- SUPERSEDED by auto-applied migration:
--   026_methods_drop_category_3r_reorder.sql
-- Kept for reference / older environments that still have category_3r.
-- Prefer: python scripts/migrate.py
-- Legacy path: python scripts/backfill_3r_rationales.py --apply-drop

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'methods'
      AND column_name = 'category_3r'
  ) THEN
    RAISE NOTICE 'category_3r already dropped — nothing to do.';
    RETURN;
  END IF;

  IF EXISTS (
    SELECT 1
    FROM methods
    WHERE (category_3r @> '["replacement"]'::jsonb
           AND (replacement_rationale IS NULL
                OR replacement_rationale = '[PENDENTE — ver category_3r]'))
       OR (category_3r @> '["reduction"]'::jsonb
           AND (reduction_rationale IS NULL
                OR reduction_rationale = '[PENDENTE — ver category_3r]'))
       OR (category_3r @> '["refinement"]'::jsonb
           AND (refinement_rationale IS NULL
                OR refinement_rationale = '[PENDENTE — ver category_3r]'))
  ) THEN
    RAISE EXCEPTION
      'Cannot drop category_3r: pending rationale placeholders remain. '
      'Run scripts/backfill_3r_rationales.py --check and fill all [PENDENTE] values first.';
  END IF;
END $$;

DROP INDEX IF EXISTS idx_methods_category_3r;

ALTER TABLE methods DROP COLUMN IF EXISTS category_3r;
