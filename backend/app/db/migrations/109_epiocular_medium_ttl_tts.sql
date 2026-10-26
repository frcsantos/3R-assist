-- =============================================================================
-- Migration 109: EpiOcular medium (MatTek product page) and the SkinEthic HCE
-- Time-to-Toxicity SOPs (DB-ALM TTL and TTS, version 2, June 2020).
--  - EpiOcular (MatTek page): normal human epidermal keratinocytes, single
--    donor, neonatal foreskin; DMEM base with epidermal growth factor, insulin,
--    hydrocortisone and other proprietary stimulators; "Serum: None"; gentamicin
--    5 ug/ml and amphotericin B 0.25 ug/ml; phenol red; shipped at 4 C on
--    medium-supplemented agarose gel. The species of insulin and EGF is not
--    stated, and the other stimulators are proprietary.
--  - SkinEthic HCE TTL/TTS (TG 492B): transformed human corneal epithelial cell
--    line grown in a "chemically defined medium"; the maintenance medium and the
--    model are proprietary to EPISKIN SA and the composition is in a technical
--    data sheet sent by e-mail; no serum or animal-derived component is
--    mentioned; shipped on semi-solid agar medium.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET notes = notes || '; EpiOcular (MatTek product page): NHEK from a single neonatal-foreskin donor, medium DMEM with EGF, insulin, hydrocortisone and proprietary stimulators, "Serum: None", gentamicin and amphotericin B added'
WHERE method_id = 9 AND kind = 'reconstructed_tissue';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (9, 'culture_supplement',
        '{"en-us": "EpiOcular culture medium: DMEM with epidermal growth factor, insulin, hydrocortisone and proprietary stimulators; serum-free (species of insulin and growth factor not stated)", "pt-br": "Meio de cultura do EpiOcular: DMEM com fator de crescimento epidérmico, insulina, hidrocortisona e estimuladores proprietários; sem soro (espécie da insulina e do fator de crescimento não informada)"}'::jsonb,
        NULL, NULL, NULL,
        'MatTek EpiOcular product page (tech specs): "Serum: None"; antibiotics gentamicin 5 ug/ml and amphotericin B 0.25 ug/ml; proprietary stimulators of non-keratinizing epithelial differentiation are not described');

UPDATE method_materials
SET notes = 'TG 492B text: SkinEthic HCE Time-to-Toxicity (TTT) test; DB-ALM TTL and TTS protocols (version 2, June 2020): transformed human corneal epithelial cell line cultured at the air-liquid interface in a chemically defined medium; the model and the maintenance medium are proprietary to EPISKIN SA, with the composition in a technical data sheet and certificate of analysis sent by the supplier; no serum or animal-derived component is mentioned; tissues shipped on semi-solid agar medium'
WHERE method_id = 39 AND kind = 'reconstructed_tissue';

COMMIT;
