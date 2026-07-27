import { apiFetch } from './api'

export function fetchAdminTables() {
  return apiFetch('/admin/tables')
}

export function fetchAdminTable(tableName, { limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  })
  return apiFetch(`/admin/tables/${encodeURIComponent(tableName)}?${params}`)
}

export function insertAdminRow(tableName, values) {
  return apiFetch(`/admin/tables/${encodeURIComponent(tableName)}`, {
    method: 'POST',
    body: JSON.stringify({ values }),
  })
}

export function updateAdminCell(tableName, { primaryKey, column, value }) {
  return apiFetch(`/admin/tables/${encodeURIComponent(tableName)}`, {
    method: 'PATCH',
    body: JSON.stringify({
      primary_key: primaryKey,
      column,
      value,
    }),
  })
}

export function deleteAdminRows(tableName, rows) {
  return apiFetch(`/admin/tables/${encodeURIComponent(tableName)}`, {
    method: 'DELETE',
    body: JSON.stringify({ rows }),
  })
}

export function updateAdminColumnComment(tableName, column, comment) {
  return apiFetch(
    `/admin/tables/${encodeURIComponent(tableName)}/columns/${encodeURIComponent(column)}/comment`,
    {
      method: 'PATCH',
      body: JSON.stringify({ comment }),
    },
  )
}

export function extractPolicy({ text, lang }) {
  return apiFetch('/admin/extract/policy', {
    method: 'POST',
    body: JSON.stringify({
      text,
      ...(lang ? { lang } : {}),
    }),
  })
}

export function extractMethodDraft({ text, lang }) {
  return apiFetch('/admin/extract/method-draft', {
    method: 'POST',
    body: JSON.stringify({
      text,
      ...(lang ? { lang } : {}),
    }),
  })
}

export function matchPolicyMethod({ code, name, purpose, limit = 5 }) {
  return apiFetch('/admin/extract/policy/match-method', {
    method: 'POST',
    body: JSON.stringify({
      code,
      name,
      purpose: purpose ?? null,
      limit,
    }),
  })
}
