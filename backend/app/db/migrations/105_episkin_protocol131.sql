-- =============================================================================
-- Migration 105: EpiSkin SIT (DB-ALM protocol 131) for TG 439 (method 1).
--  - EpiSkin-SM: human-derived epidermal keratinocytes (healthy volunteer
--    donors) on a dermal substitute of collagen type I coated with collagen
--    type IV; maintenance and assay media come with the kit and their
--    composition is not given; the protocol states that all biological
--    components of the epidermis and of the kit medium were tested for viruses,
--    bacteria and mycoplasma. No serum is mentioned; the species of the
--    collagen is not stated.
--  - Regulatory level: EpiSkin SIT is the validated reference method of TG 439,
--    endorsed by ESAC as a stand-alone replacement of the Draize skin irritation
--    test (EC Method B.46, 2009) - consistent with "total" for TG 439.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET notes = 'TG 439 text; SkinEthic RHE (DB-ALM 135): normal human keratinocytes on a polycarbonate filter, chemically defined growth medium, no serum mentioned; EpiSkin-SM (DB-ALM 131): human keratinocytes from healthy volunteer donors, kit media composition not given; epiCS (TSAR): model description only'
WHERE method_id = 1 AND kind = 'reconstructed_tissue';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (1, 'matrix',
        '{"en-us": "Dermal substitute of the EpiSkin model: collagen type I matrix coated with collagen type IV", "pt-br": "Substituto dérmico do modelo EpiSkin: matriz de colágeno tipo I revestida com colágeno tipo IV"}'::jsonb,
        NULL, NULL, NULL,
        'DB-ALM protocol 131 (EpiSkin-SM); species and origin of the collagen are not stated');

COMMIT;
