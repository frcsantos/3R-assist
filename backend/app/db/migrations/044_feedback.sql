-- General site / product feedback (distinct from query_feedback ratings).

CREATE TABLE feedback (
    id             SERIAL       PRIMARY KEY,
    user_id        INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    url            TEXT         NOT NULL,
    object         TEXT         NOT NULL,
    feedback_text  TEXT         NOT NULL,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_user_id ON feedback (user_id);
CREATE INDEX idx_feedback_created_at ON feedback (created_at DESC);

COMMENT ON TABLE feedback IS
  'General user feedback: page URL, subject object, and free-text message.';
COMMENT ON COLUMN feedback.url IS
  'Page or resource URL where the feedback was submitted.';
COMMENT ON COLUMN feedback.object IS
  'Subject of the feedback (e.g. UI element, feature, or entity).';
COMMENT ON COLUMN feedback.feedback_text IS
  'Free-text feedback message.';
