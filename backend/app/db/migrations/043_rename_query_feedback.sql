-- Rename feedback → query_feedback.

ALTER TABLE IF EXISTS feedback
  RENAME TO query_feedback;

ALTER SEQUENCE IF EXISTS feedback_id_seq
  RENAME TO query_feedback_id_seq;

ALTER INDEX IF EXISTS idx_feedback_query_id RENAME TO idx_query_feedback_query_id;
ALTER INDEX IF EXISTS idx_feedback_method_id RENAME TO idx_query_feedback_method_id;
ALTER INDEX IF EXISTS idx_feedback_rating RENAME TO idx_query_feedback_rating;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'feedback_pkey'
  ) THEN
    ALTER TABLE query_feedback
      RENAME CONSTRAINT feedback_pkey
      TO query_feedback_pkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'feedback_query_id_fkey'
  ) THEN
    ALTER TABLE query_feedback
      RENAME CONSTRAINT feedback_query_id_fkey
      TO query_feedback_query_id_fkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'feedback_method_id_fkey'
  ) THEN
    ALTER TABLE query_feedback
      RENAME CONSTRAINT feedback_method_id_fkey
      TO query_feedback_method_id_fkey;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'feedback_query_id_method_id_key'
  ) THEN
    ALTER TABLE query_feedback
      RENAME CONSTRAINT feedback_query_id_method_id_key
      TO query_feedback_query_id_method_id_key;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'feedback_rating_check'
  ) THEN
    ALTER TABLE query_feedback
      RENAME CONSTRAINT feedback_rating_check
      TO query_feedback_rating_check;
  END IF;
END $$;

COMMENT ON TABLE query_feedback IS
  'Structured relevance feedback for a recommended method within a query (F11).';
