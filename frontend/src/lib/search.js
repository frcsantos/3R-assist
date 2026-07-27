import { apiFetch } from './api'
import { serializeParams } from './protocol'

export async function searchAlternatives({ params, filters, lang }) {
  return apiFetch('/search', {
    method: 'POST',
    body: JSON.stringify({ params, filters, lang }),
  })
}

export async function searchAllExperiments(experimentStates, lang) {
  return Promise.all(
    experimentStates.map(async (experiment) => {
      const params = serializeParams(experiment.params)
      const result = await searchAlternatives({ params, lang })
      return {
        params,
        studyType: experiment.studyType,
        notes: experiment.notes,
        recommendations: result.results ?? [],
        filter_relaxation: result.filter_relaxation ?? null,
      }
    }),
  )
}

export function scorePercent(score) {
  if (typeof score !== 'number' || Number.isNaN(score)) return 0
  return Math.round(score * 100)
}

export function isLowConfidenceScore(score) {
  return score <= 0.65
}

export function localeKey(lang) {
  const normalized = String(lang ?? 'en').toLowerCase().replace('_', '-')
  if (normalized === 'pt' || normalized.startsWith('pt-')) return 'pt-br'
  return 'en-us'
}

export function pickLocalized(value, lang) {
  if (value == null) return ''
  if (typeof value === 'string') return value
  if (typeof value !== 'object') return String(value)
  const key = localeKey(lang)
  return value[key] || value['en-us'] || value['pt-br'] || ''
}

export function methodDisplayName(method, lang) {
  if (!method) return ''
  return pickLocalized(method.name, lang)
}

export function methodDescription(method, lang) {
  if (!method) return ''
  return pickLocalized(method.description, lang)
}

export function formatOecdReference(ref) {
  if (!ref?.trim()) return null
  const trimmed = ref.trim()
  if (/^oecd/i.test(trimmed)) return trimmed
  return `OECD ${trimmed}`
}

const RATIONALE_FIELDS = {
  replacement: 'replacement_rationale',
  reduction: 'reduction_rationale',
  refinement: 'refinement_rationale',
}

function nonemptyRationale(value) {
  return typeof value === 'string' && value.trim() !== ''
}

/** 3R classes present on a method (non-null/non-empty rationale columns). */
export function methodThreeRClasses(method) {
  if (!method) return []
  if (method.category_3r?.length) {
    return ['replacement', 'reduction', 'refinement'].filter((key) =>
      method.category_3r.includes(key),
    )
  }
  return ['replacement', 'reduction', 'refinement'].filter((key) =>
    nonemptyRationale(method[RATIONALE_FIELDS[key]]),
  )
}

export function methodThreeRBadges(method, t) {
  return methodThreeRClasses(method).map((type) => ({
    type,
    label: t(`s3.threeR.${type}`),
    rationale: method?.[RATIONALE_FIELDS[type]] ?? null,
  }))
}

export function primaryThreeR(methodOrCategory) {
  const values = Array.isArray(methodOrCategory)
    ? methodOrCategory
    : methodThreeRClasses(methodOrCategory)
  for (const preferred of ['replacement', 'reduction', 'refinement']) {
    if (values.includes(preferred)) return preferred
  }
  return values[0] ?? 'replacement'
}

export function primaryRegulatoryContext(contexts = []) {
  if (!contexts.length) return null
  const priority = ['brazil', 'oecd', 'eu', 'us']
  for (const jurisdiction of priority) {
    const match = contexts.find((context) => context.jurisdiction === jurisdiction)
    if (match) return match
  }
  return contexts[0]
}

export function formatJurisdictionBadges(contexts = [], t) {
  const jurisdictions = [...new Set(contexts.map((context) => context.jurisdiction))]
  return jurisdictions.map((value) => t(`s3.jurisdiction.${value}`)).join(' · ')
}

export function regulatoryUrlFromContexts(contexts = []) {
  const primary = primaryRegulatoryContext(contexts)
  return primary?.regulatory_url ?? null
}

export function regulatoryCitationFromContexts(contexts = []) {
  const primary = primaryRegulatoryContext(contexts)
  const citation = primary?.regulatory_citation?.trim()
  return citation || null
}

export function formatMatchedParams(matchedParams, t) {
  const labels = {
    endpoint_category: t('s2.fields.endpointCategory'),
    route: t('s2.fields.route'),
    study_domain: t('s2.fields.studyDomain'),
  }
  return (matchedParams ?? []).map((key) => labels[key] ?? key)
}
