-- =============================================================================
-- Migration 097: USP <86> "Bacterial Endotoxins Test Using Recombinant
-- Reagents" (proposed new chapter) added to the documents catalogue and
-- cited in the rFC material (method 56).
-- The chapter describes rFC and the recombinant cascade reagent (rCR) as
-- "nonanimal derived reagents", based on the gene sequences of horseshoe crab
-- factors (Limulus polyphemus, Tachypleus tridentatus, Carcinoscorpius
-- rotundicauda), with endpoint fluorescence or chromogenic detection. It is
-- an alternative test that must meet General Notices 6.30, and regulators may
-- require comparative data against <85>. The file states no publication date.
-- =============================================================================

BEGIN;

INSERT INTO documents (slug, doc_citation, description, date, categories, institution, url)
VALUES (
  'usp-86-bacterial-endotoxins-test-using-recombinant-reagents',
  '{"en-us": "United States Pharmacopeia (USP). General Chapter <86> Bacterial Endotoxins Test Using Recombinant Reagents (proposed new chapter). Rockville: United States Pharmacopeial Convention.", "pt-br": "United States Pharmacopeia (USP). Capítulo geral <86> Bacterial Endotoxins Test Using Recombinant Reagents (proposta de novo capítulo). Rockville: United States Pharmacopeial Convention."}'::jsonb,
  '{"en-us": "Proposed USP chapter that adds alternative bacterial endotoxins techniques using nonanimal derived recombinant reagents (recombinant factor C or recombinant cascade reagent) to chapter <85>, with endpoint fluorescence or chromogenic detection.", "pt-br": "Proposta de capítulo da USP que acrescenta ao capítulo <85> técnicas alternativas de endotoxinas bacterianas com reagentes recombinantes não derivados de animais (fator C recombinante ou reagente em cascata recombinante), com detecção por fluorescência de ponto final ou cromogênica."}'::jsonb,
  NULL,
  '["method_protocol"]'::jsonb,
  '{"en-us": "United States Pharmacopeial Convention (USP)", "pt-br": "United States Pharmacopeial Convention (USP)"}'::jsonb,
  NULL
);

UPDATE method_materials
SET notes = 'Ph. Eur. 2.6.32 and USP <86> (proposed): rFC or recombinant cascade reagent based on the gene sequences of horseshoe crab factors; USP <86> calls them nonanimal derived reagents'
WHERE method_id = 56 AND kind = 'recombinant_protein';

COMMIT;
