-- =============================================================================
-- Migration 108: MCTT HCE and KeraSkin documents (KoCVAM / Biosolution) and a
-- correction of migrations 106 and 107.
--  - TG 492B (method 39) describes only the SkinEthic HCE Time-to-Toxicity test
--    (no EpiOcular, no LabCyte, no MCTT in its text): the LabCyte CORNEA-MODEL24
--    serum and feeder rows added to method 39 in migration 107 are removed and
--    its note is corrected. Protocols 190/191 are the EIT (TG 492), not the TTT.
--  - MCTT HCE (TG 492): normal human corneal epithelial cells derived from normal
--    human cornea tissue (Biosolution product sheet MM331), grown 14 days in
--    Millicell inserts, shipped on agarose gel with the assay medium; the SOP v1.8
--    (2024) and protocol v1.7 do not describe the medium composition or mention
--    serum or other animal-derived components.
--  - KeraSkin (TG 439 SIT, TG 498 phototoxicity): primary cultured human
--    keratinocytes of Korean origin on Millicell inserts, shipped on agarose gel;
--    SOP v1.3 (2025) does not describe the medium composition or mention serum.
-- =============================================================================

BEGIN;

DELETE FROM method_materials
WHERE method_id = 39
  AND notes LIKE 'JaCVAM/J-TEC protocol v2.7%';

UPDATE method_materials
SET name = '{"en-us": "Reconstructed human cornea-like epithelium (SkinEthic HCE, the only model described in TG 492B)", "pt-br": "Epitélio corneano humano reconstruído (SkinEthic HCE, único modelo descrito na TG 492B)"}'::jsonb,
    notes = 'TG 492B text: SkinEthic HCE Time-to-Toxicity (TTT) test; the model is a transformed human corneal epithelial cell line in a chemically defined medium (DB-ALM 190/191, EIT protocols of the same tissue); the TTT SOPs (TTL/TTS) are not in the repository'
WHERE method_id = 39 AND kind = 'reconstructed_tissue';

UPDATE method_materials
SET notes = notes || '; MCTT HCE (Biosolution MM331 sheet, SOP v1.8, protocol v1.7): normal human corneal epithelial cells derived from normal human cornea tissue, 14-day culture in Millicell inserts, shipped on agarose gel with assay medium; medium composition not described and no serum or animal-derived component mentioned'
WHERE method_id = 9 AND kind = 'reconstructed_tissue';

UPDATE method_materials
SET notes = notes || '; KeraSkin (KoCVAM SOP of the phototoxicity assay v1.3): primary cultured human keratinocytes of Korean origin on Millicell inserts, shipped on agarose gel with the assay medium; medium composition not described and no serum mentioned'
WHERE method_id = 1 AND kind = 'reconstructed_tissue';

COMMIT;
