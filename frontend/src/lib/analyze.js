import { apiFetch } from './api'
import {
  buildExperimentState,
  buildExperimentStates,
  resolveExperimentStates,
} from './experimentState.js'

export {
  buildExperimentState,
  buildExperimentStates,
  resolveExperimentStates,
} from './experimentState.js'

export async function analyzeProtocol({ protocolText, lang }) {
  return apiFetch('/analyze', {
    method: 'POST',
    body: JSON.stringify({ protocol_text: protocolText, lang }),
  })
}

export function uploadProtocolSource(file) {
  const body = new FormData()
  body.append('file', file)
  return apiFetch('/admin/extract/upload', {
    method: 'POST',
    body,
  })
}

export function buildAnalysisState(
  apiResponse,
  { protocolText, lang, isMock = false },
) {
  const experiments = apiResponse.experiments ?? []
  const experimentStates = buildExperimentStates(experiments)
  const primary = experimentStates[0]
  if (!primary) {
    throw new Error('No experiments returned from analysis.')
  }

  return {
    experiments,
    experimentStates,
    experimentCount: experiments.length,
    activeExperimentIndex: 0,
    studyType: primary.studyType,
    notes: primary.notes,
    evidence: primary.evidence,
    fieldConfidence: primary.fieldConfidence,
    params: primary.params,
    protocolText,
    lang,
    isMock,
  }
}
