-- =============================================================================
-- Migration 104: reconstructed human epidermis models (TG 439, TG 431) checked
-- against the DB-ALM protocol 135 (SkinEthic RHE skin irritation test) and the
-- TSAR records of EpiSkin and epiCS (EST-1000), plus the LabCyte manual.
--  - SkinEthic RHE: normal human keratinocytes on an inert polycarbonate filter,
--    "chemically defined growth medium"; the protocol mentions no serum or
--    other animal-derived component, but does not say "serum-free" either.
--  - LabCyte EPI-MODEL24: the assay medium contains serum (species not stated).
--  - EpiSkin and epiCS: TSAR pages describe the model only (no medium).
--  So the media of the models listed in TG 439 differ; there is no common rule.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET name = '{"en-us": "Reconstructed human epidermis (RhE) models (TG 439 lists EpiDerm SIT, EpiSkin, SkinEthic RHE, LabCyte EPI-MODEL24 SIT, epiCS, Skin+ and KeraSkin)", "pt-br": "Modelos de epiderme humana reconstruída (RhE) (a TG 439 cita EpiDerm SIT, EpiSkin, SkinEthic RHE, LabCyte EPI-MODEL24 SIT, epiCS, Skin+ e KeraSkin)"}'::jsonb,
    notes = 'TG 439 text; SkinEthic RHE (DB-ALM protocol 135): normal human keratinocytes on a polycarbonate filter, chemically defined growth medium, no serum mentioned; EpiSkin and epiCS (TSAR): model description only'
WHERE method_id = 1 AND kind = 'reconstructed_tissue';

UPDATE method_materials
SET name = '{"en-us": "Reconstructed human epidermis (RHE) models (TG 431 lists EpiSkin, EpiDerm SCT, SkinEthic RHE, epiCS and EST-1000)", "pt-br": "Modelos de epiderme humana reconstruída (RHE) (a TG 431 cita EpiSkin, EpiDerm SCT, SkinEthic RHE, epiCS e EST-1000)"}'::jsonb,
    notes = 'TG 431 text; epiCS (previously EST-1000), TSAR: reconstructed epidermis of proliferating and differentiating keratinocytes, medium not described'
WHERE method_id = 3 AND kind = 'reconstructed_tissue';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (1, 'culture_supplement',
        '{"en-us": "Serum in the assay medium of the LabCyte EPI-MODEL24 SIT kit (one of the models listed in TG 439); other models may use chemically defined media", "pt-br": "Soro no meio de ensaio do kit LabCyte EPI-MODEL24 SIT (um dos modelos citados na TG 439); outros modelos podem usar meios quimicamente definidos"}'::jsonb,
        NULL, NULL, NULL,
        'LabCyte manual (J-TEC, 2017): the assay medium contains serum, species not stated; SkinEthic RHE (DB-ALM 135): chemically defined growth medium');

COMMIT;
