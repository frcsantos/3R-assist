-- =============================================================================
-- Migration 035: documents.category → categories (JSONB multi-select);
--   add institution (localized JSONB) immediately left of url; reorder columns.
-- Target order:
--   id, slug, doc_citation, description, date, categories, institution, url
-- =============================================================================

BEGIN;

-- Drop FKs that reference documents(id) before rebuild.
DO $$
DECLARE
  rec record;
BEGIN
  FOR rec IN
    SELECT con.conname, rel.relname AS table_name
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class ref ON ref.oid = con.confrelid
    JOIN pg_namespace nsp ON nsp.oid = ref.relnamespace
    WHERE con.contype = 'f'
      AND nsp.nspname = 'public'
      AND ref.relname = 'documents'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I DROP CONSTRAINT IF EXISTS %I',
      rec.table_name,
      rec.conname
    );
  END LOOP;
END $$;

CREATE TABLE documents_new (
    id            SERIAL      PRIMARY KEY,
    slug          TEXT        NOT NULL UNIQUE,
    doc_citation  JSONB       NOT NULL,
    description   JSONB       NOT NULL
                      DEFAULT '{"en-us":"","pt-br":""}'::jsonb,
    "date"        DATE,
    categories    JSONB       NOT NULL,
    institution   JSONB,
    url           TEXT,
    CONSTRAINT documents_categories_is_array CHECK (
      jsonb_typeof(categories) = 'array'
    ),
    CONSTRAINT documents_categories_not_empty CHECK (
      jsonb_array_length(categories) >= 1
    ),
    CONSTRAINT documents_categories_values_check CHECK (
      categories <@ '["method_protocol","guideline","regulation","other"]'::jsonb
    )
);

INSERT INTO documents_new (
    id, slug, doc_citation, description, "date", categories, institution, url
)
SELECT
    id,
    slug,
    doc_citation,
    COALESCE(description, '{"en-us":"","pt-br":""}'::jsonb),
    "date",
    jsonb_build_array(category),
    NULL,
    url
FROM documents;

SELECT setval(
    pg_get_serial_sequence('documents_new', 'id'),
    COALESCE((SELECT MAX(id) FROM documents_new), 1),
    true
);

DROP TABLE documents;
ALTER TABLE documents_new RENAME TO documents;
ALTER SEQUENCE documents_new_id_seq RENAME TO documents_id_seq;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'documents_new_pkey'
  ) THEN
    ALTER TABLE documents RENAME CONSTRAINT documents_new_pkey TO documents_pkey;
  END IF;
  IF EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'documents_new_slug_key'
  ) THEN
    ALTER TABLE documents RENAME CONSTRAINT documents_new_slug_key TO documents_slug_key;
  END IF;
END $$;

CREATE INDEX idx_documents_categories ON documents USING gin (categories);
CREATE INDEX idx_documents_date ON documents ("date");

COMMENT ON TABLE documents IS
  'Catalogue of source documents (method protocols, guidelines, regulations).';
COMMENT ON COLUMN documents.slug IS
  'Unique URL-safe identifier for the document.';
COMMENT ON COLUMN documents.doc_citation IS
  'Localized document citation / reference key: {"en-us": "...", "pt-br": "..."} (e.g. OECD TG 439, RN 18/2014).';
COMMENT ON COLUMN documents.description IS
  'Localized document description: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN documents."date" IS
  'Publication / adoption / issuance date of the document.';
COMMENT ON COLUMN documents.categories IS
  'Document kinds (multi-select JSON array): method_protocol | guideline | regulation | other.';
COMMENT ON COLUMN documents.institution IS
  'Localized issuing / responsible institution: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN documents.url IS
  'URL of the document, when available.';

-- Restore FKs from methods / regulations.
ALTER TABLE methods
  ADD CONSTRAINT fk_methods_source_doc
  FOREIGN KEY (source_doc_id) REFERENCES documents(id) ON DELETE SET NULL;

ALTER TABLE regulations
  ADD CONSTRAINT fk_regulations_regulatory_doc
  FOREIGN KEY (regulatory_doc_id) REFERENCES documents(id) ON DELETE SET NULL;

COMMIT;
