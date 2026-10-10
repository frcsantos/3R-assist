import { apiFetch } from './api'

export async function analyzePubMed({ protocol_text, params, lang }) {
  return apiFetch('/pubmed/analyze', {
    method: 'POST',
    body: JSON.stringify({ protocol_text, params, lang }),
  })
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const API_TOKEN = import.meta.env.VITE_API_TOKEN ?? ''

/**
 * Streaming version — uses SSE so Cloudflare doesn't 524 on long LLM runs.
 * Calls onPing() every ~10 s while the server processes.
 * Resolves with the final PubMedAnalysisResponse object.
 */
export async function analyzePubMedStream({ protocol_text, params, lang }, { onPing } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (API_TOKEN) headers['Authorization'] = `Bearer ${API_TOKEN}`

  const response = await fetch(`${API_BASE}/pubmed/analyze-stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ protocol_text, params, lang }),
  })

  if (!response.ok) {
    let message = `API ${response.status}: ${response.statusText}`
    try {
      const body = await response.json()
      if (body?.error?.message) message = body.error.message
    } catch {}
    const err = new Error(message)
    err.status = response.status
    throw err
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE events are separated by \n\n
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      if (!part.trim()) continue
      let eventType = 'message'
      let data = ''
      for (const line of part.split('\n')) {
        if (line.startsWith('event: ')) eventType = line.slice(7).trim()
        else if (line.startsWith('data: ')) data = line.slice(6).trim()
      }
      if (eventType === 'ping') {
        onPing?.()
        continue
      }
      if (eventType === 'result') return JSON.parse(data)
      if (eventType === 'error') {
        const errData = data ? JSON.parse(data) : {}
        const err = new Error(errData.message ?? 'Analysis failed')
        if (errData.code) err.code = errData.code
        throw err
      }
    }
  }

  throw new Error('Stream ended without a result — the server may have crashed.')
}
