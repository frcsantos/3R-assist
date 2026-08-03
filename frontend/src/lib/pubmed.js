import { apiFetch } from './api'

export async function analyzePubMed({ protocol_text, params, lang }) {
  return apiFetch('/pubmed/analyze', {
    method: 'POST',
    body: JSON.stringify({ protocol_text, params, lang }),
  })
}
