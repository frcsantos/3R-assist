-- =============================================================================
-- Migration 099: data checked against the full texts of TG 430, 437, 438,
-- 212, 236, 319A, 319B, 421, 422, 493 and 495.
--  - Materials: rat skin discs from humanely killed rats aged 28-30 days
--    (TG 430); bovine corneas from cattle killed for human consumption or other
--    commercial uses (TG 437); chicken eyes from slaughterhouses (TG 438);
--    RT-HEP and RT-S9 from commercial sources or prepared from trout in-house
--    (TG 319A/B); human ER-alpha produced in baculovirus-infected insect cells
--    (TG 493); chemical probes of the ROS assay (TG 495).
--  - TG 421 states it "is not an alternative to, nor does it replace" TG 414,
--    415, 416 or 443 and "will not provide evidence for definite claims of no
--    effects": the reduction text that said it could reduce the need for more
--    extensive studies "if no toxic effects are observed" is rewritten.
--  - TG 422: "can serve as an alternative to conducting two separate tests"
--    (TG 407 and TG 421), with fewer animals.
--  - TG 495 (para. 5) calls TG 432 "an alternative method for in vivo
--    phototoxicity testing": comparator recorded for TG 432 and TG 495.
-- =============================================================================

BEGIN;

-- Materials -----------------------------------------------------------------------
UPDATE method_materials SET notes = 'TG 430 text: skin discs from humanely killed rats aged 28-30 days'
WHERE method_id = 4 AND kind = 'tissue';

UPDATE method_materials SET notes = 'TG 437 text: corneas from freshly slaughtered cattle killed for human consumption or other commercial uses; only healthy animals suitable for the human food chain'
WHERE method_id = 6 AND kind = 'tissue';

UPDATE method_materials SET notes = 'TG 438 text: eyes from slaughterhouse chickens killed for human consumption, eliminating the need for laboratory animals'
WHERE method_id = 7 AND kind = 'tissue';

UPDATE method_materials SET notes = 'TG 319A text: cryopreserved RT-HEP from commercial sources or prepared in-house from rainbow trout (Annex 2)'
WHERE method_id = 54 AND kind = 'primary_cells';

UPDATE method_materials SET notes = 'TG 319B text: RT-S9 from commercial sources or prepared in-house from rainbow trout (Annex 2)'
WHERE method_id = 55 AND kind = 'subcellular_fraction';

UPDATE method_materials SET notes = 'TG 493 text: cell-free human ER-alpha (full length, produced in baculovirus-infected insect cells, or ligand-binding domain) with radiolabelled [3H]17beta-estradiol; no intrinsic metabolic capability'
WHERE method_id = 42 AND kind = 'recombinant_protein';

UPDATE method_materials
SET name = '{"en-us": "Cell-free chemical system: irradiated test chemical with p-nitrosodimethylaniline (RNO) and imidazole (singlet oxygen) and nitroblue tetrazolium (superoxide anion), read by spectrophotometry", "pt-br": "Sistema químico acelular: substância irradiada com p-nitrosodimetilanilina (RNO) e imidazol (oxigênio singlete) e nitroazul de tetrazólio (ânion superóxido), com leitura por espectrofotometria"}'::jsonb,
    notes = 'TG 495 text'
WHERE method_id = 50 AND kind = 'synthetic_reagent';

UPDATE method_materials
SET name = '{"en-us": "Fertilised fish eggs, embryo and sac-fry stages (zebrafish detailed in Annex 1; other species in Table 1)", "pt-br": "Ovos fertilizados de peixe, estágios de embrião e alevino (zebrafish detalhado no Anexo 1; outras espécies na Tabela 1)"}'::jsonb,
    species_id = (SELECT id FROM species WHERE slug = 'zebrafish'),
    notes = 'TG 212 text: detailed guidance for zebrafish; other species with available experience are not excluded'
WHERE method_id = 51 AND kind = 'embryo';

UPDATE method_materials SET notes = 'TG 236 text: newly fertilised zebrafish eggs exposed for 96 h'
WHERE method_id = 53 AND kind = 'embryo';

-- TG 421 reduction text ----------------------------------------------------------------
UPDATE methods SET reduction_rationale = jsonb_build_object(
  'en-us', 'The Guideline generates limited information and can be used as a screening step or as a dose range finding study for more extensive reproduction/developmental studies; positive results contribute to decisions on the necessity and timing of additional testing. It is not an alternative to, and does not replace, TG 414, 415, 416 or 443.',
  'pt-br', 'A Diretriz gera informação limitada e pode ser usada como etapa de triagem ou como estudo de determinação de faixa de dose para estudos mais extensos de toxicidade reprodutiva e do desenvolvimento; resultados positivos contribuem para decidir a necessidade e o momento de testes adicionais. Não é alternativa nem substitui as TGs 414, 415, 416 ou 443.')
WHERE id = 36;

-- Procedures avoided ----------------------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "More extensive reproduction/developmental toxicity studies", "pt-br": "Estudos mais extensos de toxicidade reprodutiva e do desenvolvimento"},
   "species": "rat", "oecd_ref": "TG 414, 415, 416, 443", "r_type": "reduction", "extent": null,
   "note": {"en-us": "TG 421 is not an alternative to these studies; it can serve as a dose range finding or initial screening step",
            "pt-br": "A TG 421 não é alternativa a esses estudos; pode servir como etapa de determinação de faixa de dose ou de triagem inicial"}},
  {"name": {"en-us": "More extensive reproduction/developmental toxicity studies", "pt-br": "Estudos mais extensos de toxicidade reprodutiva e do desenvolvimento"},
   "species": "rat", "oecd_ref": "TG 414, 415, 416, 443", "r_type": "refinement", "extent": null,
   "note": {"en-us": "The guiding principles of OECD GD 19 on humane endpoints must be followed",
            "pt-br": "Devem ser seguidos os princípios do GD 19 da OCDE sobre desfechos humanitários"}}
]'::jsonb WHERE id = 36;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Separate repeated-dose and reproduction/developmental toxicity studies", "pt-br": "Estudos separados de toxicidade por doses repetidas e de toxicidade reprodutiva e do desenvolvimento"},
   "species": "rat", "oecd_ref": "TG 407, TG 421", "r_type": "reduction", "extent": null,
   "note": {"en-us": "TG 422 text: can serve as an alternative to conducting two separate tests, with a smaller number of animals",
            "pt-br": "Texto da TG 422: pode servir como alternativa à realização de dois testes separados, com menor número de animais"}}
]'::jsonb WHERE id = 37;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "In vivo phototoxicity testing", "pt-br": "Testes de fototoxicidade in vivo"},
   "species": null, "oecd_ref": null, "r_type": "replacement", "extent": "total",
   "note": {"en-us": "TG 495 (para. 5) describes TG 432 as an alternative method for in vivo phototoxicity testing",
            "pt-br": "A TG 495 (par. 5) descreve a TG 432 como método alternativo aos testes de fototoxicidade in vivo"}}
]'::jsonb WHERE id = 16;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "In vivo phototoxicity testing", "pt-br": "Testes de fototoxicidade in vivo"},
   "species": null, "oecd_ref": null, "r_type": "replacement", "extent": "partial",
   "note": {"en-us": "TG 495 text: screening tool; a negative result may support a decision that no further photosafety assessment is warranted, while photoreactive results may need additional data",
            "pt-br": "Texto da TG 495: ferramenta de triagem; um resultado negativo pode apoiar a decisão de que nenhuma avaliação adicional de fotossegurança é necessária, e resultados fotorreativos podem exigir dados adicionais"}}
]'::jsonb WHERE id = 50;

COMMIT;
