import { apiFetch } from './api'

export function fetchAdminSettings() {
  return apiFetch('/admin/settings')
}

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

export function extractPolicy({ text, lang, sourceUrl, signal }) {
  return apiFetch('/admin/extract/policy', {
    method: 'POST',
    body: JSON.stringify({
      text,
      ...(lang ? { lang } : {}),
      ...(sourceUrl ? { source_url: sourceUrl } : {}),
    }),
    signal,
  })
}

export function estimateExtract({ text, lang, mode, categoryHint, sourceUrl, signal }) {
  return apiFetch('/admin/extract/estimate', {
    method: 'POST',
    body: JSON.stringify({
      text,
      mode: mode ?? 'policy',
      ...(lang ? { lang } : {}),
      ...(categoryHint ? { category_hint: categoryHint } : {}),
      ...(sourceUrl ? { source_url: sourceUrl } : {}),
    }),
    signal,
  })
}

export function resolveExtractSource({ text, signal }) {
  return apiFetch('/admin/extract/resolve', {
    method: 'POST',
    body: JSON.stringify({ text }),
    signal,
  })
}

export function uploadExtractSource(file) {
  const body = new FormData()
  body.append('file', file)
  return apiFetch('/admin/extract/upload', {
    method: 'POST',
    body,
  })
}

export function extractDocumentDraft({ text, lang, categoryHint, sourceUrl, signal }) {
  return apiFetch('/admin/extract/document-draft', {
    method: 'POST',
    body: JSON.stringify({
      text,
      ...(lang ? { lang } : {}),
      ...(categoryHint ? { category_hint: categoryHint } : {}),
      ...(sourceUrl ? { source_url: sourceUrl } : {}),
    }),
    signal,
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

export function matchPolicyDocument({
  documentName,
  documentDate,
  institution,
  url,
  limit = 5,
} = {}) {
  return apiFetch('/admin/extract/policy/match-document', {
    method: 'POST',
    body: JSON.stringify({
      document_name: documentName ?? null,
      document_date: documentDate ?? null,
      responsible_institution: institution ?? null,
      url: url ?? null,
      limit,
    }),
  })
}
