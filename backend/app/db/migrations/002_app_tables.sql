-- =============================================================================
-- 3R Assist — Migration 002: Application tables (PostgreSQL)
-- Tables: users, magic_link_tokens, queries, feedback, suggestions
-- Assumes: 001_initial.sql already applied (methods exist)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- USERS
-- F08 — email magic link auth
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id           SERIAL       PRIMARY KEY,
    email        TEXT         NOT NULL UNIQUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- MAGIC LINK TOKENS
-- Single-use tokens; itsdangerous signs them but we track usage to prevent
-- replay within the validity window.
-- ---------------------------------------------------------------------------

CREATE TABLE magic_link_tokens (
    id          SERIAL       PRIMARY KEY,
    user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- store SHA-256 of the raw token, never the token itself
    token_hash  TEXT         NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ  NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_magic_link_token_hash ON magic_link_tokens (token_hash);
CREATE INDEX idx_magic_link_expires    ON magic_link_tokens (expires_at)
    WHERE used_at IS NULL;

-- ---------------------------------------------------------------------------
-- QUERIES
-- F09 — query history; F02/F03 — parameter extraction output
-- user_id NULL = anonymous session
-- ---------------------------------------------------------------------------
-- extracted_params follows parameter_model.md ExtractionResult schema:
--   { endpoint_category, route, study_domain, procedure_text,
--     species, n_animals, regulatory, confidence, raw_text_excerpt }
--
-- results_snapshot: array of { method_id, slug, score } captured at query time.
-- Stored so history is consistent even when methods are added or removed later.
-- ---------------------------------------------------------------------------

CREATE TABLE queries (
    id                SERIAL       PRIMARY KEY,
    user_id           INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    protocol_text     TEXT         NOT NULL,
    extracted_params  JSONB,
    confidence        TEXT         CHECK (confidence IN ('high', 'medium', 'low')),
    results_snapshot  JSONB,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_queries_user_id    ON queries (user_id);
CREATE INDEX idx_queries_created_at ON queries (created_at DESC);

-- ---------------------------------------------------------------------------
-- FEEDBACK
-- F11 — structured feedback questionnaire (one row per method per query)
-- ---------------------------------------------------------------------------

CREATE TABLE feedback (
    id          SERIAL       PRIMARY KEY,
    query_id    INTEGER      NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    method_id   INTEGER      NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    rating      TEXT         NOT NULL
                    CHECK (rating IN ('relevant', 'partial', 'not_relevant')),
    comment     TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (query_id, method_id)   -- one rating per method per query
);

CREATE INDEX idx_feedback_query_id  ON feedback (query_id);
CREATE INDEX idx_feedback_method_id ON feedback (method_id);
CREATE INDEX idx_feedback_rating    ON feedback (rating);

-- ---------------------------------------------------------------------------
-- SUGGESTIONS
-- F12 — user-submitted method suggestions, queued for manual curation
-- ---------------------------------------------------------------------------

CREATE TABLE suggestions (
    id              SERIAL       PRIMARY KEY,
    user_id         INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    name_en         TEXT         NOT NULL,
    name_pt         TEXT,
    description     TEXT,
    source_url      TEXT,
    -- user's best guess; not validated — Karynn reviews before use
    endpoint_hint   TEXT,
    status          TEXT         NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'reviewed', 'accepted', 'rejected')),
    reviewer_notes  TEXT,
    submitted_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ
);

CREATE INDEX idx_suggestions_status ON suggestions (status)
    WHERE status = 'pending';


-- ---------------------------------------------------------------------------
-- TRIGGERS: updated_at equivalents where needed
-- (users.last_seen_at is updated by the auth flow, not a trigger)
-- ---------------------------------------------------------------------------

-- No auto-updated_at triggers on app tables — all mutations are explicit
-- in the service layer. last_seen_at on users is set on each magic link
-- validation, not automatically.


-- ---------------------------------------------------------------------------
-- VERIFICATION QUERIES
-- ---------------------------------------------------------------------------
-- SELECT table_name FROM information_schema.tables
--   WHERE table_schema = 'public' ORDER BY table_name;
-- Expected: feedback, magic_link_tokens, methods,
--           queries, suggestions, users
-- (method_keywords folded into methods.keywords_en / keywords_pt in 017)
