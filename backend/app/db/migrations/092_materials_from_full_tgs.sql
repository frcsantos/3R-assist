-- =============================================================================
-- Migration 092: method_materials updated from the full texts of the test
-- guidelines added to docs/oecd_files (TG 471, 473, 476, 487, 490, 460, 432,
-- 456, 455, 458, 442D, 442E, 439, 431, 492, 492B, 491, 494, 435, 496) and from
-- the full text of GD 129.
--   - S9: prepared from livers of rodents (generally rats) treated with
--     enzyme-inducing agents; recommended by default; commercial supply is not
--     mentioned in any of the five guidelines.
--   - Serum / supplements recorded as culture_supplement with the percentage
--     and type stated in the text.
--   - TG 473, 476, 487 mention no serum; TG 439, 431, 492 and 492B state no
--     medium composition (proprietary models): not recorded.
-- =============================================================================

BEGIN;

INSERT INTO species (slug, scientific_name, name, taxon_group, is_vertebrate, sort_order) VALUES
  ('horse', 'Equus ferus caballus', '{"en-us": "Horse", "pt-br": "Cavalo"}', 'mammal', TRUE, 14);

-- S9 notes --------------------------------------------------------------------
UPDATE method_materials SET notes =
  'TG 471 text: most commonly used system; S9 from rodent livers treated with Aroclor 1254 or phenobarbitone + beta-naphthoflavone; commercial supply not mentioned'
WHERE method_id = 17 AND kind = 'metabolic_activation';

UPDATE method_materials mm SET notes =
  'TG ' || t.tg || ' text: S9 from livers of rodents (generally rats) treated with enzyme-inducing agents (Aroclor 1254 or phenobarbitone + beta-naphthoflavone); recommended by default; commercial supply not mentioned'
FROM (VALUES (45, '473'), (18, '476'), (46, '490')) AS t(method_id, tg)
WHERE mm.method_id = t.method_id AND mm.kind = 'metabolic_activation';

-- Cell line species / notes ---------------------------------------------------------
UPDATE method_materials SET notes = 'TG 490 text: TK6 human lymphoblastoid cell line'
WHERE method_id = 46 AND name->>'en-us' = 'TK6 tk+/- cells';

UPDATE method_materials
SET species_id = (SELECT id FROM species WHERE slug = 'human'), origin = 'human',
    notes = 'TG 442D text: KeratinoSens and LuSens use immortalised cell lines derived from human keratinocytes; α-Sens species not stated'
WHERE method_id = 11 AND kind = 'cell_line';

-- Matrices ----------------------------------------------------------------------------
UPDATE method_materials
SET kind = 'matrix',
    name = '{"en-us": "Proteinaceous gel matrix (protein, e.g. keratin, collagen or mixtures of proteins) forming the membrane barrier", "pt-br": "Matriz de gel proteico (proteína, por exemplo queratina, colágeno ou misturas de proteínas) que forma a barreira de membrana"}'::jsonb,
    origin = NULL, animal_derived = NULL,
    notes = 'TG 435 text (para. 17); origin of the proteins is not stated'
WHERE method_id = 5;

UPDATE method_materials SET notes = 'TG 496 text: acellular reagent of proteins, glycoproteins, carbohydrates, lipids; origin of the components is not stated'
WHERE method_id = 49;

-- New rows --------------------------------------------------------------------------------
INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (19, 'metabolic_activation',
        '{"en-us": "Exogenous metabolic activation system (usually S9 from rat liver)", "pt-br": "Sistema exógeno de ativação metabólica (normalmente S9 de fígado de rato)"}'::jsonb,
        (SELECT id FROM species WHERE slug = 'rat'), 'animal', TRUE,
        'TG 487 text: S9 from livers of rodents (generally rats) treated with enzyme-inducing agents; recommended by default unless another system is justified');

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
SELECT v.method_id, 'culture_supplement',
       jsonb_build_object('en-us', v.en, 'pt-br', v.pt),
       (SELECT s.id FROM species s WHERE s.slug = v.species),
       'animal', v.animal_derived, v.notes
FROM (VALUES
  (8,  '10% heat-inactivated fetal calf/bovine serum (FCS/FBS) in the MDCK culture medium', 'Soro fetal bovino (FCS/FBS) inativado pelo calor a 10% no meio de cultura das células MDCK', 'bovine', TRUE, 'TG 460 text'),
  (16, '10% new-born calf serum in the BALB/c 3T3 culture medium (DMEM)', 'Soro de bezerro recém-nascido a 10% no meio de cultura das células BALB/c 3T3 (DMEM)', 'bovine', TRUE, 'TG 432 text'),
  (22, '10% new-born calf serum (NCS) in the 3T3 culture medium (DMEM)', 'Soro de bezerro recém-nascido (NCS) a 10% no meio de cultura das células 3T3 (DMEM)', 'bovine', TRUE, 'GD 129 text'),
  (43, 'Serum in the H295R culture medium (Nu-Serum or a comparable serum)', 'Soro no meio de cultura das células H295R (Nu-Serum ou soro comparável)', NULL, TRUE, 'TG 456 text; serum species not stated'),
  (41, 'Fetal bovine serum, including dextran-charcoal-treated FBS (DCC-FBS), in the culture medium', 'Soro fetal bovino, incluindo soro tratado com carvão e dextrano (DCC-FBS), no meio de cultura', 'bovine', TRUE, 'TG 455 text'),
  (44, 'Fetal bovine serum, including dextran-coated-charcoal-treated FBS (DCC-FBS), in the culture medium', 'Soro fetal bovino, incluindo soro tratado com carvão revestido de dextrano (DCC-FBS), no meio de cultura', 'bovine', TRUE, 'TG 458 text'),
  (40, '10% fetal bovine serum (FBS) in the SIRC culture medium (MEM)', 'Soro fetal bovino (FBS) a 10% no meio de cultura das células SIRC (MEM)', 'bovine', TRUE, 'TG 491 text'),
  (47, '5% heat-inactivated fetal bovine serum in the hCE culture medium', 'Soro fetal bovino inativado pelo calor a 5% no meio de cultura dos modelos hCE', 'bovine', TRUE, 'TG 494 text'),
  (46, 'Horse serum (heat-inactivated) in the RPMI medium used for mutant selection', 'Soro de cavalo (inativado pelo calor) no meio RPMI usado na seleção de mutantes', 'horse', TRUE, 'TG 490 text'),
  (12, '10% fetal bovine serum in the h-CLAT (THP-1) culture medium and 10% foetal calf serum in the U-SENS (U937) culture medium', 'Soro fetal bovino a 10% no meio de cultura do h-CLAT (THP-1) e soro fetal de bezerro a 10% no meio do U-SENS (U937)', 'bovine', TRUE, 'TG 442E text'),
  (11, 'Serum in the KeratinoSens culture medium (type of serum to be agreed with the authority; xeno-free adaptation with human serum available); α-Sens and Epi2SensA are serum/FBS free', 'Soro no meio de cultura do KeratinoSens (tipo de soro a combinar com a autoridade; há adaptação sem material animal com soro humano); α-Sens e Epi2SensA não usam soro', NULL, NULL, 'TG 442D text; serum species not stated')
) AS v(method_id, en, pt, species, animal_derived, notes);

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (47, 'matrix',
        '{"en-us": "Collagen vitrigel membrane (CVM) chamber supporting the hCE models", "pt-br": "Câmara com membrana de colágeno vitrigel (CVM) que sustenta os modelos hCE"}'::jsonb,
        NULL, NULL, NULL, 'TG 494 text; origin of the collagen is not stated');

COMMIT;
