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

// Fallback only: the real list comes from the database (lib/vocabularies.js).
export const DEFAULT_ROUTE = 'unspecified'
export const ROUTES = [DEFAULT_ROUTE]

export function setRoutes(slugs) {
  ROUTES.splice(0, ROUTES.length, ...slugs)
}

const ROUTE_ALIASES = {
  dermal: 'cutaneous',
}

export function canonicalRoute(code) {
  const slug = String(code ?? '')
    .trim()
    .replaceAll('_', '-')
  return ROUTE_ALIASES[slug] ?? slug
}

// Fallback only: the real list comes from the database (lib/vocabularies.js).
export const DEFAULT_APPLICATION = 'basic-research'
export const APPLICATIONS = [DEFAULT_APPLICATION]

export function setApplications(slugs) {
  APPLICATIONS.splice(0, APPLICATIONS.length, ...slugs)
}

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
