-- =============================================================================
-- Migration 089: method_materials for the methods that had none, using only
-- what the test-guideline summaries (docs/oecd_files), the CONCEA resolutions
-- and the method descriptions state. Rows marked "confirm" in notes rely on
-- the usual protocol and need curator confirmation.
-- =============================================================================

BEGIN;

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
SELECT v.method_id, v.kind,
       jsonb_build_object('en-us', v.en, 'pt-br', v.pt),
       (SELECT s.id FROM species s WHERE s.slug = v.species),
       v.origin, v.animal_derived, v.notes
FROM (VALUES
  -- Skin / eye ---------------------------------------------------------------
  (5,  'synthetic_reagent', 'Artificial membrane barrier', 'Membrana artificial como barreira', NULL::text, 'synthetic', NULL::boolean, 'TG 435 summary; composition (protein matrix) to confirm'),
  (11, 'reconstructed_tissue', 'Reconstructed human epidermis models (EpiSensA, Epi2SensA)', 'Modelos de epiderme humana reconstruída (EpiSensA, Epi2SensA)', 'human', 'human', NULL, 'TG 442D summary'),
  (11, 'cell_line', 'ARE-Nrf2 luciferase reporter cell lines (KeratinoSens, LuSens, α-Sens)', 'Linhagens celulares repórter ARE-Nrf2 luciferase (KeratinoSens, LuSens, α-Sens)', NULL, NULL, NULL, 'TG 442D summary; species not stated'),
  (12, 'cell_line', 'Human cell Line Activation Test cells (h-CLAT)', 'Células do ensaio h-CLAT (human cell Line Activation Test)', 'human', 'human', NULL, 'TG 442E summary'),
  (12, 'cell_line', 'U937 cells (U-SENS)', 'Células U937 (U-SENS)', 'human', 'human', NULL, 'TG 442E summary (U937 cell line); species to confirm'),
  (21, 'tissue', 'Skin sample from human or animal sources, viable or non-viable, in a diffusion cell', 'Amostra de pele de origem humana ou animal, viável ou não, em célula de difusão', NULL, NULL, NULL, 'TG 428 summary'),
  (49, 'matrix', 'Macromolecular reagent (proteins, glycoproteins, carbohydrates, lipids) forming a corneal-like matrix', 'Reagente macromolecular (proteínas, glicoproteínas, carboidratos, lipídios) que forma matriz semelhante à córnea', NULL, NULL, NULL, 'TG 496 summary; origin of the components to confirm'),
  (47, 'reconstructed_tissue', 'Human corneal epithelium (hCE) models', 'Modelos de epitélio corneano humano (hCE)', 'human', 'human', NULL, 'TG 494 summary'),
  (50, 'synthetic_reagent', 'Cell-free chemical system: irradiated test chemical with ROS detection by spectrometry', 'Sistema químico acelular: substância irradiada com detecção de ROS por espectrometria', NULL, 'synthetic', FALSE, 'TG 495 summary'),
  -- Genotoxicity -------------------------------------------------------------
  (17, 'whole_organism', 'Salmonella typhimurium strains', 'Cepas de Salmonella typhimurium', 'salmonella_typhimurium', 'microbial', FALSE, 'TG 471 summary'),
  (17, 'whole_organism', 'Escherichia coli strains', 'Cepas de Escherichia coli', 'escherichia_coli', 'microbial', FALSE, 'TG 471 summary'),
  (17, 'metabolic_activation', 'Exogenous metabolic activation system (usually S9 from rat liver)', 'Sistema exógeno de ativação metabólica (normalmente S9 de fígado de rato)', 'rat', 'animal', TRUE, 'TG 471 summary mentions the system; rat liver S9 confirm'),
  (45, 'cell_line', 'Cultured mammalian somatic cells (cell lines, cell strains or primary cultures)', 'Células somáticas de mamífero em cultura (linhagens, cepas ou culturas primárias)', NULL, NULL, NULL, 'TG 473 summary'),
  (45, 'metabolic_activation', 'Exogenous metabolic activation system (usually S9 from rat liver)', 'Sistema exógeno de ativação metabólica (normalmente S9 de fígado de rato)', 'rat', 'animal', TRUE, 'TG 473 summary mentions metabolic activation; rat liver S9 confirm'),
  (18, 'cell_line', 'Mammalian cells (HPRT and XPRT gene mutation assays)', 'Células de mamífero (ensaios de mutação gênica HPRT e XPRT)', NULL, NULL, NULL, 'TG 476 summary'),
  (18, 'metabolic_activation', 'Exogenous metabolic activation system (usually S9 from rat liver)', 'Sistema exógeno de ativação metabólica (normalmente S9 de fígado de rato)', 'rat', 'animal', TRUE, 'TG 476 summary mentions metabolic activation; rat liver S9 confirm'),
  (19, 'cell_line', 'Cultured mammalian cells', 'Células de mamífero em cultura', NULL, NULL, NULL, 'TG 487 summary'),
  (46, 'cell_line', 'L5178Y tk+/- 3.7.2C mouse lymphoma cells (MLA)', 'Células de linfoma de camundongo L5178Y tk+/- 3.7.2C (MLA)', 'mouse', 'animal', NULL, 'TG 490 summary'),
  (46, 'cell_line', 'TK6 tk+/- cells', 'Células TK6 tk+/-', 'human', 'human', NULL, 'TG 490 summary; species to confirm'),
  (46, 'metabolic_activation', 'Exogenous metabolic activation system (usually S9 from rat liver)', 'Sistema exógeno de ativação metabólica (normalmente S9 de fígado de rato)', 'rat', 'animal', TRUE, 'TG 490 summary mentions metabolic activation; rat liver S9 confirm'),
  -- Endocrine ----------------------------------------------------------------
  (41, 'cell_line', '(h)ERα-HeLa-9903 cell line (human cervical tumor)', 'Linhagem (h)ERα-HeLa-9903 (tumor cervical humano)', 'human', 'human', NULL, 'TG 455 summary'),
  (41, 'cell_line', 'BG1Luc-4E2 cell line (human ovarian adenocarcinoma)', 'Linhagem BG1Luc-4E2 (adenocarcinoma ovariano humano)', 'human', 'human', NULL, 'TG 455 summary'),
  (42, 'recombinant_protein', 'Human recombinant estrogen receptor alpha (full length or ligand-binding domain)', 'Receptor de estrogênio alfa humano recombinante (comprimento total ou domínio de ligação)', 'human', 'recombinant', FALSE, 'TG 493 summary'),
  (43, 'cell_line', 'H295R human adrenocarcinoma cell line', 'Linhagem de adenocarcinoma adrenocortical humano H295R', 'human', 'human', NULL, 'TG 456 summary'),
  (44, 'cell_line', 'Stably transfected cell lines expressing the androgen receptor with a luciferase reporter', 'Linhagens celulares estavelmente transfectadas que expressam o receptor de andrógeno com gene repórter luciferase', NULL, NULL, NULL, 'TG 458 summary; species not stated'),
  -- In vivo ----------------------------------------------------------------------
  (24, 'whole_organism', 'Rat (other rodent species may be used; normally females)', 'Rato (outras espécies de roedores podem ser usadas; normalmente fêmeas)', 'rat', 'animal', TRUE, 'TG 423 text'),
  (25, 'whole_organism', 'Rodents (preferably female rats)', 'Roedores (preferencialmente ratas)', 'rat', 'animal', TRUE, 'TG 425 summary'),
  (36, 'whole_organism', 'Rat', 'Rato', 'rat', 'animal', TRUE, 'TG 421 text'),
  (37, 'whole_organism', 'Rat', 'Rato', 'rat', 'animal', TRUE, 'TG 422 text'),
  (51, 'embryo', 'Fertilised fish eggs, embryo and sac-fry stages', 'Ovos fertilizados, embriões e estágios de alevino de peixe', NULL, 'animal', TRUE, 'TG 212 summary; species not stated'),
  -- Pyrogens ------------------------------------------------------------------------
  (20, 'sample', 'Human whole blood or peripheral-blood monocytes from volunteer donors', 'Sangue total humano ou monócitos de sangue periférico de doadores voluntários', 'human', 'human', FALSE, 'CONCEA RN 45/2019, art. 3, single paragraph'),
  -- Rabies -------------------------------------------------------------------------------
  (30, 'tissue', 'Brain tissue impressions or smears from suspect animals', 'Impressões ou esfregaços de tecido cerebral de animais suspeitos', NULL, 'animal', TRUE, 'method description'),
  (33, 'tissue', 'Central nervous system tissue impressions from suspect animals', 'Impressões de tecido do sistema nervoso central de animais suspeitos', NULL, 'animal', TRUE, 'method description'),
  (34, 'tissue', 'Brain tissue samples from suspect animals', 'Amostras de tecido cerebral de animais suspeitos', NULL, 'animal', TRUE, 'method description'),
  (34, 'cell_line', 'Neuroblastoma cells (e.g. N2a)', 'Células de neuroblastoma (por exemplo N2a)', 'mouse', 'animal', NULL, 'method description; N2a species confirm'),
  (35, 'tissue', 'Suspect animal brain tissue samples (RNA detection)', 'Amostras de tecido cerebral de animais suspeitos (detecção de RNA)', NULL, 'animal', TRUE, 'method description')
) AS v(method_id, kind, en, pt, species, origin, animal_derived, notes);

COMMIT;
