-- =============================================================================
-- Assist3R — Migration 066: User sessions (F08 magic-link auth, Phase 2)
-- Tables: user_sessions
-- Assumes: 002_app_tables.sql already applied (users, magic_link_tokens exist)
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id          SERIAL       PRIMARY KEY,
    user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- store SHA-256 of the raw session token, never the token itself
    token_hash  TEXT         NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ  NOT NULL,
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token_hash ON user_sessions (token_hash);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions (expires_at)
    WHERE revoked_at IS NULL;
