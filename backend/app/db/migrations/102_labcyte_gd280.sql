-- =============================================================================
-- Migration 102: LabCyte EPI-MODEL manual (J-TEC, March 2017), EpiSensA
-- brochure (SenzaGen, 2026-03-10) and OECD GD 280 (RT-HEP / RT-S9 guidance).
--  - EpiSensA (TG 442D, method 11) uses the LabCyte EPI-MODEL24 kit, a
--    reconstructed human epidermis made from normal human epidermal cells; its
--    assay medium "contains serum" (species not stated). Epi2SensA uses a
--    serum-free assay medium (TG 442D).
--  - GD 280: BCFs predicted from in vitro intrinsic clearance (RT-HEP, RT-S9)
--    can screen "whether a full in vivo fish-BCF study is warranted", "may not
--    replace in vivo fish bioaccumulation tests", and may be an alternative
--    only if in vivo testing is not technically feasible or not allowed:
--    reduction rationale for TG 319A and TG 319B (the "without live fish" text
--    of TG 319B is replaced), comparator TG 305.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET name = '{"en-us": "Reconstructed human epidermis models: LabCyte EPI-MODEL24 (EpiSensA) and EpiDerm EPI-200 (Epi2SensA)", "pt-br": "Modelos de epiderme humana reconstruída: LabCyte EPI-MODEL24 (EpiSensA) e EpiDerm EPI-200 (Epi2SensA)"}'::jsonb,
    notes = 'TG 442D text; LabCyte manual: model made by culturing normal human epidermal cells'
WHERE method_id = 11 AND kind = 'reconstructed_tissue';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (11, 'culture_supplement',
        '{"en-us": "Serum in the assay medium supplied with the LabCyte EPI-MODEL24 kit (EpiSensA); Epi2SensA uses a serum-free assay medium", "pt-br": "Soro no meio de ensaio fornecido com o kit LabCyte EPI-MODEL24 (EpiSensA); o Epi2SensA usa meio de ensaio sem soro"}'::jsonb,
        NULL, NULL, NULL,
        'LabCyte EPI-MODEL manual (J-TEC, 2017): the assay medium contains serum; species of the serum is not stated. TG 442D: Epi2SensA uses serum-free Assay Medium EPI-100-NMM');

UPDATE methods SET reduction_rationale = jsonb_build_object(
  'en-us', 'Predicted bioconcentration factors based on in vitro intrinsic clearance can be used as a screening tool to decide whether a full in vivo fish BCF study is warranted; they may not replace in vivo fish bioaccumulation tests.',
  'pt-br', 'Fatores de bioconcentração previstos com base no clearance intrínseco in vitro podem ser usados como ferramenta de triagem para decidir se um estudo completo de BCF in vivo em peixes se justifica; eles podem não substituir os testes de bioacumulação em peixes in vivo.')
WHERE id IN (54, 55);

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "In vivo fish bioconcentration study", "pt-br": "Estudo de bioconcentração in vivo em peixes"},
   "species": null, "oecd_ref": "TG 305", "r_type": "reduction", "extent": null,
   "note": {"en-us": "GD 280: in vitro based BCF predictions screen whether a full in vivo fish BCF study is warranted and may not replace it; they may be an alternative if in vivo testing is not technically feasible or not allowed",
            "pt-br": "GD 280: as previsões de BCF com dados in vitro triam se um estudo completo de BCF em peixes se justifica e podem não substituí-lo; podem ser alternativa se o teste in vivo for tecnicamente inviável ou não permitido"}}
]'::jsonb WHERE id IN (54, 55);

COMMIT;
