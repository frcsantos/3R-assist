import { apiFetch } from './api'

export function fetchMethodsCatalogue(lang) {
  const params = new URLSearchParams()
  if (lang) params.set('lang', lang)
  const query = params.toString()
  return apiFetch(`/methods${query ? `?${query}` : ''}`)
}

export function fetchDocumentsCatalogue(categories) {
  const params = new URLSearchParams()
  for (const category of categories ?? []) {
    params.append('category', category)
  }
  const query = params.toString()
  return apiFetch(`/documents${query ? `?${query}` : ''}`)
}
