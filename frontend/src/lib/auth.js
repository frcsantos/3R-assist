import { apiFetch } from './api'

// User system (F08) helpers. Everything here is inert while the backend
// reports enabled=false via GET /auth/status — the UI stays hidden and no
// sign-in flow is reachable.

const SESSION_STORAGE_KEY = 'assist3r.session'

let statusPromise = null

export function getAuthStatus({ refresh = false } = {}) {
  if (refresh || statusPromise == null) {
    statusPromise = apiFetch('/auth/status')
      .then((body) => body?.enabled === true)
      .catch(() => false)
  }
  return statusPromise
}

export async function isAuthEnabled() {
  return getAuthStatus()
}

export function hasSession() {
  return Boolean(localStorage.getItem(SESSION_STORAGE_KEY))
}

export async function requestMagicLink(email) {
  return apiFetch('/auth/magic-link', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function verifyMagicLink(token) {
  const session = await apiFetch('/auth/verify', {
    method: 'POST',
    body: JSON.stringify({ token }),
  })
  if (session?.token) {
    localStorage.setItem(SESSION_STORAGE_KEY, session.token)
  }
  return session
}

export async function fetchMe() {
  const token = localStorage.getItem(SESSION_STORAGE_KEY)
  if (!token) return null
  try {
    return await apiFetch('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch {
    return null
  }
}

export async function signOut() {
  const token = localStorage.getItem(SESSION_STORAGE_KEY)
  if (token) {
    try {
      await apiFetch('/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
    } catch {
      // Ignore: the session may already be invalid server-side.
    }
  }
  localStorage.removeItem(SESSION_STORAGE_KEY)
}
