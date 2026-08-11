import {
  STUDY_DOMAINS,
  ENDPOINT_CATEGORIES,
  ROUTES,
  SPECIES,
} from './parameterVocabulary'

export const ANIMAL_COUNT_FIELDS = [
  { key: 'female', labelKey: 's2.fields.animalCounts.female' },
  { key: 'male', labelKey: 's2.fields.animalCounts.male' },
  { key: 'total', labelKey: 's2.fields.animalCounts.total' },
  { key: 'per_group', labelKey: 's2.fields.animalCounts.perGroup' },
]

export const ENDPOINT_FIELD = {
  key: 'endpoint_category',
  labelKey: 's2.fields.endpointCategory',
  type: 'select',
  options: ENDPOINT_CATEGORIES,
  enumPrefix: 'endpointCategory',
  required: true,
  allowEmpty: true,
}

export const MATCHING_FIELDS = [
  {
    key: 'route',
    labelKey: 's2.fields.route',
    type: 'routes',
    options: ROUTES,
    enumPrefix: 'route',
    hintKey: 's2.hints.route',
    evidenceKey: 'route',
    confidenceKey: 'route',
  },
  {
    key: 'study_domain',
    labelKey: 's2.fields.studyDomain',
    type: 'select',
    options: STUDY_DOMAINS,
    enumPrefix: 'studyDomain',
    required: true,
    evidenceKey: 'study_domain',
    confidenceKey: 'study_domain',
  },
  {
    key: 'procedure_text',
    labelKey: 's2.fields.procedureText',
    type: 'textarea',
    hintKey: 's2.hints.procedureText',
    evidenceKey: 'procedure_text',
    confidenceKey: 'procedure_text',
  },
]

export const DISPLAY_FIELDS = [
  {
    key: 'species',
    labelKey: 's2.fields.species',
    type: 'select',
    options: SPECIES,
    enumPrefix: 'species',
    allowEmpty: true,
    evidenceKey: 'species',
    confidenceKey: 'species',
  },
]

const EMPTY_ANIMAL_COUNTS = {
  female: '',
  male: '',
  total: '',
  per_group: '',
}

function normalizeRoutes(route) {
  if (Array.isArray(route)) {
    return route.filter((item) => ROUTES.includes(item))
  }
  if (typeof route === 'string' && route.trim()) {
    return route
      .split(',')
      .map((part) => part.trim())
      .filter((item) => ROUTES.includes(item))
  }
  return []
}

function parseCount(value) {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function normalizeAnimalCounts(counts, fallbackTotal) {
  const source = counts ?? {}
  return {
    female: source.female ?? '',
    male: source.male ?? '',
    total: source.total ?? fallbackTotal ?? '',
    per_group: source.per_group ?? '',
  }
}

function serializeAnimalCounts(formCounts) {
  const counts = {
    female: parseCount(formCounts?.female),
    male: parseCount(formCounts?.male),
    total: parseCount(formCounts?.total),
    per_group: parseCount(formCounts?.per_group),
  }
  const hasValue = Object.values(counts).some((value) => value !== null)
  return hasValue ? counts : null
}

export function primaryAnimalCount(counts) {
  if (!counts) return null
  if (counts.total != null) return counts.total
  if (counts.male != null && counts.female != null) {
    return counts.male + counts.female
  }
  return counts.male ?? counts.female ?? counts.per_group ?? null
}

export function normalizeParamsFromExperiment(experiment) {
  const raw = experiment?.raw ?? {}
  const params = experiment?.params ?? {}

  return normalizeParams({
    endpoint_category: experiment?.endpoint_category ?? params.endpoint_category,
    route: raw.route ?? params.route,
    study_domain: raw.study_domain ?? params.study_domain,
    procedure_text: raw.procedure_text ?? params.procedure_text,
    species: raw.species ?? params.species,
    animal_counts: raw.animal_counts,
    n_animals: params.n_animals,
  })
}

export function normalizeParams(params) {
  return {
    endpoint_category: params?.endpoint_category ?? '',
    route: normalizeRoutes(params?.route),
    study_domain: params?.study_domain ?? 'general',
    procedure_text: params?.procedure_text ?? '',
    species: params?.species ?? '',
    animal_counts: normalizeAnimalCounts(
      params?.animal_counts,
      params?.n_animals ?? '',
    ),
  }
}

export function serializeParams(form) {
  const animal_counts = serializeAnimalCounts(form.animal_counts)
  const routes = normalizeRoutes(form.route)

  return {
    endpoint_category: form.endpoint_category || null,
    route: routes.length ? routes : null,
    study_domain: form.study_domain || 'general',
    procedure_text: form.procedure_text?.trim() || null,
    species: form.species || null,
    animal_counts,
    n_animals: primaryAnimalCount(animal_counts),
  }
}

export function emptyParameterKeys(params) {
  const keys = []
  if (!params?.study_domain?.trim()) keys.push('study_domain')
  return keys
}

export function extractEvidence(raw = {}) {
  return {
    route: raw.route_evidence ?? null,
    study_domain: raw.study_domain_evidence ?? null,
    procedure_text: raw.procedure_text_evidence ?? null,
    species: raw.species_evidence ?? null,
    animal_counts: raw.animal_counts_evidence ?? null,
  }
}

export function extractFieldConfidence(raw = {}) {
  return {
    route: raw.route_confidence ?? null,
    study_domain: raw.study_domain_confidence ?? null,
    procedure_text: raw.procedure_text_confidence ?? null,
    species: raw.species_confidence ?? null,
    animal_counts: raw.animal_counts_confidence ?? null,
  }
}
