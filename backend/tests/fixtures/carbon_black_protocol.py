"""Ground-truth extraction expectations for the carbon black inhalation protocol."""

from tests.fixtures.ground_truth import ExpectedAnimalCounts, ExpectedEvidence, ExpectedExtraction

CARBON_BLACK_PROTOCOL = (
    "Material and methods. Animals and CB exposure study design: Male, pathogen-free "
    "Sprague–Dawley rats at 6 weeks of age were acclimated for a week before the "
    "commencement of inhalation exposure. During the acclimation and inhalation exposure, "
    "the rats were housed in polycarbonate cages and provided food and tap water ad libitum "
    "in a controlled humidity and temperature environment with a 12 hrs light/dark cycle. "
    "We divided 32 rats into two groups: control and exposure. Rats in the exposure group "
    "were exposed to CB in the nose-only inhalation chamber at 30 mg/m³ for 6 hrs/day for "
    "90 days. The control animals were exposed to filter air for 24 hrs/day. After exposure "
    "for 90 days, eight rats were selected randomly and sacrificed in each group, "
    "respectively. The rest eight rats in each group were recovered for 14 days after "
    "exposure in the chamber with HEPA-filters. Rats were anesthetized by pentobarbital "
    "sodium and sacrificed at the endpoint of treatment. Blood samples were collected from "
    "abdominal aorta. Organs were separated to further detect. The present protocol was "
    "approved by the Committee of the Ethics Animal Experiments of Hebei Medical University "
    "(IACUC-Hebmu-20160047) and carried out under the Hebei Medical University institutional "
    "guidelines for ethical animal use. Characterization of CB, aerosol generation, and "
    "conditions in the inhalation chamber: CB (≥99.8%) was purchased from the CB "
    "manufacturing factory (Jiaozuo Chemical Industry Limited Company, Henan, China) and "
    "its characteristics were the same as our previous studies. Briefly, Tecnai G220 "
    "transmission electron microscope (TEM, FEI, USA) and Sirion 200 scanning electron "
    "microscope (SEM, FEI, Holland) were used to evaluate the size and morphology of CB "
    "particles. Nitrogen adsorption capacity was calculated to evaluate the specific surface "
    "characteristics of CB by Brunauer–Emmett–Teller method. The size and zeta potential of "
    "CB particles were performed on DelsaTM Nanoparticle analysis instrument (Beckman coulter, "
    "CA, USA). CB was baked at 80°C for 12 hrs before exposure and packed in an aerosol "
    "generator column (Beijing Huironghe Technology Co., Ltd. Beijing, China). The aerosol "
    "generator system was employed to reliably disperse non-cohesive powders such as mineral "
    "dusts, medical compounds, pollen, and so forth in the size range <100 μm. In the present "
    "study, the CB powder was filled into the powder reservoir and uniformly compressed along "
    "a 20 cm filling height by a tamper. Then, the CB powder was transported onto a rotating "
    "brush at 13 L/min feed rate. The powder that came from the reservoir and had been loosened "
    "from the rotating brush was dispersed into practically all individual particles at 23 L/min "
    "speed in the dispersion head by dispersion air at 10 L/min flow rate. Dosing was performed "
    "using a precisely controlled feed rate of the feed piston (Figure 1). The concentration of "
    "CB aerosol in the exposed chamber was 22.50–42.50 mg/m³ by filter weighing method, and the "
    "average was 30.06±4.42 mg/m³. During exposure, each rat was placed in a polycarbonate holder "
    "and constrained with a sealed restraint inserted in the rear opening of the holder so that "
    "only the tip of the rat's nose projects out of an opening in the front of the holder. A "
    "prediction of the deposited alveolar fraction was generated using the MPPD model version "
    "3.04. The calculated deposition faction of SD rats was 0.1146, and the deposition in each "
    "rat was 16 mg by MPPD after CB exposure for 90 days. At the occupational exposure limit of "
    "3.5 mg/m³ CB per 8 hrs work shift (established by OSHA and NIOSH), the deposition in each "
    "worker was 80 mg by MPPD after CB exposure for 90 days. Lung function test: Eight rats in "
    "each group were executed the lung function tests using a ventilated bias flow whole body "
    "plethysmograph (AniRes2005, Beilanbo Ltd, China). The parameters of lung function included "
    "FEV1, FVC, FEV1/FVC (%), PEF, and MMF. The rats were placed in the animal chamber, and the "
    "plethysmography was then conducted based on the measurements of the selected parameter values "
    "for 5 mins. Detection of pulmonary deposition/clearance by SDS-PAGE: According to the "
    "previous literature with a small modified SDS-PAGE protocol was used to detect the deposition "
    "and retention of CB in rats. Six lungs of rats in each group were used to detect the CB "
    "contents. Thirty milligram lung tissue was homogenized in 700 μL normal saline and then "
    "processed for SDS-PAGE. The optical images of gels were acquired using a flatbed scanner "
    "(Tanon-5500, Tanon Science & Technology Co., Ltd. Shanghai, China) and the optical density "
    "(OD) of each band, which represented the CB contents, was quantified using Image-Pro Plus "
    "6.0 software (Media Cybernetics, Inc. Rockville, MD). Organ coefficient and histopathological "
    "examination: Organs, including testis, heart, lungs, kidneys, spleen, liver, and brain were "
    "separated and weighted at the endpoint of the experiment. The organ coefficient was calculated "
    "as: organ weight/body weight ×100%. Six rats in each group were used for histopathological "
    "examination. Animal noses were perfused with ~5 mL of formalin, trimmed, and immersion-fixed "
    "in 10% neutral buffered formalin. The lungs, spleen, and thymus were fixed for 24 hrs and "
    "embedded in paraffin. Following paraffin embedding, tissues were cut into 5 μm serial "
    "sections. H&E staining was used to observe changes. Lung sections were stained with Masson "
    "following the manufacturer's protocol (Sigma–Aldrich). Images were observed under a light "
    "microscope (Olympus, Japan). Scoring criteria included alveolar congestion, fibrin exudation, "
    "desquamation of epithelial cells, infiltration of neutrophils, and thickness of alveolar wall. "
    "For TEM image, three animals in each group were anesthetized and perfused with 20 mL of 37°C "
    "saline and 2.5% glutaraldehyde. Lung pieces were cut into 1 mm³ pieces and examined under "
    "H-7500 TEM (Hitachi, Japan). Apoptosis detection: Apoptosis was examined by TUNEL assay "
    "(Roche Ltd., Shanghai). Apoptotic indices (OD) were calculated. Apoptosis of thymocytes was "
    "detected using flow cytometry (Annexin V-FITC kit, BD). Cytokines analysis: IL-6, IL-8, "
    "IL-17, and TNF-α in serum and lung tissue were evaluated with rat ELISA kits (NeoBioscience, "
    "Shenzhen). For IHC, antigenic site retrievals were accomplished by microwave heat-mediated "
    "method. Images were observed under light microscope (Olympus). Peripheral blood cell counts "
    "and lymphocyte subsets: Peripheral blood cell counts were detected by Auto 5-diff hematology "
    "analyzer (Tecom Science Corporation, Nanchang). Peripheral lymphocytes were isolated using "
    "separation solution (Solarbio Life Sciences). CD4, CD3, and CD8 subsets were acquired using "
    "AccuriC6 flow cytometer (BD). Lymphocytes proliferation was detected via PHA stimulation and "
    "MTS assay. Statistical analysis: Performed using SPSS vs 21.0. Two-group t-test and one-way "
    "ANOVA followed by Dunnett's test were used. Non-parametric statistics were performed for "
    "pathological scores (Mann–Whitney U-test). Significance set at P<0.05."
)

EXPECTED_CARBON_BLACK_INHALATION = ExpectedExtraction(
    study_type_keywords=("subchronic", "inhalation"),
    endpoint_category=None,
    route=["inhalation"],
    application={"regulatory-use", "basic-research"},
    procedure_keywords=("90", "inhalation", "cb", "repeated", "subacute", "chronic", "lung"),
    species="rat",
    animal_counts=ExpectedAnimalCounts(total=32),
    regulatory=None,
    evidence=ExpectedEvidence(
        route="inhalation",
        species="sprague",
        animal_counts="32",
    ),
    notes=(
        "No endpoint_category match: subchronic inhalation toxicity not in §3.1 vocabulary. "
        "Route 'inhalation' has no methods in MVP database. Protocol also includes a "
        "14-day post-exposure recovery cohort not represented in any field."
    ),
)
