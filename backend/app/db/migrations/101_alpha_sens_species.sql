-- Migration 101: TG 442D states that the alpha-Sens cell line is an immortalised
-- adherent cell line derived from human keratinocytes (available from the JCRB
-- Cell Bank); the note of the reporter cell line row is updated.
BEGIN;
UPDATE method_materials
SET notes = 'TG 442D text: KeratinoSens, LuSens and alpha-Sens use immortalised adherent cell lines derived from human keratinocytes'
WHERE method_id = 11 AND kind = 'cell_line';
COMMIT;
