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

function tryParseLocalizedObject(value) {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  if (!trimmed.startsWith('{')) return null
  if (!trimmed.includes('en-us') && !trimmed.includes('pt-br')) return null
  try {
    const parsed = JSON.parse(trimmed)
    if (
      parsed &&
      typeof parsed === 'object' &&
      !Array.isArray(parsed) &&
      ('en-us' in parsed || 'pt-br' in parsed)
    ) {
      return parsed
    }
  } catch {
    /* plain string */
  }
  return null
}

export function pickLocalized(value, lang) {
  if (value == null) return ''
  if (typeof value === 'string') {
    const nested = tryParseLocalizedObject(value)
    return nested ? pickLocalized(nested, lang) : value
  }
  if (typeof value !== 'object') return String(value)
  const key = localeKey(lang)
  const picked = value[key] || value['en-us'] || value['pt-br'] || ''
  if (typeof picked === 'string') {
    const nested = tryParseLocalizedObject(picked)
    return nested ? pickLocalized(nested, lang) : picked
  }
  return pickLocalized(picked, lang)
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
  if (value == null) return false
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return false
    const nested = tryParseLocalizedObject(trimmed)
    if (nested) return nonemptyRationale(nested)
    return true
  }
  if (typeof value === 'object') {
    return Object.values(value).some(
      (part) => typeof part === 'string' && part.trim() !== '',
    )
  }
  return false
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

export function methodThreeRBadges(method, t, lang) {
  return methodThreeRClasses(method).map((type) => ({
    type,
    label: t(`s3.threeR.${type}`),
    rationale: pickLocalized(method?.[RATIONALE_FIELDS[type]], lang) || null,
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

export const JURISDICTION_LABELS = {
  brazil: { 'en-us': 'Brazil', 'pt-br': 'Brasil' },
  eu: { 'en-us': 'EU', 'pt-br': 'UE' },
  us: { 'en-us': 'US', 'pt-br': 'EUA' },
  oecd: { 'en-us': 'OECD', 'pt-br': 'OCDE' },
}

export function jurisdictionMatches(jurisdiction, code) {
  const expected = JURISDICTION_LABELS[code]
  if (!expected || jurisdiction == null) return false
  if (typeof jurisdiction === 'string') {
    const key = jurisdiction.toLowerCase()
    if (key === code) return true
    const mapped = JURISDICTION_LABELS[key]
    if (!mapped) return false
    return (
      mapped['en-us'] === expected['en-us'] ||
      mapped['pt-br'] === expected['pt-br']
    )
  }
  return (
    jurisdiction['en-us'] === expected['en-us'] ||
    jurisdiction['pt-br'] === expected['pt-br']
  )
}

export function jurisdictionLabel(jurisdiction, lang, t) {
  if (jurisdiction == null) return ''
  if (typeof jurisdiction === 'string') {
    return t ? t(`s3.jurisdiction.${jurisdiction}`, { defaultValue: jurisdiction }) : jurisdiction
  }
  return pickLocalized(jurisdiction, lang)
}

export function primaryRegulatoryContext(contexts = []) {
  if (!contexts.length) return null
  const priority = ['brazil', 'oecd', 'eu', 'us']
  for (const code of priority) {
    const match = contexts.find((context) =>
      jurisdictionMatches(context.jurisdiction, code),
    )
    if (match) return match
  }
  return contexts[0]
}

export function formatJurisdictionBadges(contexts = [], lang, t) {
  const seen = new Set()
  const labels = []
  for (const context of contexts) {
    const label = jurisdictionLabel(context.jurisdiction, lang, t)
    if (!label || seen.has(label)) continue
    seen.add(label)
    labels.push(label)
  }
  return labels.join(' · ')
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
