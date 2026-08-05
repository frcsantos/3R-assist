-- =============================================================================
-- Migration 027: documents catalogue
-- Source documents for methods / protocols / guidelines / regulations.
-- =============================================================================

CREATE TABLE documents (
    id          SERIAL      PRIMARY KEY,
    slug        TEXT        NOT NULL UNIQUE,
    doc_ref     TEXT        NOT NULL,
    "date"      DATE,
    category    TEXT        NOT NULL
                    CHECK (category IN (
                        'method_protocol',
                        'guideline',
                        'regulation'
                    )),
    url         TEXT
);

CREATE INDEX idx_documents_category ON documents (category);
CREATE INDEX idx_documents_date ON documents ("date");

COMMENT ON TABLE documents IS
  'Catalogue of source documents (method protocols, guidelines, regulations).';
COMMENT ON COLUMN documents.slug IS
  'Unique URL-safe identifier for the document.';
COMMENT ON COLUMN documents.doc_ref IS
  'Human-readable document reference / citation key (e.g. OECD TG 439, RN 18/2014).';
COMMENT ON COLUMN documents."date" IS
  'Publication / adoption / issuance date of the document.';
COMMENT ON COLUMN documents.category IS
  'Document kind: method_protocol | guideline | regulation.';
COMMENT ON COLUMN documents.url IS
  'URL of the document, when available.';
