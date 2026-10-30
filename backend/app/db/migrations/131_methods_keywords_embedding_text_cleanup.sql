-- Migration 131: standardise methods.text_for_embedding and clean up methods.keywords.
--
-- text_for_embedding now follows one pattern for every method, built from curated fields:
--   "<source> <code>: <name>. <description>"   (English, ASCII only; <= ~70 words)
--   e.g. "OECD TG 212: Fish, Short-term Toxicity Test on Embryo and Sac-Fry Stages. ..."
-- The old strings mixed slugs, "Test No.", "OECD-GD129", dashes and non-ASCII symbols.
-- embedding_json is reset to NULL so embed_methods.py regenerates it from the new text
-- (it was NULL for every method when this was written; the reset keeps the invariant that
-- text_for_embedding matches the string that produced embedding_json).
--
-- keywords fixes: missing accents (tg495), title-case terms (rabies RT-PCR), and harmonised
-- PT terms across methods (toxicidade oral aguda, toxicidade no desenvolvimento,
-- desregulação endócrina, depuração intrínseca; skin sensitisation spelling in tg442b).

BEGIN;

-- text_for_embedding -----------------------------------------------------------
UPDATE methods SET text_for_embedding = 'European Pharmacopoeia: Test for bacterial endotoxins using recombinant factor C. An in vitro method using recombinant factor C (rFC) and fluorimetric detection to detect or quantify bacterial endotoxins without horseshoe crab-derived lysate.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'european-pharmacopoeia-bacterial-endotoxins-test-recombinant-reagents';

UPDATE methods SET text_for_embedding = 'Brazilian Pharmacopoeia: Monocyte-activation test. An in vitro method for the detection of bacterial endotoxins and non-endotoxin pyrogens (NEPs) in parenteral products, using human monocytes or monocytic cell lines to measure the release of pro-inflammatory cytokines.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'farmacopeia-MG5.5.2.7.1-00-teste-de-ativacao-de-monocitos-mat';

UPDATE methods SET text_for_embedding = 'Brazilian Pharmacopoeia: Bacterial endotoxins. In vitro test using Limulus polyphemus or Tachypleus tridentatus amoebocyte lysate (LAL) to detect or quantify gram-negative bacterial endotoxins, including gel-clot, turbidimetric, and chromogenic methods.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'farmacopeia-MG5.5.2.7.3-02-teste-de-endotoxinas-bacterianas-lal';

UPDATE methods SET text_for_embedding = 'OECD GD 129: Basal Cytotoxicity for Acute Toxicity Starting Dose Estimation. In vitro basal cytotoxicity assay based on neutral red uptake (NRU), using BALB/c 3T3 cells or normal human keratinocytes (NHK). The IC50 obtained is used to estimate an LD50 and to support the selection of the starting dose in in vivo acute oral toxicity tests, with the potential to reduce the number of animals used.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-gd129-cytotoxicity-starting-dose';

UPDATE methods SET text_for_embedding = 'OECD TG 212: Fish, Short-term Toxicity Test on Embryo and Sac-Fry Stages. This test exposes fish life stages from newly fertilized egg to the end of the sac-fry stage to five concentrations of a test substance to assess lethal and sub-lethal effects.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg212-fish-embryo-sac-fry-toxicity';

UPDATE methods SET text_for_embedding = 'OECD TG 236: Fish Embryo Acute Toxicity (FET) Test. An acute toxicity test using zebrafish embryos (Danio rerio) exposed to chemicals for 96 hours to determine lethality based on apical observations.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg236-fish-embryo-acute-toxicity-test';

UPDATE methods SET text_for_embedding = 'OECD TG 319A: Determination of in vitro intrinsic clearance using cryopreserved rainbow trout hepatocytes (RT-HEP). This Test Guideline describes the use of cryopreserved rainbow trout (Oncorhynchus mykiss) hepatocytes (RT-HEP) as a metabolising system to determine the intrinsic clearance (CL, IN VITRO, INT) of a test chemical using a substrate depletion approach.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg319a-rt-hep-clearance';

UPDATE methods SET text_for_embedding = 'OECD TG 319B: Determination of in vitro intrinsic clearance using rainbow trout liver S9 sub-cellular fraction (RT-S9). The test guideline describes the use of rainbow trout liver S9 sub-cellular fraction as a metabolising system to determine the in vitro intrinsic clearance of a test chemical using a substrate depletion approach.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg319b-rt-s9-intrinsic-clearance';

UPDATE methods SET text_for_embedding = 'OECD TG 420: Acute Oral Toxicity - Fixed Dose Procedure. The Fixed Dose Procedure is a method for the assessment of acute oral toxicity in rats, using a stepwise approach to identify doses that produce signs of toxicity without requiring the use of lethal doses as a primary endpoint.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg420-fixed-dose-procedure';

UPDATE methods SET text_for_embedding = 'OECD TG 421: Reproduction/Developmental Toxicity Screening Test. A screening test describing the effects of a test chemical on male and female reproductive performance in rats, including endocrine disruptor endpoints such as anogenital distance, nipple retention, and thyroid examination.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg421-reproduction-developmental-toxicity-screening-test';

UPDATE methods SET text_for_embedding = 'OECD TG 422: Combined Repeated Dose Toxicity Study with the Reproduction/Developmental Toxicity Screening Test. A screening test guideline designed to assess the effects of a test chemical on male and female reproductive performance, developmental toxicity, and general repeated dose toxicity in rats, including endocrine disruptor endpoints.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg422-combined-repeated-dose-reproduction-developmental-toxicity-screening';

UPDATE methods SET text_for_embedding = 'OECD TG 423: Acute Oral Toxicity - Acute Toxic Class Method. A stepwise procedure with the use of 3 animals of a single sex per step, designed to rank substances for classification purposes and hazard assessment using fixed doses.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg423-acute-oral-toxicity-acute-toxic-class-method';

UPDATE methods SET text_for_embedding = 'OECD TG 425: Acute Oral Toxicity: Up-and-Down Procedure. An acute oral toxicity test method using an up-and-down procedure in rodents to estimate the LD50 and classify substances according to the GHS.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg425-acute-oral-toxicity-up-and-down-procedure';

UPDATE methods SET text_for_embedding = 'OECD TG 428: Skin Absorption: In Vitro Method. An in vitro method using diffusion cells with skin samples (human or animal, viable or non-viable) to measure the percutaneous absorption of test substances applied to the skin surface.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg428-skin-absorption-in-vitro';

UPDATE methods SET text_for_embedding = 'OECD TG 429: Skin Sensitisation: Local Lymph Node Assay. The Local Lymph Node Assay (LLNA) is a method for identifying skin sensitizers by measuring the proliferation of lymphocytes in the auricular lymph nodes draining the site of chemical application in mice.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg429-local-lymph-node-assay';

UPDATE methods SET text_for_embedding = 'OECD TG 430: In Vitro Skin Corrosion: Transcutaneous Electrical Resistance Test Method (TER). A test method that utilizes rat skin discs to identify corrosives by their ability to produce a loss of normal stratum corneum integrity and barrier function as measured by transcutaneous electrical resistance.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg430-ter-corrosion';

UPDATE methods SET text_for_embedding = 'OECD TG 431: In vitro skin corrosion: reconstructed human epidermis (RHE) test method. In vitro method that uses a three-dimensional reconstructed human epidermis with a functional stratum corneum to identify corrosive and non-corrosive substances and mixtures based on the reduction in cell viability after defined exposure periods.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg431-in-vitro-skin-corrosion';

UPDATE methods SET text_for_embedding = 'OECD TG 432: In Vitro 3T3 NRU Phototoxicity Test. A method to evaluate phototoxicity by comparing the relative reduction in viability of Balb/c 3T3 cells (murine fibroblast cell line) exposed to chemicals in the presence versus absence of light using the Neutral Red uptake assay.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg432-3t3-nru-phototoxicity';

UPDATE methods SET text_for_embedding = 'OECD TG 435: In Vitro Membrane Barrier Test Method for Skin Corrosion. An in vitro membrane barrier test method that uses an artificial membrane designed to respond to corrosive chemicals in a manner similar to skin to identify corrosive chemicals.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg435-membrane-barrier-test';

UPDATE methods SET text_for_embedding = 'OECD TG 437: Bovine Corneal Opacity and Permeability Test Method for Identifying i) Chemicals Inducing Serious Eye Damage and ii) Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage. An ex vivo test method that uses isolated bovine corneas from cattle slaughtered for commercial purposes to identify chemicals inducing serious eye damage or chemicals not requiring classification for eye irritation/damage.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg437-bcop';

UPDATE methods SET text_for_embedding = 'OECD TG 438: Isolated Chicken Eye Test Method. An ex vivo test method using enucleated chicken eyes from slaughterhouses to identify chemicals inducing serious eye damage or those not requiring classification for eye irritation/damage based on corneal opacity, fluorescein retention, swelling, and morphological damage.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg438-isolated-chicken-eye';

UPDATE methods SET text_for_embedding = 'OECD TG 439: In Vitro Skin Irritation: Reconstructed Human Epidermis Test Method. An in vitro procedure using reconstructed human epidermis (RhE) to identify irritant chemicals (substances and mixtures) by measuring cell viability via MTT reduction, mimicking the physiological properties of human skin.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg439-reconstructed-human-epidermis-skin-irritation';

UPDATE methods SET text_for_embedding = 'OECD TG 442A: LLNA: DA - Non-Radioactive Local Lymph Node Assay (ATP). The Local Lymph Node Assay: DA (LLNA: DA) is a non-radioactive modification to the LLNA method for identifying potential skin sensitizing test substances by measuring lymphocyte proliferation in auricular lymph nodes via ATP content bioluminescence.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg442a-llna-da';

UPDATE methods SET text_for_embedding = 'OECD TG 442B: Skin Sensitization: Local Lymph Node Assay: BrdU-ELISA or -FCM. A non-radioactive modification to the LLNA method for identifying potential skin sensitizing test chemicals by measuring the proliferation of lymphocytes in auricular lymph nodes using BrdU content, either by ELISA or Flow Cytometry.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg442b-llna-brdu-elisa-fcm';

UPDATE methods SET text_for_embedding = 'OECD TG 442C: In Chemico Skin Sensitisation. This Test Guideline addresses the molecular initiating event of skin sensitisation, namely protein reactivity, by quantifying the reactivity of test chemicals towards model synthetic peptides or amino acid derivatives containing either lysine or cysteine. It includes three methods: DPRA, ADRA, and kDPRA.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg442c-in-chemico-skin-sensitisation';

UPDATE methods SET text_for_embedding = 'OECD TG 442D: In Vitro Skin Sensitisation: Key Event on Keratinocyte Activation. A Key Event based Test Guideline addressing the human health hazard endpoint skin sensitisation, focusing on keratinocyte activation. It includes five in vitro methods: KeratinoSens, LuSens, EpiSensA, Epi2SensA, and alpha-Sens.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg442d-in-vitro-skin-sensitisation';

UPDATE methods SET text_for_embedding = 'OECD TG 442E: In Vitro Skin Sensitisation: Key Event on Dendritic Cell Activation. In vitro test guideline addressing the activation of dendritic cells within the skin sensitisation Adverse Outcome Pathway (AOP). Methods include h-CLAT, U-SENS, IL-8 Luc assay, and GARDskin, used for discriminating between skin sensitisers and non-sensitisers.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg442e-in-vitro-skin-sensitisation';

UPDATE methods SET text_for_embedding = 'OECD TG 455: Performance-Based Test Guideline for Stably Transfected Transactivation In Vitro Assays to Detect Estrogen Receptor Agonists and Antagonists. Performance-based guideline for in vitro assays with stably transfected cell lines, used to identify substances with agonist or antagonist activity on estrogen receptors through reporter gene transactivation.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg455-stably-transfected-transactivation-in-vitro-assays';

UPDATE methods SET text_for_embedding = 'OECD TG 456: H295R Steroidogenesis Assay. An in vitro screen using the human H295R adreno-carcinoma cell line to assess chemical effects on the production of 17-beta-estradiol and testosterone by measuring enzyme activity in the steroidogenesis pathway.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg456-h295r-steroidogenesis-assay';

UPDATE methods SET text_for_embedding = 'OECD TG 458: Stably Transfected Human Androgen Receptor Transcriptional Activation Assay. In vitro assay using Androgen Receptor TransActivation (ARTA) in stably transfected cell lines (AR-EcoScreen, AR-CALUX, 22Rv1/MMTV_GR-KO) to detect androgenic agonist and antagonist activity of chemicals.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg458-androgen-receptor-transactivational-assay';

UPDATE methods SET text_for_embedding = 'OECD TG 460: Fluorescein Leakage Test Method for Identifying Ocular Corrosives and Severe Irritants. An in vitro assay using a confluent monolayer of Madin-Darby Canine Kidney (MDCK) cells as a barrier to identify water-soluble ocular corrosives and severe irritants (UN GHS Category 1) by measuring increased fluorescein permeability resulting from impaired cell junctions.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg460-fluorescein-leakage';

UPDATE methods SET text_for_embedding = 'OECD TG 471: Bacterial Reverse Mutation Test. A test using amino-acid requiring strains of Salmonella typhimurium and Escherichia coli to detect point mutations by base substitutions or frameshifts, involving exposure of bacterial cells to a test substance with and without exogenous metabolic activation.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg471-bacterial-reverse-mutation-test';

UPDATE methods SET text_for_embedding = 'OECD TG 473: In Vitro Mammalian Chromosomal Aberration Test. The purpose of the in vitro chromosome aberration test is to identify agents that cause structural chromosome aberrations in cultured mammalian somatic cells.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg473-in-vitro-mammalian-chromosomal-aberration-test';

UPDATE methods SET text_for_embedding = 'OECD TG 476: In Vitro Mammalian Cell Gene Mutation Tests using the Hprt and xprt genes. The in vitro mammalian cell gene mutation test can be used to detect gene mutations induced by chemical substances measuring mutation at hypoxanthine-guanine phosphoribosyl transferase (HPRT) and xanthine-guanine phosphoribosyl transferase (XPRT) loci.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg476-in-vitro-mammalian-cell-gene-mutation-tests';

UPDATE methods SET text_for_embedding = 'OECD TG 487: In Vitro Mammalian Cell Micronucleus Test. The in vitro micronucleus test is a genotoxicity test for the detection of micronuclei in the cytoplasm of interphase cells, originating from acentric chromosome fragments or whole chromosomes that are unable to migrate to the poles during anaphase.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg487-in-vitro-mammalian-cell-micronucleus-test';

UPDATE methods SET text_for_embedding = 'OECD TG 490: In Vitro Mammalian Cell Gene Mutation Tests Using the Thymidine Kinase Gene. The in vitro mammalian cell gene mutation test using the thymidine kinase (tk) gene involves two distinct assays (MLA using L5178Y tk+/-3.7.2C cells and the TK6 assay using TK6 tk+/- cells) to detect gene mutations and chromosomal events induced by chemical substances in cells exposed with and without metabolic activation.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg490-in-vitro-mammalian-cell-gene-mutation-tests';

UPDATE methods SET text_for_embedding = 'OECD TG 491: Short Time Exposure In Vitro Test Method for Identifying i) Chemicals Inducing Serious Eye Damage and ii) Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage. A cytotoxicity-based in vitro assay using Statens Seruminstitut Rabbit Cornea (SIRC) cells to identify chemicals inducing serious eye damage or those not requiring classification, based on relative cell viability measured by the MTT assay after a five-minute exposure.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg491-short-time-exposure-in-vitro';

UPDATE methods SET text_for_embedding = 'OECD TG 492: Reconstructed human Cornea-like Epithelium (RhCE) test method for identifying chemicals not requiring classification and labelling for eye irritation or serious eye damage. An in vitro procedure using reconstructed human cornea-like epithelium (RhCE) to identify chemicals that do not require classification and labelling for eye irritation or serious eye damage according to UN GHS, based on the MTT assay to evaluate tissue cytotoxicity.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg492-rhce-eye-irritation';

UPDATE methods SET text_for_embedding = 'OECD TG 492B: Reconstructed Human Cornea-like Epithelium (RhCE) Test Method for Eye Hazard Identification. An in vitro procedure using Reconstructed Human Cornea-like Epithelium (RhCE) to identify chemicals not requiring classification, requiring classification for eye irritation (Cat 2), or serious eye damage (Cat 1) according to UN GHS, based on the MTT cytotoxicity assay.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg492b-rhce-eye-hazard';

UPDATE methods SET text_for_embedding = 'OECD TG 493: Performance-Based Test Guideline for Human Recombinant Estrogen Receptor (hrER) In Vitro Assays to Detect Chemicals with ER Binding Affinity. A performance-based test guideline for in vitro assays using human recombinant estrogen receptor alpha (ERalpha) to measure the ability of test chemicals to compete with a radiolabeled ligand for binding to the receptor, thereby identifying potential ER binders.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg493-hrer-binding-assay';

UPDATE methods SET text_for_embedding = 'OECD TG 494: Vitrigel - Eye Irritancy Test Method. An in vitro test method using human corneal epithelium (hCE) models to identify chemicals not requiring classification and labelling for eye irritation or serious eye damage by measuring changes in Transepithelial Electrical Resistance (TEER) values.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg494-vitrigel-eye-irritancy-test';

UPDATE methods SET text_for_embedding = 'OECD TG 495: Ros (Reactive Oxygen Species) Assay for Photoreactivity. A test method to measure the phototoxicity of a chemical by detecting the generation of Reactive Oxygen Species (ROS) from irradiated chemicals under simulated sunlight.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg495-ros-assay-photoreactivity';

UPDATE methods SET text_for_embedding = 'OECD TG 496: In vitro Macromolecular Test Method for Identifying Chemicals Inducing Serious Eye Damage and Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage. A biochemical in vitro test method that uses a macromolecular reagent matrix mimicking the corneal structure. It identifies chemicals inducing serious eye damage and those not requiring classification by measuring protein denaturation and matrix turbidity via light scattering.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'oecd-tg496-in-vitro-macromolecular-test-method';

UPDATE methods SET text_for_embedding = 'WOAH Terrestrial Manual 2025: Direct fluorescent antibody (DFA) test. Laboratory diagnostic technique used to detect rabies virus antigens in brain tissue impressions or smears, using fluorescein-conjugated anti-rabies antibodies.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'rabies-direct-fluorescent-antibody-test';

UPDATE methods SET text_for_embedding = 'WOAH Terrestrial Manual 2025: Direct rapid immunohistochemistry test (dRIT). A diagnostic method for rabies using streptavidin-biotin peroxidase staining to detect lyssavirus antigens in touch impressions of CNS tissues. It is an alternative to the direct fluorescent antibody (DFA) test that does not require a fluorescence microscope.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'rabies-direct-rapid-immunohistochemistry-test';

UPDATE methods SET text_for_embedding = 'WOAH Terrestrial Manual 2025: Pan-lyssavirus reverse-transcription polymerase chain reaction (RT-PCR) assays. Laboratory technique for the detection and identification of lyssavirus RNA in suspect animal brain tissue samples using conventional or real-time reverse-transcription polymerase chain reaction (RT-PCR) assays. Can replace the mouse inoculation test (MIT) for animal rabies diagnosis.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'rabies-rt-pcr-diagnostic-assay';

UPDATE methods SET text_for_embedding = 'WOAH Terrestrial Manual 2025: Rabies tissue culture infection test (RTCIT). A diagnostic method for the detection and isolation of rabies virus in suspect animal brain tissue samples using neuroblastoma cell cultures (e.g., N2a), intended to replace the mouse inoculation test.', embedding_json = NULL, updated_at = NOW()
WHERE slug = 'rabies-virus-isolation-tissue-culture';

-- keywords ---------------------------------------------------------------------

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["fotorreatividade", "fototoxicidade", "espécies reativas de oxigênio", "ROS", "segurança química"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg495-ros-assay-photoreactivity';

UPDATE methods SET keywords = keywords || jsonb_build_object('en-us', '["rabies", "lyssavirus", "RT-PCR", "diagnosis", "molecular diagnostics", "virus detection"]'::jsonb, 'pt-br', '["raiva", "lyssavirus", "RT-PCR", "diagnóstico", "diagnóstico molecular", "detecção de vírus"]'::jsonb), updated_at = NOW()
WHERE slug = 'rabies-rt-pcr-diagnostic-assay';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["DL50", "toxicidade oral aguda", "procedimento up-and-down", "roedores"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg425-acute-oral-toxicity-up-and-down-procedure';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["toxicidade reprodutiva", "toxicidade no desenvolvimento", "rato", "desregulação endócrina"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg421-reproduction-developmental-toxicity-screening-test';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["toxicidade reprodutiva", "toxicidade no desenvolvimento", "toxicidade por doses repetidas", "desregulação endócrina", "rato"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg422-combined-repeated-dose-reproduction-developmental-toxicity-screening';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["receptor de estrogênio", "desregulação endócrina", "afinidade de ligação", "in vitro", "hrER"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg493-hrer-binding-assay';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["esteroidogênese", "desregulador endócrino", "H295R", "produção hormonal"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg456-h295r-steroidogenesis-assay';

UPDATE methods SET keywords = keywords || jsonb_build_object('pt-br', '["truta arco-íris", "fração S9", "depuração intrínseca", "metabolismo", "depleção de substrato"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg319b-rt-s9-intrinsic-clearance';

UPDATE methods SET keywords = keywords || jsonb_build_object('en-us', '["skin sensitisation", "LLNA", "BrdU", "ELISA", "flow cytometry", "lymph nodes"]'::jsonb), updated_at = NOW()
WHERE slug = 'oecd-tg442b-llna-brdu-elisa-fcm';

COMMIT;
