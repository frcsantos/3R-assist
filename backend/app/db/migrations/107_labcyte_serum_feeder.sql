-- =============================================================================
-- Migration 107: LabCyte models checked against the JaCVAM/J-TEC documents:
-- EPI-MODEL24 SIT SOP v8.3 (2011), SCT SOP v1.6 (2017), SCT peer review panel
-- report (2018), SIT SOP for medical device extracts v2.2 (2024) and
-- CORNEA-MODEL24 eye irritation protocol v2.7 (2018).
--  - Serum: both models are produced at the air-liquid interface for 13 days in
--    "an optimized medium containing 5% fetal bovine serum" (so the serum of the
--    earlier manual note is bovine). The SCT peer review report also discusses
--    serum batches.
--  - Feeder layer: keratinocytes (neonate foreskin) and corneal epithelial cells
--    (human donor cornea) are expanded on irradiated 3T3-J2 cells. The documents
--    do not state the species; 3T3-J2 is a mouse fibroblast line (general
--    knowledge, to be confirmed by the curators).
-- =============================================================================

BEGIN;

-- TG 439 (method 1) --------------------------------------------------------------
UPDATE method_materials
SET name = '{"en-us": "5% fetal bovine serum in the production medium of the LabCyte EPI-MODEL24 SIT (one of the models listed in TG 439); other models may use chemically defined media", "pt-br": "Soro fetal bovino a 5% no meio de produção do LabCyte EPI-MODEL24 SIT (um dos modelos citados na TG 439); outros modelos podem usar meios quimicamente definidos"}'::jsonb,
    species_id = (SELECT id FROM species WHERE slug = 'bovine'),
    animal_derived = TRUE,
    notes = 'JaCVAM/J-TEC SOP v8.3 (SIT): tissue cultured for 13 days at the air-liquid interface in an optimized medium containing 5% fetal bovine serum; SkinEthic RHE (DB-ALM 135): chemically defined growth medium'
WHERE id = 78;

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (1, 'biological_extract',
        '{"en-us": "Irradiated 3T3-J2 feeder cells used to expand the keratinocytes of the LabCyte EPI-MODEL24", "pt-br": "Células alimentadoras 3T3-J2 irradiadas usadas para expandir os queratinócitos do LabCyte EPI-MODEL24"}'::jsonb,
        (SELECT id FROM species WHERE slug = 'mouse'), NULL, TRUE,
        'JaCVAM/J-TEC SOP v8.3 and SCT peer review report: keratinocytes (neonate foreskin) cultured with 3T3-J2 cells as a feeder layer; species not stated in the documents (3T3-J2 is a mouse fibroblast line, to be confirmed)');

-- TG 442D (method 11) -----------------------------------------------------------
UPDATE method_materials
SET name = '{"en-us": "Serum in the LabCyte EPI-MODEL24 kit used for EpiSensA (5% fetal bovine serum in the production medium; the kit assay medium contains serum); Epi2SensA uses a serum-free assay medium", "pt-br": "Soro no kit LabCyte EPI-MODEL24 usado no EpiSensA (soro fetal bovino a 5% no meio de produção; o meio de ensaio do kit contém soro); o Epi2SensA usa meio de ensaio sem soro"}'::jsonb,
    species_id = (SELECT id FROM species WHERE slug = 'bovine'),
    animal_derived = TRUE,
    notes = 'LabCyte manual (J-TEC, 2017): assay medium contains serum; JaCVAM SOPs of the same model: production medium with 5% fetal bovine serum. TG 442D: Epi2SensA uses serum-free Assay Medium EPI-100-NMM'
WHERE id = 77;

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (11, 'biological_extract',
        '{"en-us": "Irradiated 3T3-J2 feeder cells used to expand the keratinocytes of the LabCyte EPI-MODEL24 (EpiSensA)", "pt-br": "Células alimentadoras 3T3-J2 irradiadas usadas para expandir os queratinócitos do LabCyte EPI-MODEL24 (EpiSensA)"}'::jsonb,
        (SELECT id FROM species WHERE slug = 'mouse'), NULL, TRUE,
        'JaCVAM/J-TEC SOPs of the same model; species not stated in the documents (3T3-J2 is a mouse fibroblast line, to be confirmed)');

-- TG 492 (method 9) and TG 492B (method 39): LabCyte CORNEA-MODEL24 -------------------
INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
SELECT m, 'culture_supplement',
       '{"en-us": "5% fetal bovine serum in the production medium of the LabCyte CORNEA-MODEL24 (one of the models listed in the Guideline); EpiOcular and SkinEthic HCE protocols mention no serum", "pt-br": "Soro fetal bovino a 5% no meio de produção do LabCyte CORNEA-MODEL24 (um dos modelos citados na Diretriz); os protocolos do EpiOcular e do SkinEthic HCE não citam soro"}'::jsonb,
       (SELECT id FROM species WHERE slug = 'bovine'), NULL, TRUE,
       'JaCVAM/J-TEC protocol v2.7 (2018): cultured for 13 days at the air-liquid interface in an optimized medium containing 5% fetal bovine serum'
FROM (VALUES (9), (39)) AS t(m);

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
SELECT m, 'biological_extract',
       '{"en-us": "Irradiated 3T3-J2 feeder cells used to expand the corneal epithelial cells of the LabCyte CORNEA-MODEL24", "pt-br": "Células alimentadoras 3T3-J2 irradiadas usadas para expandir as células epiteliais da córnea do LabCyte CORNEA-MODEL24"}'::jsonb,
       (SELECT id FROM species WHERE slug = 'mouse'), NULL, TRUE,
       'JaCVAM/J-TEC protocol v2.7: normal human corneal epithelial cells from a donor cornea cultured with 3T3-J2 cells as a feeder layer; species not stated in the document (3T3-J2 is a mouse fibroblast line, to be confirmed)'
FROM (VALUES (9), (39)) AS t(m);

COMMIT;
