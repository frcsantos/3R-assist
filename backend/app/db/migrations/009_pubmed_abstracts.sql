-- =============================================================================
-- 3R Assist — Migration 009: PubMed abstracts knowledge base (pgvector)
--
-- Two separate embedding columns support two parallel search paths:
--   endpoint_embedding  — title + background/objective/conclusions text
--                         queried by Path A (hypothesis/endpoint search)
--   method_embedding    — methods/results text
--                         queried by Path B (reconstruction/alternative search)
--
-- Requires: pgvector extension. For self-hosted PostgreSQL install from
-- github.com/pgvector/pgvector. Most managed providers include it natively.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS pubmed_abstracts (
    pmid                TEXT        PRIMARY KEY,
    title               TEXT        NOT NULL,
    authors             JSONB       NOT NULL DEFAULT '[]',
    institutions        JSONB       NOT NULL DEFAULT '[]',
    pub_year            SMALLINT,
    pub_month           SMALLINT,
    journal             TEXT,                   -- journal full title
    abstract_text       TEXT        NOT NULL,   -- full abstract for display
    endpoint_text       TEXT        NOT NULL,   -- background + objective + conclusions
    method_text         TEXT        NOT NULL,   -- methods + results
    mesh_terms          JSONB       NOT NULL DEFAULT '[]',
    cluster             TEXT        NOT NULL,   -- filter cluster that matched at ingestion
    -- 384 dims = all-MiniLM-L6-v2; update column type if embedding model changes
    endpoint_embedding  vector(384),
    method_embedding    vector(384),
    indexed_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS pubmed_pub_year_idx
    ON pubmed_abstracts (pub_year DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS pubmed_mesh_idx
    ON pubmed_abstracts USING gin (mesh_terms);

CREATE INDEX IF NOT EXISTS pubmed_cluster_idx
    ON pubmed_abstracts (cluster);

-- ---------------------------------------------------------------------------
-- Vector indexes must be created AFTER initial data load (requires > 10 000 rows).
-- Run both manually once the table is populated:
--
--   CREATE INDEX pubmed_endpoint_embedding_idx ON pubmed_abstracts
--     USING ivfflat (endpoint_embedding vector_cosine_ops) WITH (lists = 1000);
--
--   CREATE INDEX pubmed_method_embedding_idx ON pubmed_abstracts
--     USING ivfflat (method_embedding vector_cosine_ops) WITH (lists = 1000);
--
-- For very large datasets (> 1M rows) prefer HNSW:
--   CREATE INDEX ... USING hnsw (endpoint_embedding vector_cosine_ops);
--   CREATE INDEX ... USING hnsw (method_embedding vector_cosine_ops);
-- ---------------------------------------------------------------------------
