// Fallback only: the real tree comes from the database (lib/vocabularies.js).
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

export function setEndpointCategories(slugs) {
  ENDPOINT_CATEGORIES.splice(0, ENDPOINT_CATEGORIES.length, ...slugs)
}

// Same aliases as the backend (normalize_endpoint_slug) for the old underscore codes.
const ENDPOINT_ALIASES = {
  'acute-toxicity': 'acute-systemic-toxicity',
  'ocular-irritation': 'eye-irritation',
  'skin-absorption': 'dermal-absorption',
  'bacterial-endotoxin': 'bacterial-endotoxins',
  toxicokinetics: 'toxicokinetic-properties',
}

/** Map an endpoint code to the one in the current option list (old codes included). */
export function canonicalEndpoint(code) {
  const raw = String(code ?? '').trim()
  if (!raw || ENDPOINT_CATEGORIES.includes(raw)) return raw
  const slug = raw.replaceAll('_', '-')
  const aliased = ENDPOINT_ALIASES[slug] ?? slug
  return ENDPOINT_CATEGORIES.includes(aliased) ? aliased : raw
}

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

export function canonicalApplication(code) {
  const slug = String(code ?? '')
    .trim()
    .replaceAll('_', '-')
  return slug
}

// Species rows come from the database (lib/vocabularies.js); these two markers
// are not organisms and always close the list.
export const SPECIES_MARKERS = ['in_vitro', 'other']
export const SPECIES = [...SPECIES_MARKERS]

export function setSpecies(slugs) {
  SPECIES.splice(
    0,
    SPECIES.length,
    ...slugs.filter((slug) => !SPECIES_MARKERS.includes(slug)),
    ...SPECIES_MARKERS,
  )
}
