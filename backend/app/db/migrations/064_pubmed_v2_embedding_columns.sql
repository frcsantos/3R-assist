-- =============================================================================
-- Migration 064: Add v2 embedding columns (1024 dims) for BAAI/bge-m3
--
-- These columns run in parallel with the existing vector(384) columns so that
-- production keeps serving searches on the old embeddings while re-embedding
-- runs in the background (zero-downtime migration).
--
-- Steps after applying this migration:
--   1. Run scripts/re_embed_pubmed_bge_m3.py   (fills *_v2 columns, resumable)
--   2. Build HNSW indexes on *_v2 columns      (see comments below)
--   3. Update repository.py to use *_v2 columns + hnsw.ef_search
--   4. Update EMBEDDING_MODEL=BAAI/bge-m3 in .env and restart backend
--   5. Validate, then run migration 065 to drop v1 columns and rename v2 → v1
--
-- HNSW index build (run manually once re-embedding is complete):
--
--   SET maintenance_work_mem = '1800MB';
--   SET max_parallel_maintenance_workers = 15;
--   SET synchronous_commit = off;
--
--   CREATE INDEX pubmed_endpoint_embedding_v2_idx
--     ON pubmed_abstracts
--     USING hnsw (endpoint_embedding_v2 vector_cosine_ops);
--
--   -- After the first index completes:
--   CREATE INDEX pubmed_method_embedding_v2_idx
--     ON pubmed_abstracts
--     USING hnsw (method_embedding_v2 vector_cosine_ops);
-- =============================================================================

ALTER TABLE pubmed_abstracts
    ADD COLUMN IF NOT EXISTS endpoint_embedding_v2 vector(1024),
    ADD COLUMN IF NOT EXISTS method_embedding_v2   vector(1024);
