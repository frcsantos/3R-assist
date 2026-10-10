const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const API_TOKEN = import.meta.env.VITE_API_TOKEN ?? ''

function formatErrorDetail(detail) {
  if (detail == null) {
    return ''
  }
  if (typeof detail !== 'object' || Array.isArray(detail)) {
    return String(detail)
  }

  const parts = []
  if (detail.type) {
    parts.push(String(detail.type))
  }
  if (detail.reason) {
    parts.push(String(detail.reason))
  }
  for (const [key, value] of Object.entries(detail)) {
    if (key === 'type' || key === 'reason' || value == null || value === '') {
      continue
    }
    parts.push(
      `${key}: ${typeof value === 'object' ? JSON.stringify(value) : String(value)}`,
    )
  }
  return parts.join(' — ')
}

const PUBMED_TIMEOUT_MS = 720_000 // 12 min — covers slow Ollama under GPU contention

export async function apiFetch(path, options = {}) {
  const { signal, ...rest } = options
  const headers = { ...rest.headers }
  const isFormData =
    typeof FormData !== 'undefined' && rest.body instanceof FormData
  if (!isFormData && headers['Content-Type'] == null) {
    headers['Content-Type'] = 'application/json'
  }
  if (API_TOKEN && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${API_TOKEN}`
  }

  const isPubMed = path.startsWith('/pubmed/')
  const timeoutController = new AbortController()
  let timedOut = false
  const timeoutId = isPubMed
    ? window.setTimeout(() => { timedOut = true; timeoutController.abort() }, PUBMED_TIMEOUT_MS)
    : null

  // Forward external cancellation into our controller
  const onExternalAbort = signal ? () => timeoutController.abort() : null
  if (onExternalAbort) signal.addEventListener('abort', onExternalAbort)

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...rest,
      headers,
      signal: timeoutController.signal,
    })
  } catch (err) {
    if (err?.name === 'AbortError') {
      if (timedOut) {
        const timeoutError = new Error('Analysis is taking too long — the AI model is under load. Please try again.')
        timeoutError.code = 'TIMEOUT'
        throw timeoutError
      }
      const abortError = new Error('Request cancelled')
      abortError.code = 'ABORTED'
      abortError.name = 'AbortError'
      throw abortError
    }
    throw err
  } finally {
    if (timeoutId) window.clearTimeout(timeoutId)
    if (onExternalAbort) signal.removeEventListener('abort', onExternalAbort)
  }
  if (!response.ok) {
    let message = `API ${response.status}: ${response.statusText}`
    let code = null
    try {
      const body = await response.json()
      if (body?.error?.message) {
        message = body.error.message
        code = body.error.code ?? null
        const detailText = formatErrorDetail(body.error.detail)
        if (detailText && !message.includes(detailText)) {
          message = `${message} (${detailText})`
        }
      }
    } catch {
      // keep default message
    }
    const error = new Error(message)
    if (code) error.code = code
    error.status = response.status
    throw error
  }
  return response.json()
}
