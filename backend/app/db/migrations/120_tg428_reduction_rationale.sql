-- =============================================================================
-- Migration 120: TG 428 (method 21, in vitro skin absorption) gets a reduction
-- rationale and the avoided in vivo procedure (TG 427). Provisional: pending
-- confirmation in docs/decisoes_curadoria.md (item 7, TG 428). Basis: the
-- regulation note ("excised skin - category = reduction, not replacement") and
-- the TG 427 comparator; the TG 428 text itself makes no 3R claim.
-- Only fills the columns while they are still NULL.
-- =============================================================================

BEGIN;

UPDATE methods
SET reduction_rationale = '{
  "en-us": "The method measures skin absorption on excised skin in a diffusion cell, which can reduce the use of live animals compared with the in vivo skin absorption study (TG 427). It is not a full replacement because the skin used is usually obtained from animals.",
  "pt-br": "O método mede a absorção cutânea em pele excisada, em célula de difusão, o que pode reduzir o uso de animais vivos em comparação com o estudo in vivo de absorção cutânea (TG 427). Não é uma substituição total porque a pele utilizada costuma ser obtida de animais."
}'::jsonb
WHERE id = 21 AND reduction_rationale IS NULL;

UPDATE methods
SET animal_procedures_avoided = '[
  {
    "name": {
      "en-us": "In vivo skin absorption study",
      "pt-br": "Estudo in vivo de absorção cutânea"
    },
    "note": {
      "en-us": "TG 427: the in vivo comparator, usually performed in the rat, which requires live animals and radiolabelled material",
      "pt-br": "TG 427: comparador in vivo, geralmente realizado em ratos, que exige animais vivos e material radiomarcado"
    },
    "extent": null,
    "r_type": "reduction",
    "species": "rat",
    "oecd_ref": "TG 427"
  }
]'::jsonb
WHERE id = 21 AND animal_procedures_avoided IS NULL;

COMMIT;
