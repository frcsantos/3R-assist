-- =============================================================================
-- Migration 106: RhCE models (TG 492, TG 492B) and EpiSensA checked against the
-- DB-ALM protocols 164 (EpiOcular EIT), 190 (SkinEthic HCE EITL), 191 (SkinEthic
-- HCE EITS) and the EpiSensA SOP v2.6 (Kao).
--  - EpiOcular (MatTek): normal human foreskin-derived epidermal keratinocytes,
--    not transformed or transfected; "specialized medium" with no composition and
--    no mention of serum.
--  - SkinEthic HCE: transformed (immortalised) human corneal epithelial cell line
--    cultured at the air-liquid interface in a "chemically defined medium"; the
--    protocols mention no serum or other animal-derived component.
--  - EpiSensA SOP v2.6: LabCyte EPI-MODEL24 (J-TEC, kit 401124) from normal human
--    epidermal keratinocytes with ready-to-use assay medium supplied in the kit;
--    the SOP does not describe the medium composition (the manual says serum).
-- =============================================================================

BEGIN;

UPDATE method_materials
SET notes = 'TG 492 text; EpiOcular (DB-ALM 164): normal human foreskin-derived epidermal keratinocytes, not transformed, "specialized medium" without composition or serum mention; SkinEthic HCE (DB-ALM 190/191): transformed human corneal epithelial cell line in a chemically defined medium, no serum mentioned'
WHERE method_id = 9 AND kind = 'reconstructed_tissue';

UPDATE method_materials
SET notes = 'TG 492B text; same models as TG 492: EpiOcular (DB-ALM 164, normal human keratinocytes) and SkinEthic HCE (DB-ALM 190/191, transformed human corneal epithelial cell line, chemically defined medium)'
WHERE method_id = 39 AND kind = 'reconstructed_tissue';

UPDATE method_materials
SET notes = 'TG 442D text; EpiSensA SOP v2.6 (Kao): LabCyte EPI-MODEL24 (J-TEC kit 401124) reconstructed from normal human epidermal keratinocytes, ready-to-use assay medium in the kit (composition not given in the SOP); LabCyte manual: model made by culturing normal human epidermal cells'
WHERE id = 24;

COMMIT;
