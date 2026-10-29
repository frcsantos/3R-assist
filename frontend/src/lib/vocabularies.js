import { apiFetch } from './api'
import i18n from './i18n'
import { setApplications, setRoutes, setSpecies } from './parameterVocabulary'

const LOCALE_KEYS = { pt: 'pt-br', en: 'en-us' }

// enum_terms domain -> i18n path where t() looks the label up.
const ENUM_DOMAIN_PATHS = {
  animal_use: ['s3', 'enums', 'animalUse'],
  test_system: ['s3', 'enums', 'testSystem'],
  review_status: ['s3', 'enums', 'reviewStatus'],
  material_kind: ['s3', 'enums', 'materialKind'],
  material_origin: ['s3', 'enums', 'materialOrigin'],
  extent: ['s3', 'enums', 'extent'],
  taxon_group: ['s3', 'enums', 'taxonGroup'],
  validation_status: ['s3', 'validationStatus'],
  regulatory_status: ['s3', 'regulatoryStatus'],
  three_r_type: ['s3', 'threeR'],
  document_category: ['s4', 'documentCategory'],
}

function nest(path, value) {
  return path.reduceRight((inner, key) => ({ [key]: inner }), value)
}

function registerLabels(path, items, getCode) {
  for (const [lang, key] of Object.entries(LOCALE_KEYS)) {
    const labels = {}
    for (const item of items) {
      labels[getCode(item)] = item.name?.[key] ?? getCode(item)
    }
    i18n.addResourceBundle(lang, 'translation', nest(path, labels), true, true)
  }
}

/**
 * Load the application categories from the database (GET /vocabularies/applications),
 * replace the fallback list in parameterVocabulary and register the labels so that
 * t('s2.enums.application.<slug>') resolves. Returns true when the list was loaded.
 */
export async function loadApplications() {
  try {
    const data = await apiFetch('/vocabularies/applications')
    const items = data?.items ?? []
    if (!items.length) return false

    setApplications(items.map((item) => item.slug))
    registerLabels(['s2', 'enums', 'application'], items, (item) => item.slug)
    return true
  } catch {
    // Keep the fallback list; the form still works with the default value.
    return false
  }
}

/** Same for the routes table (GET /vocabularies/routes) -> t('s2.enums.route.<slug>'). */
export async function loadRoutes() {
  try {
    const data = await apiFetch('/vocabularies/routes')
    const items = data?.items ?? []
    if (!items.length) return false

    setRoutes(items.map((item) => item.slug))
    registerLabels(['s2', 'enums', 'route'], items, (item) => item.slug)
    return true
  } catch {
    return false
  }
}

/** Same for the species table (GET /vocabularies/species) -> t('s2.enums.species.<slug>'). */
export async function loadSpecies() {
  try {
    const data = await apiFetch('/vocabularies/species')
    const items = data?.items ?? []
    if (!items.length) return false

    setSpecies(items.map((item) => item.slug))
    registerLabels(['s2', 'enums', 'species'], items, (item) => item.slug)
    return true
  } catch {
    return false
  }
}

/**
 * Load the labels of the coded columns (GET /vocabularies/enums) and register
 * them under the i18n paths listed in ENUM_DOMAIN_PATHS.
 */
export async function loadEnumTerms() {
  try {
    const data = await apiFetch('/vocabularies/enums')
    const domains = data?.domains ?? {}
    for (const [domain, items] of Object.entries(domains)) {
      const path = ENUM_DOMAIN_PATHS[domain]
      if (path) registerLabels(path, items, (item) => item.code)
    }
    return Object.keys(domains).length > 0
  } catch {
    return false
  }
}

export function loadVocabularies() {
  return Promise.all([
    loadApplications(),
    loadRoutes(),
    loadSpecies(),
    loadEnumTerms(),
  ]).then(
    (results) => results.some(Boolean),
  )
}
