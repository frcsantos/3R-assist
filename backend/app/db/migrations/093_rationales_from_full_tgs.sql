-- =============================================================================
-- Migration 093: 3R rationales checked against the full texts of TG 420, 425,
-- 428, 429, 442A, 442B, 442C and the defined-approach guidelines (TG 467, 497).
--
--  - TG 429, 442A and 442B state that, compared with the guinea pig tests
--    (TG 406), the LLNA and its two non-radioactive modifications offer
--    reduction and refinement ("substantial refinement (less pain and
--    distress)"). The previous 442A/442B refinement text (avoiding radioactive
--    isotopes) was an operator-safety argument, not the guideline's; replaced.
--  - TG 442B: placeholder reduction text written; TG 442A: reduction added.
--  - TG 420: "uses fewer animals and causes less suffering than the traditional
--    methods"; "significantly" was not in the text.
--  - TG 425: "minimizing the number of animals required"; the guideline makes
--    no refinement claim, so the placeholder refinement text is cleared.
--  - TG 442C/D/E (partial replacement) confirmed: "may not be sufficient as
--    stand-alone methods"; only kDPRA positives stand alone (subcategory 1A).
--  - animal_procedures_avoided: guinea pig tests (TG 406) for TG 429/442A/442B.
-- =============================================================================

BEGIN;

UPDATE methods SET refinement_rationale = jsonb_build_object(
  'en-us', 'The LLNA offers a substantial refinement (less pain and distress) in the way animals are used for skin sensitisation testing, an advantage over the guinea pig tests (TG 406).',
  'pt-br', 'O LLNA oferece um refinamento substancial (menos dor e sofrimento) na forma como os animais são usados nos testes de sensibilização cutânea, uma vantagem em relação aos testes em cobaias (TG 406).')
WHERE id = 13;

UPDATE methods SET
  reduction_rationale = jsonb_build_object(
    'en-us', 'Compared with the guinea pig tests (TG 406), the LLNA: DA has the potential to reduce animal use for skin sensitisation testing.',
    'pt-br', 'Em comparação com os testes em cobaias (TG 406), o LLNA: DA tem potencial para reduzir o uso de animais nos testes de sensibilização cutânea.'),
  refinement_rationale = jsonb_build_object(
    'en-us', 'The LLNA: DA offers a substantial refinement (less pain and distress) in the way animals are used for skin sensitisation testing, an advantage over the guinea pig tests (TG 406).',
    'pt-br', 'O LLNA: DA oferece um refinamento substancial (menos dor e sofrimento) na forma como os animais são usados nos testes de sensibilização cutânea, uma vantagem em relação aos testes em cobaias (TG 406).')
WHERE id = 14;

UPDATE methods SET
  reduction_rationale = jsonb_build_object(
    'en-us', 'Like other LLNA methods, the LLNA: BrdU-ELISA has the potential to reduce animal use compared with the guinea pig tests (TG 406); not requiring a radiolabel may allow wider use of mice and further reduce the use of guinea pigs.',
    'pt-br', 'Como os demais métodos LLNA, o LLNA: BrdU-ELISA tem potencial para reduzir o uso de animais em comparação com os testes em cobaias (TG 406); por não exigir marcação radioativa, pode ampliar o uso de camundongos e reduzir ainda mais o uso de cobaias.'),
  refinement_rationale = jsonb_build_object(
    'en-us', 'The LLNA: BrdU-ELISA offers a substantial refinement in the way animals are used for skin sensitisation testing, an advantage over the guinea pig tests (TG 406).',
    'pt-br', 'O LLNA: BrdU-ELISA oferece um refinamento substancial na forma como os animais são usados nos testes de sensibilização cutânea, uma vantagem em relação aos testes em cobaias (TG 406).')
WHERE id = 15;

UPDATE methods SET reduction_rationale = jsonb_build_object(
  'en-us', 'The method uses a stepwise procedure with fixed doses, avoids death as an endpoint and uses fewer animals than the traditional methods.',
  'pt-br', 'O método utiliza um procedimento gradual com doses fixas, evita a morte como desfecho e usa menos animais do que os métodos tradicionais.')
WHERE id = 23;

UPDATE methods SET
  reduction_rationale = jsonb_build_object(
    'en-us', 'The procedure minimises the number of animals required to estimate acute oral toxicity; its stopping criteria keep the number of animals low.',
    'pt-br', 'O procedimento minimiza o número de animais necessários para estimar a toxicidade oral aguda; seus critérios de parada mantêm baixo o número de animais.'),
  refinement_rationale = NULL
WHERE id = 25;

-- Procedures avoided ----------------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Skin sensitisation tests in guinea pigs", "pt-br": "Testes de sensibilização cutânea em cobaias"},
   "species": "guinea_pig", "oecd_ref": "TG 406", "r_type": "reduction", "extent": null},
  {"name": {"en-us": "Skin sensitisation tests in guinea pigs", "pt-br": "Testes de sensibilização cutânea em cobaias"},
   "species": "guinea_pig", "oecd_ref": "TG 406", "r_type": "refinement", "extent": null},
  {"name": {"en-us": "Standard LLNA group design", "pt-br": "Delineamento padrão do LLNA"},
   "species": "mouse", "oecd_ref": "TG 429", "r_type": "reduction", "extent": null}
]'::jsonb WHERE id = 13;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Skin sensitisation tests in guinea pigs", "pt-br": "Testes de sensibilização cutânea em cobaias"},
   "species": "guinea_pig", "oecd_ref": "TG 406", "r_type": "reduction", "extent": null},
  {"name": {"en-us": "Skin sensitisation tests in guinea pigs", "pt-br": "Testes de sensibilização cutânea em cobaias"},
   "species": "guinea_pig", "oecd_ref": "TG 406", "r_type": "refinement", "extent": null}
]'::jsonb WHERE id IN (14, 15);

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Conventional acute oral toxicity tests (LD50 determination)", "pt-br": "Testes convencionais de toxicidade oral aguda (determinação da DL50)"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "reduction", "extent": null}
]'::jsonb WHERE id = 25;

COMMIT;
