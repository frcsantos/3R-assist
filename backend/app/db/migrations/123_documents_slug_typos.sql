-- =============================================================================
-- Migration 123: typos in documents.slug (and one in a citation).
--  - Doc 10 (Ph. Eur. 2.6.32): "endoxins" -> "endotoxins".
--  - Doc 40 (TG 490): "usingthe" -> "using-the"; the same missing space is in
--    doc_citation ("Usingthe" -> "Using the").
--  - Doc 41 (TG 494): "494--2026-07-02vitrigel" -> "494-2026-07-02-vitrigel".
-- Public URLs /explore/documents/<slug> of these three documents change.
-- =============================================================================

BEGIN;

UPDATE documents
SET slug = replace(slug, 'bacterial-endoxins', 'bacterial-endotoxins')
WHERE slug LIKE '%bacterial-endoxins%';

UPDATE documents
SET slug = replace(slug, 'usingthe', 'using-the'),
    doc_citation = replace(doc_citation::text, 'Usingthe', 'Using the')::jsonb
WHERE slug LIKE '%usingthe%';

UPDATE documents
SET slug = replace(slug, '494--2026-07-02vitrigel', '494-2026-07-02-vitrigel')
WHERE slug LIKE '%494--2026-07-02vitrigel%';

COMMIT;
