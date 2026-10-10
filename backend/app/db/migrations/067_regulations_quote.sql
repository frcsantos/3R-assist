-- Migration 067: regulations.regulatory_citation → regulatory_quote (short quotes).
-- Already applied to the Neon database from regulations_quotes_oecd_endpoints.sql,
-- which also set regulatory_endpoints = '{}' for OECD rows. Recorded here for history.
-- Full references remain in documents via regulations.regulatory_doc_id.
-- API still exposes the field as `regulatory_citation` (alias in repositories/methods.py).
ALTER TABLE regulations RENAME COLUMN regulatory_citation TO regulatory_quote;
