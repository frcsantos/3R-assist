export const ENDPOINT_CATEGORIES = [
  'acute_toxicity',
  'skin_irritation',
  'skin_corrosion',
  'ocular_irritation',
  'skin_sensitisation',
  'phototoxicity',
  'genotoxicity',
  'pyrogenicity',
  'skin_absorption',
  'reproductive_toxicity',
  'endocrine_activity',
  'photoreactivity',
  'aquatic_toxicity',
  'toxicokinetics',
  'bacterial_endotoxin',
  'rabies_diagnosis',
]

export const ROUTES = [
  'cutaneous',
  'inhalation',
  'oral',
  'ocular',
  'intranasal',
  'intratracheal',
  'intravenous',
  'intra-arterial',
  'intramuscular',
  'subcutaneous',
  'intradermal',
  'intraperitoneal',
  'rectal',
  'vaginal',
  'topical-mucosal',
  'implantation',
  'multiple',
  'not-applicable',
  'unspecified',
  'other',
]

const ROUTE_ALIASES = {
  dermal: 'cutaneous',
}

export function canonicalRoute(code) {
  const slug = String(code ?? '')
    .trim()
    .replaceAll('_', '-')
  return ROUTE_ALIASES[slug] ?? slug
}

export const APPLICATIONS = [
  'basic-research',
  'translational-applied-research',
  'regulatory-use',
  'routine-production',
  'education-training',
  'environmental-protection',
  'species-preservation',
  'forensic-inquiry',
  'other',
]

const APPLICATION_ALIASES = {
  general: 'basic-research',
  pharma: 'regulatory-use',
  cosmetics: 'regulatory-use',
  'chemical-safety': 'regulatory-use',
  'chemical_safety': 'regulatory-use',
}

export function canonicalApplication(code) {
  const slug = String(code ?? '')
    .trim()
    .replaceAll('_', '-')
  return APPLICATION_ALIASES[slug] ?? slug
}

export const SPECIES = [
  'rat',
  'mouse',
  'rabbit',
  'guinea_pig',
  'chicken',
  'zebrafish',
  'in_vitro',
  'other',
]
