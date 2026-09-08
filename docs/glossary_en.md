**Endpoint:** In toxicology and pharmacology, this refers to the biological effect or measurable parameter that a study aims to evaluate—the response that the test captures, not the substance being tested or the method itself. This is the accepted terminology in regulatory ecotoxicology (OECD, ECHA, and ANVISA use the term in this sense).
Examples of endpoints: eye irritation, skin corrosion, skin sensitization (allergenicity), genotoxicity, acute toxicity, phototoxicity, pyrogenicity. Each answers a distinct regulatory question (e.g., “Does this substance corrode the skin?” → endpoint = skin corrosion).

**Method:** A discrete, validatable technique that produces measurable data for a single endpoint_category—e.g., TG 439 EpiSkin produces a cell viability value that classifies skin irritation. 

**Methodology:** An experimental design or broader strategy that answers a research question, potentially combining or sequencing multiple methods—e.g., an IATA (Integrated Approach to Testing and Assessment) that combines in silico + in vitro + in vivo confirmation, or a comprehensive behavioral study design.

**Route:** Describes how the test substance comes into contact with the biological system—not the type of biological system. In surrogate methods, it refers to which routes in the original protocol this method is compatible with to replace—use “null” when it is compatible with any route.

**Application:** The intended use or purpose of a study or method (e.g. basic research, regulatory use, education). Formerly called “study domain”.

**Animal use (`animal_use`):** How a catalogue method uses animals or animal-derived materials — a single controlled-vocabulary value on `methods`, used for curation, filtering, and result-card display. Values (canonical definitions in ADR-026):
- **None** — no animals and no animal-derived materials are used.
- **Animal-derived material** — products obtained from animals (sera, antibodies, enzymes, …) are used, without animals being killed for this method's tissue harvest.
- **Slaughterhouse byproduct** — tissues/organs from animals already slaughtered for food or other primary purposes (e.g. post-slaughter bovine corneas in EVEIT).
- **Animals killed for tissue** — animals are killed specifically to obtain tissue for the method.
- **Live animals** — living animals are used in the procedure.
- **Mixed or variable** — more than one of the above clearly applies, or use varies.

May be null during curation when the source document does not clearly support a classification; null means “unclassified”, never “None”.

**Animal counts (`animal_counts`):** Structured number of animals extracted from a submitted protocol: **Females**, **Males**, **Total**, **Per group**. Only subfields explicitly stated in the protocol text are populated; derived values are prohibited (ADR-017). Null when the protocol has no meaningful experimental animal cohort (e.g. slaughterhouse byproducts — see the EVEIT example in `parameter_model.md` §8). Displayed on S2; see `parameter_model.md` §4.