import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import Button from '../components/Button'
import {
  deleteAdminRows,
  extractMethodDraft,
  extractPolicy,
  fetchAdminTable,
  fetchAdminTables,
  insertAdminRow,
  matchPolicyDocument,
  matchPolicyMethod,
  updateAdminCell,
  updateAdminColumnComment,
} from '../lib/admin'
import { currentLanguage } from '../lib/i18n'
import {
  formatOecdReference,
  jurisdictionLabel,
  JURISDICTION_LABELS,
  methodDescription,
  methodDisplayName,
  pickLocalized,
  primaryRegulatoryContext,
  scorePercent,
} from '../lib/search'

const PAGE_SIZE = 10
const MAIN_TABS = ['database', 'extract', 'docs', 'settings']

function formatCell(value) {
  if (value === null || value === undefined) {
    return '—'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

function toDraft(value) {
  if (value === null || value === undefined) {
    return ''
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

function parseMultiSelectDraft(draft) {
  const trimmed = String(draft ?? '').trim()
  if (!trimmed) return []
  try {
    const parsed = JSON.parse(trimmed)
    if (!Array.isArray(parsed)) return []
    return parsed.map((item) => String(item))
  } catch {
    return []
  }
}

function toMultiSelectDraft(selected) {
  if (!selected?.length) return ''
  return JSON.stringify(selected, null, 2)
}

function isJsonColumnType(type) {
  return type === 'jsonb' || type === 'json'
}

/** Columns that store JSON arrays of vocabulary codes (admin multi-select). */
const MULTI_SELECT_COLUMNS = new Set(['routes_applicable'])

function isMultiSelectColumn(column, type, options) {
  if (!options?.length) return false
  if (MULTI_SELECT_COLUMNS.has(column)) return true
  return isJsonColumnType(type)
}

const RATIONALE_3R_COLUMNS = [
  ['replacement_rationale', 'replacement'],
  ['reduction_rationale', 'reduction'],
  ['refinement_rationale', 'refinement'],
]

function category3rFromRationales(values) {
  return RATIONALE_3R_COLUMNS.filter(
    ([column]) => String(values[column] ?? '').trim() !== '',
  ).map(([, label]) => label)
}

function withDerivedCategory3r(values, columns) {
  if (!columns.includes('category_3r')) return values
  const hasRationale = RATIONALE_3R_COLUMNS.some(([column]) =>
    columns.includes(column),
  )
  if (!hasRationale) return values
  return {
    ...values,
    category_3r: toDraft(category3rFromRationales(values)),
  }
}

function fromDraft(draft, original) {
  const trimmed = draft.trim()
  if (trimmed === '') {
    return null
  }
  if (typeof original === 'object' && original !== null) {
    return JSON.parse(trimmed)
  }
  if (typeof original === 'boolean') {
    const lower = trimmed.toLowerCase()
    if (lower === 'true') return true
    if (lower === 'false') return false
    return trimmed
  }
  if (typeof original === 'number') {
    const number = Number(trimmed)
    return Number.isNaN(number) ? trimmed : number
  }
  return draft
}

function rowKey(row, primaryKey, fallback) {
  if (!primaryKey?.length) {
    return fallback
  }
  return primaryKey.map((column) => String(row[column])).join('|')
}

function primaryKeyValues(row, primaryKey) {
  return Object.fromEntries(primaryKey.map((column) => [column, row[column]]))
}

function tabClass(isActive) {
  return isActive
    ? 'border-b-2 border-primary px-3 py-2 font-nav-link text-nav-link font-medium text-primary'
    : 'px-3 py-2 font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary'
}

function HintIcon({ label, description, hasComment, onClick }) {
  const tooltip = description || label
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={tooltip}
      className={`ml-1 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[10px] font-medium leading-none transition-colors ${
        hasComment
          ? 'border-primary text-primary hover:bg-primary hover:text-on-primary'
          : 'border-on-surface-variant/40 text-on-surface-variant/60 hover:border-primary hover:text-primary'
      }`}
    >
      i
    </button>
  )
}

function CloseIconButton({ label, disabled, onClick }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      aria-label={label}
      title={label}
      className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-on-secondary-container transition-colors hover:bg-surface-container hover:text-primary disabled:opacity-40"
    >
      <svg
        viewBox="0 0 16 16"
        aria-hidden="true"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      >
        <path d="M4 4l8 8M12 4l-8 8" />
      </svg>
    </button>
  )
}

function EditIconButton({ label, disabled, onClick }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      aria-label={label}
      title={label}
      className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-primary transition-colors hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-40"
    >
      <svg
        viewBox="0 0 16 16"
        aria-hidden="true"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M11.5 2.5l2 2L5 13H3v-2l8.5-8.5z" />
      </svg>
    </button>
  )
}

function csvEscape(value) {
  if (value === null || value === undefined) {
    return ''
  }
  const text =
    typeof value === 'object' ? JSON.stringify(value) : String(value)
  if (/[",\r\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

function rowsToCsv(columns, rows) {
  const header = columns.map(csvEscape).join(',')
  const lines = rows.map((row) =>
    columns.map((column) => csvEscape(row[column])).join(','),
  )
  return [header, ...lines].join('\r\n')
}

function downloadCsv(filename, csv) {
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const EXPORT_PAGE_SIZE = 500

function AddRowModal({
  table,
  columns,
  comments,
  types,
  requiredColumns = [],
  foreignKeys = {},
  columnOptions = {},
  mode = 'create',
  initialValues = null,
  lockedColumns = [],
  primaryKey = null,
  protocolAssist = false,
  title = null,
  onClose,
  onSaved,
}) {
  const { t } = useTranslation()
  const isEdit = mode === 'edit'
  const requiredSet = new Set(requiredColumns)
  const lockedSet = new Set(lockedColumns)
  const derivesCategory3r =
    columns.includes('category_3r') &&
    RATIONALE_3R_COLUMNS.some(([column]) => columns.includes(column))
  if (derivesCategory3r) {
    lockedSet.add('category_3r')
  }
  const [values, setValues] = useState(() =>
    withDerivedCategory3r(
      Object.fromEntries(
        columns.map((column) => [
          column,
          initialValues ? toDraft(initialValues[column]) : '',
        ]),
      ),
      columns,
    ),
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [protocolText, setProtocolText] = useState('')
  const [extracting, setExtracting] = useState(false)
  const [extractElapsedSeconds, setExtractElapsedSeconds] = useState(0)

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape' && !saving && !extracting) {
        onClose()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose, saving, extracting])

  useEffect(() => {
    if (!extracting) {
      setExtractElapsedSeconds(0)
      return undefined
    }

    setExtractElapsedSeconds(0)
    const startedAt = Date.now()
    const timer = window.setInterval(() => {
      setExtractElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000))
    }, 250)

    return () => window.clearInterval(timer)
  }, [extracting])

  function updateValue(column, value) {
    if (lockedSet.has(column)) return
    setValues((current) => {
      const next = {
        ...current,
        [column]: value,
      }
      return withDerivedCategory3r(next, columns)
    })
  }

  async function extractFromProtocol(event) {
    event?.preventDefault?.()
    if (extracting || saving) return
    const trimmed = protocolText.trim()
    if (trimmed.length < POLICY_TEXT_MIN) {
      setError(t('admin.extract.tooShort', { min: POLICY_TEXT_MIN }))
      return
    }

    setExtracting(true)
    setError(null)
    try {
      const result = await extractMethodDraft({
        text: trimmed,
        lang: currentLanguage(),
      })
      const fields = result.fields ?? {}
      setValues((current) => {
        const next = { ...current }
        for (const column of columns) {
          if (lockedSet.has(column) && column !== 'category_3r') continue
          if (!(column in fields)) continue
          const value = fields[column]
          if (value === null || value === undefined) continue
          if (typeof value === 'string' && value.trim() === '') continue
          next[column] = toDraft(value)
        }
        return withDerivedCategory3r(next, columns)
      })
    } catch (err) {
      setError(err.message ?? t('admin.extract.methodDraftError'))
    } finally {
      setExtracting(false)
    }
  }

  async function submit() {
    if (saving || extracting) return

    const missing = columns.filter(
      (column) =>
        !lockedSet.has(column) &&
        requiredSet.has(column) &&
        String(values[column] ?? '').trim() === '',
    )
    if (missing.length > 0) {
      setError(t('admin.requiredFieldsMissing', { fields: missing.join(', ') }))
      return
    }

    setSaving(true)
    setError(null)
    try {
      const payload = withDerivedCategory3r(values, columns)
      if (isEdit) {
        if (!primaryKey) {
          throw new Error(t('admin.editRowError'))
        }
        let lastRow = null
        for (const column of columns) {
          if (lockedSet.has(column) && column !== 'category_3r') continue
          const nextValue = payload[column] ?? ''
          const previousValue = initialValues
            ? toDraft(initialValues[column])
            : ''
          if (nextValue === previousValue) continue
          const result = await updateAdminCell(table, {
            primaryKey,
            column,
            value: nextValue,
          })
          lastRow = result.row
        }
        onSaved(lastRow)
      } else {
        const result = await insertAdminRow(table, payload)
        onSaved(result.row)
      }
    } catch (err) {
      setError(
        err.message ?? (isEdit ? t('admin.editRowError') : t('admin.addRowError')),
      )
    } finally {
      setSaving(false)
    }
  }

  const fieldClass =
    'w-full rounded border border-border-subtle bg-surface-container-lowest px-3 py-2 font-metadata text-metadata text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60'
  const firstEditableIndex = columns.findIndex((column) => !lockedSet.has(column))
  const protocolTrimmedLength = protocolText.trim().length
  const canExtract =
    protocolAssist &&
    protocolTrimmedLength >= POLICY_TEXT_MIN &&
    !extracting &&
    !saving

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 px-container-padding py-section-gap"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget && !saving && !extracting) {
          onClose()
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="row-form-title"
        className="flex max-h-full w-full max-w-3xl flex-col rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding shadow-lg"
      >
        <div className="mb-card-gap flex items-start justify-between gap-3">
          <h2
            id="row-form-title"
            className="font-headline-lg text-headline-lg text-primary"
          >
            {title ?? (isEdit ? t('admin.editRow') : t('admin.addRow'))}
          </h2>
          <CloseIconButton
            label={t('admin.close')}
            disabled={saving || extracting}
            onClick={onClose}
          />
        </div>

        {error && (
          <p className="mb-card-gap font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        )}

        <div className="min-h-0 flex-1 space-y-card-gap overflow-y-auto pr-1">
          {protocolAssist ? (
            <form
              onSubmit={extractFromProtocol}
              className="space-y-2 border-b border-border-subtle pb-card-gap"
            >
              <label className="block min-w-0" htmlFor="method-protocol-text">
                <span className="mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant">
                  {t('admin.extract.methodProtocolLabel')}
                </span>
                <textarea
                  id="method-protocol-text"
                  rows={6}
                  value={protocolText}
                  disabled={saving || extracting}
                  onChange={(event) => setProtocolText(event.target.value)}
                  placeholder={t('admin.extract.methodProtocolPlaceholder')}
                  className="w-full rounded border border-border-subtle bg-surface-container-lowest px-3 py-2 font-metadata text-metadata text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60"
                />
              </label>
              <p className="font-metadata text-metadata text-on-secondary-container opacity-65">
                {t('admin.extract.methodProtocolHint')}
              </p>
              {protocolTrimmedLength > 0 &&
              protocolTrimmedLength < POLICY_TEXT_MIN ? (
                <p className="font-metadata text-metadata text-error" role="alert">
                  {t('admin.extract.tooShort', { min: POLICY_TEXT_MIN })}
                </p>
              ) : null}
              <div className="flex justify-end">
                <Button type="submit" size="sm" disabled={!canExtract}>
                  {extracting
                    ? t('admin.extract.submittingSeconds', {
                        seconds: extractElapsedSeconds,
                      })
                    : t('admin.extract.submit')}
                </Button>
              </div>
            </form>
          ) : null}
          {columns.map((column, index) => {
            const hint = comments?.[column]
            const type = types?.[column]
            const locked = lockedSet.has(column)
            const required = !locked && requiredSet.has(column)
            const options = columnOptions?.[column] ?? []
            const foreignKey = foreignKeys?.[column]
            const useSelect = options.length > 0
            const useMultiSelect = isMultiSelectColumn(column, type, options)
            const autoFocus = !protocolAssist && index === firstEditableIndex
            const labelId = `row-field-${column}-label`
            const fieldId = `row-field-${column}`
            const selectedValues = useMultiSelect
              ? parseMultiSelectDraft(values[column])
              : []

            function toggleMultiOption(optionValue) {
              const next = selectedValues.includes(optionValue)
                ? selectedValues.filter((item) => item !== optionValue)
                : [...selectedValues, optionValue]
              updateValue(column, toMultiSelectDraft(next))
            }

            return (
              <div
                key={column}
                className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] sm:items-start sm:gap-4"
              >
                <div className="block min-w-0">
                  <label
                    id={labelId}
                    htmlFor={useMultiSelect ? undefined : fieldId}
                    className="mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant"
                  >
                    {column}
                    {required ? (
                      <span className="ml-0.5 text-error" aria-hidden="true">
                        *
                      </span>
                    ) : null}
                    {type ? (
                      <span className="ml-1 normal-case opacity-65">({type})</span>
                    ) : null}
                    {foreignKey ? (
                      <span className="ml-1 normal-case opacity-65">
                        → {foreignKey.table}.{foreignKey.column}
                      </span>
                    ) : null}
                  </label>
                  {useMultiSelect ? (
                    <div
                      id={fieldId}
                      role="group"
                      aria-labelledby={labelId}
                      className={`${fieldClass} flex flex-col gap-2`}
                    >
                      {options.map((option, optionIndex) => {
                        const optionValue = String(option.value)
                        const optionId = `${fieldId}-${optionValue}`
                        const checked = selectedValues.includes(optionValue)
                        return (
                          <label
                            key={optionValue}
                            htmlFor={optionId}
                            className="inline-flex cursor-pointer items-center gap-2 font-metadata text-metadata text-on-surface"
                          >
                            <input
                              id={optionId}
                              type="checkbox"
                              checked={checked}
                              disabled={saving || extracting || locked}
                              autoFocus={autoFocus && optionIndex === 0}
                              onChange={() => toggleMultiOption(optionValue)}
                              className="h-4 w-4 shrink-0 rounded border-border-subtle text-primary accent-primary"
                            />
                            {option.label}
                          </label>
                        )
                      })}
                    </div>
                  ) : useSelect ? (
                    <select
                      id={fieldId}
                      autoFocus={autoFocus}
                      value={values[column] ?? ''}
                      disabled={saving || extracting || locked}
                      required={required}
                      onChange={(event) => updateValue(column, event.target.value)}
                      className={fieldClass}
                    >
                      <option value="">
                        {required
                          ? t('admin.selectRequired')
                          : t('admin.selectOptional')}
                      </option>
                      {options.map((option) => (
                        <option
                          key={String(option.value)}
                          value={String(option.value)}
                        >
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      id={fieldId}
                      type="text"
                      autoFocus={autoFocus}
                      value={values[column] ?? ''}
                      disabled={saving || extracting || locked}
                      required={required}
                      onChange={(event) => updateValue(column, event.target.value)}
                      className={fieldClass}
                    />
                  )}
                </div>
                <p className="whitespace-pre-wrap font-metadata text-metadata text-on-secondary-container opacity-65 sm:pt-6">
                  {hint || t('admin.noCommentHint')}
                </p>
              </div>
            )
          })}
        </div>

        <div className="mt-card-gap flex gap-3 border-t border-border-subtle pt-card-gap">
          <button
            type="button"
            disabled={saving || extracting}
            onClick={submit}
            className="font-metadata text-metadata text-primary hover:underline disabled:opacity-40"
          >
            {saving ? t('admin.saving') : t('admin.ok')}
          </button>
          <button
            type="button"
            disabled={saving || extracting}
            onClick={onClose}
            className="font-metadata text-metadata text-on-secondary-container hover:underline disabled:opacity-40"
          >
            {t('admin.cancel')}
          </button>
        </div>
      </div>
    </div>
  )
}

function ColumnCommentModal({ table, column, comment, onClose, onSaved }) {
  const { t } = useTranslation()
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(comment ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape' && !saving) {
        if (editing) {
          setEditing(false)
          setDraft(comment ?? '')
          setError(null)
        } else {
          onClose()
        }
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [comment, editing, onClose, saving])

  function startEdit() {
    if (saving) return
    setError(null)
    setDraft(comment ?? '')
    setEditing(true)
  }

  function cancelEdit() {
    if (saving) return
    setEditing(false)
    setDraft(comment ?? '')
    setError(null)
  }

  async function saveEdit() {
    if (saving) return
    setSaving(true)
    setError(null)
    try {
      const result = await updateAdminColumnComment(table, column, draft)
      onSaved(result.comment)
      setEditing(false)
    } catch (err) {
      setError(err.message ?? t('admin.saveError'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 px-container-padding"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget && !saving && !editing) {
          onClose()
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="column-comment-title"
        className="w-full max-w-lg rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding shadow-lg"
      >
        <div className="mb-card-gap flex items-start justify-between gap-3">
          <div>
            <p className="font-label-caps text-label-caps uppercase text-on-surface-variant">
              {t('admin.columnComment')}
            </p>
            <h2
              id="column-comment-title"
              className="mt-fine-gap font-headline-lg text-headline-lg text-primary"
            >
              {column}
            </h2>
          </div>
          <CloseIconButton
            label={t('admin.close')}
            disabled={saving}
            onClick={onClose}
          />
        </div>

        {error && (
          <p className="mb-card-gap font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        )}

        {editing ? (
          <div className="flex flex-col gap-2">
            <textarea
              autoFocus
              rows={6}
              value={draft}
              disabled={saving}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
                  event.preventDefault()
                  saveEdit()
                }
              }}
              className="w-full rounded border border-border-subtle bg-surface-container-lowest px-3 py-2 font-body-base text-body-base text-on-surface outline-none focus:border-primary"
            />
            <div className="flex gap-3">
              <button
                type="button"
                disabled={saving}
                onClick={saveEdit}
                className="font-metadata text-metadata text-primary hover:underline disabled:opacity-40"
              >
                {saving ? t('admin.saving') : t('admin.save')}
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={cancelEdit}
                className="font-metadata text-metadata text-on-secondary-container hover:underline disabled:opacity-40"
              >
                {t('admin.cancel')}
              </button>
            </div>
          </div>
        ) : (
          <p
            onDoubleClick={startEdit}
            title={t('admin.editHint')}
            className="min-h-[6rem] cursor-text whitespace-pre-wrap rounded border border-transparent px-1 py-1 font-body-base text-body-base text-on-surface hover:border-border-subtle"
          >
            {comment ? (
              comment
            ) : (
              <span className="text-on-secondary-container opacity-65">
                {t('admin.noComment')}
              </span>
            )}
          </p>
        )}
      </div>
    </div>
  )
}

function DatabasePanel() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const [tables, setTables] = useState([])
  const [activeTable, setActiveTable] = useState(null)
  const [page, setPage] = useState(0)
  const [tableData, setTableData] = useState(null)
  const [loadingTables, setLoadingTables] = useState(true)
  const [loadingData, setLoadingData] = useState(false)
  const [error, setError] = useState(null)
  const [edit, setEdit] = useState(null)
  const [saving, setSaving] = useState(false)
  const [selected, setSelected] = useState({})
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [commentColumn, setCommentColumn] = useState(null)
  const [rowModal, setRowModal] = useState(null)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadTables() {
      setLoadingTables(true)
      setError(null)
      try {
        const result = await fetchAdminTables()
        if (cancelled) return
        setTables(result.tables)
      } catch (err) {
        if (!cancelled) {
          setError(err.message ?? t('admin.loadError'))
        }
      } finally {
        if (!cancelled) {
          setLoadingTables(false)
        }
      }
    }

    loadTables()
    return () => {
      cancelled = true
    }
  }, [t])

  useEffect(() => {
    if (tables.length === 0) return

    const fromHash = location.hash.replace(/^#/, '')
    if (fromHash && tables.includes(fromHash)) {
      setActiveTable(fromHash)
      return
    }

    setActiveTable((current) => current ?? tables[0])
  }, [tables, location.hash])

  function selectTable(table) {
    setActiveTable(table)
    setPage(0)
    setEdit(null)
    setSelected({})
    setConfirmDelete(false)
    setCommentColumn(null)
    setRowModal(null)
    navigate(`/admin/database#${table}`, { replace: true })
  }

  useEffect(() => {
    if (!activeTable) {
      setTableData(null)
      return undefined
    }

    let cancelled = false

    async function loadTable() {
      setLoadingData(true)
      setError(null)
      setEdit(null)
      setSelected({})
      setConfirmDelete(false)
      setCommentColumn(null)
      setRowModal(null)
      try {
        const result = await fetchAdminTable(activeTable, {
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        })
        if (!cancelled) {
          setTableData(result)
        }
      } catch (err) {
        if (!cancelled) {
          setTableData(null)
          setError(err.message ?? t('admin.loadError'))
        }
      } finally {
        if (!cancelled) {
          setLoadingData(false)
        }
      }
    }

    loadTable()
    return () => {
      cancelled = true
    }
  }, [activeTable, page, t])

  const primaryKey = tableData?.primary_key ?? []
  const totalPages = tableData ? Math.max(1, Math.ceil(tableData.total / PAGE_SIZE)) : 1
  const selectedKeys = Object.keys(selected)
  const selectedCount = selectedKeys.length
  const pageRowKeys =
    tableData?.rows.map((row, index) =>
      rowKey(row, primaryKey, `${activeTable}-${tableData.offset + index}`),
    ) ?? []
  const allPageSelected =
    pageRowKeys.length > 0 && pageRowKeys.every((key) => selected[key])

  function startEdit(row, column) {
    if (!primaryKey.length || primaryKey.includes(column) || saving || deleting) {
      return
    }
    setError(null)
    setConfirmDelete(false)
    setEdit({
      rowKey: rowKey(row, primaryKey),
      column,
      draft: toDraft(row[column]),
      original: row[column],
      primaryKey: primaryKeyValues(row, primaryKey),
    })
  }

  function cancelEdit() {
    if (saving) return
    setEdit(null)
  }

  async function exportTableCsv() {
    if (!activeTable || !tableData || exporting) return
    setExporting(true)
    setError(null)
    try {
      const columns = tableData.columns
      const rows = []
      let offset = 0
      let total = Infinity
      while (offset < total) {
        const result = await fetchAdminTable(activeTable, {
          limit: EXPORT_PAGE_SIZE,
          offset,
        })
        rows.push(...result.rows)
        total = result.total
        offset += result.rows.length
        if (result.rows.length === 0) break
      }
      downloadCsv(`${activeTable}.csv`, rowsToCsv(columns, rows))
    } catch (err) {
      setError(err.message ?? t('admin.exportError'))
    } finally {
      setExporting(false)
    }
  }

  function toggleRow(row, key) {
    if (!primaryKey.length || deleting) return
    setConfirmDelete(false)
    setSelected((current) => {
      if (current[key]) {
        const next = { ...current }
        delete next[key]
        return next
      }
      return {
        ...current,
        [key]: primaryKeyValues(row, primaryKey),
      }
    })
  }

  function toggleAllPageRows() {
    if (!primaryKey.length || !tableData || deleting) return
    setConfirmDelete(false)
    setSelected((current) => {
      if (allPageSelected) {
        const next = { ...current }
        for (const key of pageRowKeys) {
          delete next[key]
        }
        return next
      }
      const next = { ...current }
      tableData.rows.forEach((row, index) => {
        const key = rowKey(
          row,
          primaryKey,
          `${activeTable}-${tableData.offset + index}`,
        )
        next[key] = primaryKeyValues(row, primaryKey)
      })
      return next
    })
  }

  function requestDelete() {
    if (selectedCount === 0 || deleting) return
    setEdit(null)
    setError(null)
    setConfirmDelete(true)
  }

  function cancelDelete() {
    if (deleting) return
    setConfirmDelete(false)
  }

  async function confirmDeleteRows() {
    if (!activeTable || !tableData || selectedCount === 0 || deleting) return

    setDeleting(true)
    setError(null)
    try {
      const result = await deleteAdminRows(activeTable, Object.values(selected))
      const remaining = Math.max(0, tableData.total - result.deleted)
      const maxPage = Math.max(0, Math.ceil(remaining / PAGE_SIZE) - 1)
      setSelected({})
      setConfirmDelete(false)
      setEdit(null)
      if (page > maxPage) {
        setPage(maxPage)
      } else {
        const refreshed = await fetchAdminTable(activeTable, {
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        })
        setTableData(refreshed)
      }
    } catch (err) {
      setError(err.message ?? t('admin.deleteError'))
    } finally {
      setDeleting(false)
    }
  }

  async function saveEdit() {
    if (!edit || !activeTable || saving) return

    let value
    try {
      value = fromDraft(edit.draft, edit.original)
    } catch {
      setError(t('admin.invalidValue'))
      return
    }

    setSaving(true)
    setError(null)
    try {
      const result = await updateAdminCell(activeTable, {
        primaryKey: edit.primaryKey,
        column: edit.column,
        value,
      })
      setTableData((current) => {
        if (!current) return current
        return {
          ...current,
          rows: current.rows.map((row) =>
            rowKey(row, current.primary_key) === edit.rowKey ? result.row : row,
          ),
        }
      })
      setEdit(null)
    } catch (err) {
      setError(err.message ?? t('admin.saveError'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      {error && (
        <p className="mb-card-gap font-metadata text-metadata text-error" role="alert">
          {error}
        </p>
      )}

      {loadingTables ? (
        <p className="font-body-base text-body-base text-on-secondary-container">
          {t('admin.loading')}
        </p>
      ) : error && tables.length === 0 ? null : tables.length === 0 ? (
        <p className="font-body-base text-body-base text-on-secondary-container">
          {t('admin.noTables')}
        </p>
      ) : (
        <>
          <div
            className="mb-card-gap flex flex-wrap gap-2 border-b border-border-subtle"
            role="tablist"
            aria-label={t('admin.tablesLabel')}
          >
            {tables.map((table) => {
              const isActive = table === activeTable
              return (
                <button
                  key={table}
                  id={table}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => selectTable(table)}
                  className={tabClass(isActive)}
                >
                  {table}
                </button>
              )
            })}
          </div>

          <section className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding">
            {loadingData ? (
              <p className="font-body-base text-body-base text-on-secondary-container">
                {t('admin.loading')}
              </p>
            ) : tableData ? (
              <>
                <div className="mb-card-gap flex flex-wrap items-center justify-between gap-3">
                  <p className="font-metadata text-metadata text-on-secondary-container">
                    {tableData.total === 0
                      ? t('admin.emptyTable')
                      : t('admin.rowCount', {
                          from: tableData.offset + 1,
                          to: tableData.offset + tableData.rows.length,
                          total: tableData.total,
                        })}
                  </p>
                  <div className="flex flex-wrap items-center gap-3">
                    {tableData.columns.length > 0 ? (
                      <button
                        type="button"
                        disabled={saving || deleting || exporting}
                        onClick={exportTableCsv}
                        className="font-metadata text-metadata text-primary hover:underline disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {exporting ? t('admin.exporting') : t('admin.exportCsv')}
                      </button>
                    ) : null}
                    {tableData.columns.length > 0 ? (
                      <button
                        type="button"
                        disabled={saving || deleting || exporting}
                        onClick={() => {
                          setCommentColumn(null)
                          setConfirmDelete(false)
                          setEdit(null)
                          setRowModal({ mode: 'create' })
                        }}
                        className="font-metadata text-metadata text-primary hover:underline disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {t('admin.addRow')}
                      </button>
                    ) : null}
                    {primaryKey.length > 0 && tableData.rows.length > 0 ? (
                      confirmDelete ? (
                        <div className="flex items-center gap-3">
                          <span className="font-metadata text-metadata text-on-secondary-container">
                            {t('admin.deleteConfirm', { count: selectedCount })}
                          </span>
                          <button
                            type="button"
                            disabled={deleting}
                            onClick={confirmDeleteRows}
                            className="font-metadata text-metadata text-error hover:underline disabled:opacity-40"
                          >
                            {deleting ? t('admin.deleting') : t('admin.deleteConfirmAction')}
                          </button>
                          <button
                            type="button"
                            disabled={deleting}
                            onClick={cancelDelete}
                            className="font-metadata text-metadata text-on-secondary-container hover:underline disabled:opacity-40"
                          >
                            {t('admin.cancel')}
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          disabled={selectedCount === 0 || saving}
                          onClick={requestDelete}
                          className="font-metadata text-metadata text-error hover:underline disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          {selectedCount > 0
                            ? t('admin.deleteSelected', { count: selectedCount })
                            : t('admin.delete')}
                        </button>
                      )
                    ) : null}
                  </div>
                </div>
                {tableData.rows.length === 0 ? null : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-max min-w-full border-collapse text-left">
                        <thead>
                          <tr className="border-b border-border-subtle">
                            {primaryKey.length > 0 ? (
                              <th className="w-8 px-3 py-2">
                                <input
                                  type="checkbox"
                                  checked={allPageSelected}
                                  disabled={deleting}
                                  onChange={toggleAllPageRows}
                                  aria-label={t('admin.selectAll')}
                                  className="align-middle"
                                />
                              </th>
                            ) : null}
                            {primaryKey.length > 0 ? (
                              <th className="w-10 whitespace-nowrap px-2 py-2">
                                <span className="sr-only">{t('admin.edit')}</span>
                              </th>
                            ) : null}
                            {tableData.columns.map((column) => {
                              const comment = tableData.column_comments?.[column] ?? null
                              return (
                                <th
                                  key={column}
                                  className="whitespace-nowrap px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant"
                                >
                                  <span className="inline-flex items-center">
                                    {column}
                                    <HintIcon
                                      label={t('admin.columnCommentHint', {
                                        column,
                                      })}
                                      description={comment || t('admin.noCommentHint')}
                                      hasComment={Boolean(comment)}
                                      onClick={() => setCommentColumn(column)}
                                    />
                                  </span>
                                </th>
                              )
                            })}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle font-metadata text-metadata">
                          {tableData.rows.map((row, index) => {
                            const currentRowKey = rowKey(
                              row,
                              primaryKey,
                              `${activeTable}-${tableData.offset + index}`,
                            )
                            return (
                              <tr
                                key={currentRowKey}
                                className={selected[currentRowKey] ? 'bg-surface-container' : ''}
                              >
                                {primaryKey.length > 0 ? (
                                  <td className="w-8 px-3 py-2 align-top">
                                    <input
                                      type="checkbox"
                                      checked={Boolean(selected[currentRowKey])}
                                      disabled={deleting}
                                      onChange={() => toggleRow(row, currentRowKey)}
                                      aria-label={t('admin.selectRow')}
                                      className="align-middle"
                                    />
                                  </td>
                                ) : null}
                                {primaryKey.length > 0 ? (
                                  <td className="w-10 whitespace-nowrap px-2 py-2 align-top">
                                    <EditIconButton
                                      label={t('admin.edit')}
                                      disabled={saving || deleting || exporting}
                                      onClick={() => {
                                        setCommentColumn(null)
                                        setConfirmDelete(false)
                                        setEdit(null)
                                        setRowModal({ mode: 'edit', row })
                                      }}
                                    />
                                  </td>
                                ) : null}
                                {tableData.columns.map((column) => {
                                  const isPk = primaryKey.includes(column)
                                  const isEditing =
                                    edit?.rowKey === currentRowKey &&
                                    edit?.column === column
                                  const useTextarea =
                                    isEditing &&
                                    (typeof edit.original === 'object' ||
                                      edit.draft.length > 60)

                                  return (
                                    <td
                                      key={column}
                                      className={`px-3 py-2 align-top text-on-surface ${
                                        isEditing ? '' : 'whitespace-nowrap'
                                      } ${
                                        isPk || !primaryKey.length
                                          ? ''
                                          : 'cursor-text'
                                      }`}
                                      onDoubleClick={() => startEdit(row, column)}
                                      title={
                                        isPk || !primaryKey.length
                                          ? undefined
                                          : t('admin.editHint')
                                      }
                                    >
                                      {isEditing ? (
                                        <div className="flex min-w-[12rem] flex-col gap-1">
                                          {useTextarea ? (
                                            <textarea
                                              autoFocus
                                              rows={4}
                                              value={edit.draft}
                                              disabled={saving}
                                              onChange={(event) =>
                                                setEdit((current) =>
                                                  current
                                                    ? {
                                                        ...current,
                                                        draft: event.target.value,
                                                      }
                                                    : current,
                                                )
                                              }
                                              onKeyDown={(event) => {
                                                if (
                                                  event.key === 'Escape'
                                                ) {
                                                  event.preventDefault()
                                                  cancelEdit()
                                                }
                                                if (
                                                  event.key === 'Enter' &&
                                                  (event.metaKey || event.ctrlKey)
                                                ) {
                                                  event.preventDefault()
                                                  saveEdit()
                                                }
                                              }}
                                              className="w-full min-w-[12rem] rounded border border-border-subtle bg-surface-container-lowest px-2 py-1 font-metadata text-metadata text-on-surface outline-none focus:border-primary"
                                            />
                                          ) : (
                                            <input
                                              autoFocus
                                              type="text"
                                              value={edit.draft}
                                              disabled={saving}
                                              onChange={(event) =>
                                                setEdit((current) =>
                                                  current
                                                    ? {
                                                        ...current,
                                                        draft: event.target.value,
                                                      }
                                                    : current,
                                                )
                                              }
                                              onKeyDown={(event) => {
                                                if (event.key === 'Escape') {
                                                  event.preventDefault()
                                                  cancelEdit()
                                                }
                                                if (event.key === 'Enter') {
                                                  event.preventDefault()
                                                  saveEdit()
                                                }
                                              }}
                                              className="w-full min-w-[12rem] rounded border border-border-subtle bg-surface-container-lowest px-2 py-1 font-metadata text-metadata text-on-surface outline-none focus:border-primary"
                                            />
                                          )}
                                          <div className="flex gap-2">
                                            <button
                                              type="button"
                                              disabled={saving}
                                              onClick={saveEdit}
                                              className="font-metadata text-metadata text-primary hover:underline disabled:opacity-40"
                                            >
                                              {saving
                                                ? t('admin.saving')
                                                : t('admin.save')}
                                            </button>
                                            <button
                                              type="button"
                                              disabled={saving}
                                              onClick={cancelEdit}
                                              className="font-metadata text-metadata text-on-secondary-container hover:underline disabled:opacity-40"
                                            >
                                              {t('admin.cancel')}
                                            </button>
                                          </div>
                                        </div>
                                      ) : (
                                        formatCell(row[column])
                                      )}
                                    </td>
                                  )
                                })}
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>

                    {tableData.total > PAGE_SIZE && (
                      <div className="mt-card-gap flex items-center justify-between gap-4">
                        <button
                          type="button"
                          disabled={page === 0}
                          onClick={() => setPage((current) => current - 1)}
                          className="rounded-md border border-border-subtle px-3 py-1.5 font-metadata text-metadata text-on-surface transition-colors hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          {t('admin.prevPage')}
                        </button>
                        <span className="font-metadata text-metadata text-on-secondary-container">
                          {t('admin.pageOf', { current: page + 1, total: totalPages })}
                        </span>
                        <button
                          type="button"
                          disabled={page >= totalPages - 1}
                          onClick={() => setPage((current) => current + 1)}
                          className="rounded-md border border-border-subtle px-3 py-1.5 font-metadata text-metadata text-on-surface transition-colors hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          {t('admin.nextPage')}
                        </button>
                      </div>
                    )}
                  </>
                )}
              </>
            ) : null}
          </section>

          {rowModal && activeTable && tableData ? (
            <AddRowModal
              key={`${rowModal.mode}-${rowModal.mode === 'edit' ? rowKey(rowModal.row, primaryKey) : 'new'}`}
              table={activeTable}
              columns={tableData.columns.filter(
                (column) => !(tableData.auto_columns ?? []).includes(column),
              )}
              comments={tableData.column_comments}
              types={tableData.column_types}
              requiredColumns={tableData.required_columns}
              foreignKeys={tableData.foreign_keys}
              columnOptions={tableData.column_options}
              mode={rowModal.mode}
              initialValues={rowModal.mode === 'edit' ? rowModal.row : null}
              lockedColumns={
                rowModal.mode === 'edit' ? (tableData.primary_key ?? []) : []
              }
              primaryKey={
                rowModal.mode === 'edit'
                  ? primaryKeyValues(rowModal.row, primaryKey)
                  : null
              }
              onClose={() => setRowModal(null)}
              onSaved={async (savedRow) => {
                const wasCreate = rowModal.mode === 'create'
                setRowModal(null)
                setSelected({})
                setConfirmDelete(false)
                setEdit(null)
                if (wasCreate) {
                  if (page !== 0) {
                    setPage(0)
                    return
                  }
                  try {
                    const refreshed = await fetchAdminTable(activeTable, {
                      limit: PAGE_SIZE,
                      offset: 0,
                    })
                    setTableData(refreshed)
                  } catch (err) {
                    setError(err.message ?? t('admin.loadError'))
                  }
                  return
                }
                if (savedRow) {
                  setTableData((current) => {
                    if (!current) return current
                    const key = rowKey(savedRow, current.primary_key)
                    return {
                      ...current,
                      rows: current.rows.map((row) =>
                        rowKey(row, current.primary_key) === key ? savedRow : row,
                      ),
                    }
                  })
                  return
                }
                try {
                  const refreshed = await fetchAdminTable(activeTable, {
                    limit: PAGE_SIZE,
                    offset: page * PAGE_SIZE,
                  })
                  setTableData(refreshed)
                } catch (err) {
                  setError(err.message ?? t('admin.loadError'))
                }
              }}
            />
          ) : null}

          {commentColumn && activeTable && tableData ? (
            <ColumnCommentModal
              table={activeTable}
              column={commentColumn}
              comment={tableData.column_comments?.[commentColumn] ?? null}
              onClose={() => setCommentColumn(null)}
              onSaved={(nextComment) => {
                setTableData((current) => {
                  if (!current) return current
                  return {
                    ...current,
                    column_comments: {
                      ...(current.column_comments ?? {}),
                      [commentColumn]: nextComment,
                    },
                  }
                })
              }}
            />
          ) : null}
        </>
      )}
    </>
  )
}

function PlaceholderPanel({ messageKey }) {
  const { t } = useTranslation()

  return (
    <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
      {t(messageKey)}
    </p>
  )
}

const POLICY_TEXT_MIN = 20
const POLICY_TEXT_MAX = 50000
const EXTRACT_HISTORY_KEY = '3r_assist.extract.history'
const EXTRACT_HISTORY_MAX = 20

function readExtractHistory() {
  try {
    const raw = window.localStorage.getItem(EXTRACT_HISTORY_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function writeExtractHistory(entries) {
  window.localStorage.setItem(EXTRACT_HISTORY_KEY, JSON.stringify(entries))
}

function extractionLabel(entry) {
  const name = entry?.result?.document_name?.trim()
  if (name) return name
  const preview = entry?.text?.trim()?.slice(0, 48)
  if (preview) return preview.length < entry.text.trim().length ? `${preview}…` : preview
  return entry?.savedAt ?? '—'
}

function oecdTgNumberFromRef(ref) {
  if (!ref) return null
  const match = String(ref).match(/\b(?:OECD\s+)?TG\s*(\d{3,4})\b/i)
  return match?.[1] ?? null
}

function oecdTestSearchUrl(testNumber) {
  const params = new URLSearchParams({
    q: `"Test No. ${testNumber}"`,
    orderBy: 'mostRelevant',
    page: '0',
    facetTags: 'oecd-languages:en,oecd-content-types:publications/reports',
  })
  return `https://www.oecd.org/content/oecd/en/search.html?${params.toString()}`
}

function slugifyMethodDraft(value) {
  return String(value ?? '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80)
}

function methodInitialValuesFromExtracted(method, normalizedOecd) {
  const tgNumber =
    oecdTgNumberFromRef(normalizedOecd) ?? oecdTgNumberFromRef(method.code)
  const oecdRef =
    (normalizedOecd && /^TG\s+\d{3,4}$/i.test(normalizedOecd.trim())
      ? normalizedOecd.trim().toUpperCase().replace(/^TG\s+/i, 'TG ')
      : null) ?? (tgNumber ? `TG ${tgNumber}` : '')
  const name = method.name?.trim() ?? ''
  const purpose = method.purpose?.trim() ?? ''
  const code = method.code?.trim() ?? ''

  let slug
  if (tgNumber) {
    const namePart = slugifyMethodDraft(name || code)
    slug = namePart
      ? `oecd-tg${tgNumber}-${namePart}`.slice(0, 80)
      : `oecd-tg${tgNumber}`
  } else if (oecdRef) {
    slug = slugifyMethodDraft(`oecd-${oecdRef}`)
    if (!slug.startsWith('oecd-')) {
      slug = `oecd-${slug}`
    }
  } else {
    slug = slugifyMethodDraft(code || name)
  }

  return {
    slug,
    name: { 'en-us': name, 'pt-br': name },
    description: { 'en-us': purpose || name, 'pt-br': purpose || name },
    text_for_embedding: [oecdRef || code, name, purpose].filter(Boolean).join(' — '),
    oecd_ref: oecdRef,
    source_db: oecdRef ? 'OECD_TG' : '',
    active: 'false',
  }
}

function regulationDateFromDocument(documentDate) {
  if (!documentDate) return ''
  const trimmed = String(documentDate).trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed
  const yearOnly = trimmed.match(/^(20\d{2})$/)
  if (yearOnly) return `${yearOnly[1]}-01-01`
  return trimmed
}

function regulationInitialValuesFromExtracted(
  method,
  { documentDate, institution, matchResult, oecdTgNumber } = {},
) {
  const topMatch = matchResult?.matches?.[0]?.method ?? null
  const isOecd = Boolean(
    oecdTgNumber || matchResult?.normalized_oecd_ref || oecdTgNumberFromRef(method.code),
  )
  const code = method.code?.trim() ?? ''
  const name = method.name?.trim() ?? ''

  return {
    method_id: topMatch?.id ?? '',
    jurisdiction: isOecd ? JURISDICTION_LABELS.oecd : '',
    validation_status: 'validated',
    regulation_status: method.status ?? '',
    regulation_date: regulationDateFromDocument(documentDate),
    regulation_purpose: method.purpose?.trim() ?? '',
    regulatory_body:
      institution?.trim() || (isOecd ? 'OECD' : ''),
    regulatory_doc_id: '',
    regulatory_citation: '',
    notes: [code, name].filter(Boolean).join(' — '),
  }
}

function documentInitialValuesFromExtracted({
  documentName,
  documentDate,
  url,
} = {}) {
  const citation = documentName?.trim() ?? ''
  return {
    slug: slugifyMethodDraft(citation),
    doc_citation: { 'en-us': citation, 'pt-br': citation },
    date: regulationDateFromDocument(documentDate),
    category: 'regulation',
    url: url?.trim() ?? '',
  }
}

function ExpandArrow({ open }) {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className={`h-3.5 w-3.5 transition-transform duration-ethos ${
        open ? 'rotate-90' : ''
      }`}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 4l4 4-4 4" />
    </svg>
  )
}

function ExtractedMethodRow({ method, documentDate, institution }) {
  const { t, i18n } = useTranslation()
  const lang = i18n.language?.startsWith('pt') ? 'pt' : 'en'
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [matchResult, setMatchResult] = useState(null)
  const [addMethodSchema, setAddMethodSchema] = useState(null)
  const [addMethodOpen, setAddMethodOpen] = useState(false)
  const [addMethodLoading, setAddMethodLoading] = useState(false)
  const [addMethodError, setAddMethodError] = useState(null)
  const [addRegulationSchema, setAddRegulationSchema] = useState(null)
  const [addRegulationOpen, setAddRegulationOpen] = useState(false)
  const [addRegulationLoading, setAddRegulationLoading] = useState(false)
  const [addRegulationError, setAddRegulationError] = useState(null)

  async function toggle() {
    const next = !open
    setOpen(next)
    if (!next || loading) return

    setLoading(true)
    setError(null)
    setMatchResult(null)
    setAddMethodError(null)
    setAddRegulationError(null)
    try {
      const result = await matchPolicyMethod({
        code: method.code,
        name: method.name,
        purpose: method.purpose,
      })
      setMatchResult(result)
    } catch {
      setError(t('admin.extract.matchError'))
    } finally {
      setLoading(false)
    }
  }

  async function openAddMethod() {
    if (addMethodLoading || addRegulationLoading) return
    setAddMethodError(null)
    setAddMethodLoading(true)
    try {
      const schema = await fetchAdminTable('methods', { limit: 1, offset: 0 })
      setAddMethodSchema(schema)
      setAddMethodOpen(true)
    } catch {
      setAddMethodError(t('admin.extract.addMethodError'))
    } finally {
      setAddMethodLoading(false)
    }
  }

  async function openAddRegulation() {
    if (addRegulationLoading || addMethodLoading) return
    setAddRegulationError(null)
    setAddRegulationLoading(true)
    try {
      const schema = await fetchAdminTable('regulations', {
        limit: 1,
        offset: 0,
      })
      setAddRegulationSchema(schema)
      setAddRegulationOpen(true)
    } catch {
      setAddRegulationError(t('admin.extract.addRegulationError'))
    } finally {
      setAddRegulationLoading(false)
    }
  }

  const matches = matchResult?.matches ?? []
  const oecdTgNumber =
    oecdTgNumberFromRef(matchResult?.normalized_oecd_ref) ??
    oecdTgNumberFromRef(method.code)
  const colSpan = 5
  const addMethodColumns =
    addMethodSchema?.columns.filter(
      (column) => !(addMethodSchema.auto_columns ?? []).includes(column),
    ) ?? []
  const addRegulationColumns =
    addRegulationSchema?.columns.filter(
      (column) => !(addRegulationSchema.auto_columns ?? []).includes(column),
    ) ?? []

  return (
    <>
      <tr>
        <td className="w-10 px-2 py-2 align-top">
          <button
            type="button"
            onClick={toggle}
            aria-expanded={open}
            aria-label={
              open
                ? t('admin.extract.collapseMatches')
                : t('admin.extract.expandMatches')
            }
            title={
              open
                ? t('admin.extract.collapseMatches')
                : t('admin.extract.expandMatches')
            }
            className="inline-flex h-7 w-7 items-center justify-center rounded-md text-on-secondary-container transition-colors hover:bg-surface-container hover:text-primary"
          >
            <ExpandArrow open={open} />
          </button>
        </td>
        <td className="whitespace-nowrap px-3 py-2 align-top text-on-surface">
          {method.code}
        </td>
        <td className="px-3 py-2 align-top text-on-surface">{method.name}</td>
        <td className="px-3 py-2 align-top text-on-surface">
          {method.purpose || t('admin.extract.notFound')}
        </td>
        <td className="whitespace-nowrap px-3 py-2 align-top text-on-surface">
          {method.status
            ? t(`s3.regulatoryStatus.${method.status}`)
            : t('admin.extract.notFound')}
        </td>
      </tr>
      {open ? (
        <tr className="bg-surface-container/40">
          <td colSpan={colSpan} className="px-3 py-3">
            {loading ? (
              <p className="font-metadata text-metadata text-on-secondary-container">
                {t('admin.extract.matching')}
              </p>
            ) : error ? (
              <p className="font-metadata text-metadata text-error" role="alert">
                {error}
              </p>
            ) : (
              <div className="space-y-3">
                {matches.length === 0 ? (
                  <p className="font-metadata text-metadata text-on-secondary-container opacity-65">
                    {t('admin.extract.noMatches')}
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {matches.map((candidate) => {
                      const dbMethod = candidate.method
                      const oecd = formatOecdReference(dbMethod.oecd_ref)
                      const contexts = dbMethod.regulatory_contexts ?? []
                      const primaryContext = primaryRegulatoryContext(contexts)
                      return (
                        <li
                          key={`${candidate.match_kind}-${dbMethod.id}`}
                          className="rounded-md border border-border-subtle bg-surface-container-lowest px-3 py-2"
                        >
                          <div className="flex flex-wrap items-baseline justify-between gap-2">
                            <p className="font-metadata text-metadata text-on-surface">
                              {methodDisplayName(dbMethod, lang)}
                              <span className="ml-2 opacity-65">
                                ({dbMethod.slug})
                              </span>
                            </p>
                            <p className="font-metadata text-metadata text-on-secondary-container">
                              {candidate.match_kind === 'oecd_ref'
                                ? t('admin.extract.matchByOecd')
                                : t('admin.extract.matchByText')}
                              {' · '}
                              {scorePercent(candidate.score)}%
                              {!dbMethod.active
                                ? ` · ${t('admin.extract.inactive')}`
                                : ''}
                            </p>
                          </div>
                          <p className="mt-1 font-metadata text-metadata text-on-secondary-container opacity-80">
                            {[
                              oecd,
                              dbMethod.endpoint_category,
                              dbMethod.study_domain,
                              dbMethod.source_db,
                            ]
                              .filter(Boolean)
                              .join(' · ')}
                          </p>
                          {primaryContext?.regulation_purpose ? (
                            <p className="mt-1 font-metadata text-metadata text-on-secondary-container">
                              {t('s3.purposeLabel')}: {primaryContext.regulation_purpose}
                            </p>
                          ) : null}
                          {primaryContext?.regulation_status ? (
                            <p className="mt-1 font-metadata text-metadata text-on-secondary-container">
                              {t('admin.extract.regulatoryStatus')}:{' '}
                              {t(
                                `s3.regulatoryStatus.${primaryContext.regulation_status}`,
                              )}
                            </p>
                          ) : null}
                          <p className="mt-1 font-metadata text-metadata text-on-secondary-container opacity-65">
                            {methodDescription(dbMethod, lang)}
                          </p>
                          {contexts.length > 0 ? (
                            <ul className="mt-2 space-y-1">
                              {contexts.map((context, index) => {
                                const name = jurisdictionLabel(
                                  context.jurisdiction,
                                  lang,
                                  t,
                                )
                                const date = context.regulation_date || null
                                const url = context.regulatory_url || null
                                const keyBase =
                                  typeof context.jurisdiction === 'object'
                                    ? context.jurisdiction['en-us']
                                    : context.jurisdiction
                                return (
                                  <li
                                    key={`${keyBase}-${index}`}
                                    className="font-metadata text-metadata text-on-secondary-container"
                                  >
                                    <span>{name || t('admin.extract.notFound')}</span>
                                    <span className="opacity-65">
                                      {' · '}
                                      {date || t('admin.extract.notFound')}
                                    </span>
                                    {' · '}
                                    {url ? (
                                      <a
                                        href={url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-primary underline-offset-2 hover:underline"
                                      >
                                        {t('s3.regulatoryLink')}
                                      </a>
                                    ) : (
                                      <span className="opacity-65">
                                        {t('admin.extract.notFound')}
                                      </span>
                                    )}
                                  </li>
                                )
                              })}
                            </ul>
                          ) : null}
                        </li>
                      )
                    })}
                  </ul>
                )}
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    disabled={addRegulationLoading || addMethodLoading}
                    onClick={openAddRegulation}
                    className="order-1 inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {addRegulationLoading
                      ? t('admin.loading')
                      : t('admin.extract.addRegulation')}
                  </button>
                  <button
                    type="button"
                    disabled={addMethodLoading || addRegulationLoading}
                    onClick={openAddMethod}
                    className="order-2 inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {addMethodLoading
                      ? t('admin.loading')
                      : t('admin.extract.addMethod')}
                  </button>
                  {oecdTgNumber ? (
                    <a
                      href={oecdTestSearchUrl(oecdTgNumber)}
                      target="_blank"
                      rel="noreferrer"
                      className="order-3 inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container"
                    >
                      {t('admin.extract.searchOecd')}
                    </a>
                  ) : null}
                </div>
                {addRegulationError ? (
                  <p
                    className="font-metadata text-metadata text-error"
                    role="alert"
                  >
                    {addRegulationError}
                  </p>
                ) : null}
                {addMethodError ? (
                  <p
                    className="font-metadata text-metadata text-error"
                    role="alert"
                  >
                    {addMethodError}
                  </p>
                ) : null}
              </div>
            )}
          </td>
        </tr>
      ) : null}
      {addRegulationOpen && addRegulationSchema
        ? createPortal(
            <AddRowModal
              key={`extract-add-regulation-${method.code}-${method.name}`}
              table="regulations"
              columns={addRegulationColumns}
              comments={addRegulationSchema.column_comments}
              types={addRegulationSchema.column_types}
              requiredColumns={addRegulationSchema.required_columns}
              foreignKeys={addRegulationSchema.foreign_keys}
              columnOptions={addRegulationSchema.column_options}
              mode="create"
              title={t('admin.extract.addRegulation')}
              initialValues={regulationInitialValuesFromExtracted(method, {
                documentDate,
                institution,
                matchResult,
                oecdTgNumber,
              })}
              onClose={() => setAddRegulationOpen(false)}
              onSaved={() => setAddRegulationOpen(false)}
            />,
            document.body,
          )
        : null}
      {addMethodOpen && addMethodSchema
        ? createPortal(
            <AddRowModal
              key={`extract-add-method-${method.code}-${method.name}`}
              table="methods"
              columns={addMethodColumns}
              comments={addMethodSchema.column_comments}
              types={addMethodSchema.column_types}
              requiredColumns={addMethodSchema.required_columns}
              foreignKeys={addMethodSchema.foreign_keys}
              columnOptions={addMethodSchema.column_options}
              mode="create"
              protocolAssist
              title={t('admin.extract.addMethod')}
              initialValues={methodInitialValuesFromExtracted(
                method,
                matchResult?.normalized_oecd_ref,
              )}
              onClose={() => setAddMethodOpen(false)}
              onSaved={() => setAddMethodOpen(false)}
            />,
            document.body,
          )
        : null}
    </>
  )
}

function ExtractPanel() {
  const { t, i18n } = useTranslation()
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [documentUrl, setDocumentUrl] = useState('')
  const [documentMatches, setDocumentMatches] = useState(null)
  const [documentSearchLoading, setDocumentSearchLoading] = useState(false)
  const [documentSearchError, setDocumentSearchError] = useState(null)
  const [addDocumentSchema, setAddDocumentSchema] = useState(null)
  const [addDocumentOpen, setAddDocumentOpen] = useState(false)
  const [addDocumentLoading, setAddDocumentLoading] = useState(false)
  const [addDocumentError, setAddDocumentError] = useState(null)
  const [history, setHistory] = useState(() => readExtractHistory())
  const [activeHistoryId, setActiveHistoryId] = useState(null)

  useEffect(() => {
    if (!submitting) {
      setElapsedSeconds(0)
      return undefined
    }

    setElapsedSeconds(0)
    const startedAt = Date.now()
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000))
    }, 250)

    return () => window.clearInterval(timer)
  }, [submitting])

  const trimmedLength = text.trim().length
  const canSubmit = trimmedLength >= POLICY_TEXT_MIN && !submitting
  const dateLocale = i18n.language?.startsWith('pt') ? 'pt-BR' : 'en-US'

  function persistHistory(entries) {
    setHistory(entries)
    writeExtractHistory(entries)
  }

  function clearDocumentSearch() {
    setDocumentMatches(null)
    setDocumentSearchError(null)
  }

  function loadHistoryEntry(entry) {
    setError(null)
    setText(entry.text ?? '')
    setResult(entry.result ?? null)
    setDocumentUrl('')
    clearDocumentSearch()
    setAddDocumentError(null)
    setActiveHistoryId(entry.id)
  }

  async function searchDocuments() {
    if (documentSearchLoading || !result) return
    setDocumentSearchError(null)
    setDocumentSearchLoading(true)
    try {
      const matched = await matchPolicyDocument({
        documentName: result.document_name,
        documentDate: result.document_date,
        institution: result.responsible_institution,
        url: documentUrl,
      })
      setDocumentMatches(matched.matches ?? [])
    } catch {
      setDocumentMatches(null)
      setDocumentSearchError(t('admin.extract.searchDocumentError'))
    } finally {
      setDocumentSearchLoading(false)
    }
  }

  async function openAddDocument() {
    if (addDocumentLoading || !result) return
    setAddDocumentError(null)
    setAddDocumentLoading(true)
    try {
      const schema = await fetchAdminTable('documents', { limit: 1, offset: 0 })
      setAddDocumentSchema(schema)
      setAddDocumentOpen(true)
    } catch {
      setAddDocumentError(t('admin.extract.addDocumentError'))
    } finally {
      setAddDocumentLoading(false)
    }
  }

  function removeHistoryEntry(entryId) {
    const next = history.filter((entry) => entry.id !== entryId)
    persistHistory(next)
    if (activeHistoryId === entryId) {
      setActiveHistoryId(null)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) return

    setError(null)
    setSubmitting(true)
    try {
      const sourceText = text.trim()
      const extracted = await extractPolicy({
        text: sourceText,
        lang: currentLanguage(),
      })
      const entry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        savedAt: new Date().toISOString(),
        text: sourceText,
        result: extracted,
      }
      persistHistory([entry, ...history].slice(0, EXTRACT_HISTORY_MAX))
      setActiveHistoryId(entry.id)
      setResult(extracted)
      setDocumentUrl('')
      clearDocumentSearch()
      setAddDocumentError(null)
    } catch (err) {
      setResult(null)
      setDocumentUrl('')
      clearDocumentSearch()
      setError(err.message ?? t('admin.extract.error'))
    } finally {
      setSubmitting(false)
    }
  }

  const addDocumentColumns =
    addDocumentSchema?.columns.filter(
      (column) => !(addDocumentSchema.auto_columns ?? []).includes(column),
    ) ?? []

  return (
    <div className="space-y-section-gap">
      {history.length > 0 ? (
        <section className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding">
          <h2 className="mb-card-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
            {t('admin.extract.savedTitle')}
          </h2>
          <ul className="divide-y divide-border-subtle">
            {history.map((entry) => {
              const isActive = entry.id === activeHistoryId
              const methodCount = entry.result?.methods?.length ?? 0
              const savedLabel = new Date(entry.savedAt).toLocaleString(dateLocale, {
                dateStyle: 'short',
                timeStyle: 'short',
              })
              return (
                <li
                  key={entry.id}
                  className={`flex flex-wrap items-center gap-2 py-2 ${
                    isActive ? 'bg-surface-container/50' : ''
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => loadHistoryEntry(entry)}
                    className="min-w-0 flex-1 text-left transition-colors hover:text-primary"
                  >
                    <span className="block truncate font-metadata text-metadata text-on-surface">
                      {extractionLabel(entry)}
                    </span>
                    <span className="block font-metadata text-metadata text-on-secondary-container opacity-65">
                      {t('admin.extract.savedMeta', {
                        date: savedLabel,
                        count: methodCount,
                      })}
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => removeHistoryEntry(entry.id)}
                    className="shrink-0 rounded-md px-2 py-1 font-metadata text-metadata text-on-secondary-container transition-colors hover:bg-surface-container hover:text-error"
                    title={t('admin.extract.removeSaved')}
                    aria-label={t('admin.extract.removeSaved')}
                  >
                    {t('admin.extract.removeSaved')}
                  </button>
                </li>
              )
            })}
          </ul>
        </section>
      ) : null}

      <form
        onSubmit={handleSubmit}
        className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding"
      >
        <label
          htmlFor="policy-extraction-text"
          className="mb-card-gap block font-label-caps text-label-caps uppercase text-on-surface-variant"
        >
          {t('admin.extract.policyLabel')}
        </label>
        <div className="relative">
          <textarea
            id="policy-extraction-text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            maxLength={POLICY_TEXT_MAX}
            rows={12}
            disabled={submitting}
            placeholder={t('admin.extract.policyPlaceholder')}
            className="w-full resize-y rounded-lg border border-border-emphasis bg-surface-container-low p-container-padding font-monospace-data text-monospace-data text-on-surface outline-none transition-colors duration-ethos placeholder:text-text-tertiary focus:border-primary disabled:opacity-60"
          />
          <div
            className="pointer-events-none absolute bottom-4 right-4 font-metadata text-metadata text-text-tertiary"
            aria-live="polite"
          >
            {t('admin.extract.charCount', {
              count: text.length,
              max: POLICY_TEXT_MAX,
            })}
          </div>
        </div>

        {trimmedLength > 0 && trimmedLength < POLICY_TEXT_MIN ? (
          <p className="mt-card-gap font-metadata text-metadata text-error" role="alert">
            {t('admin.extract.tooShort', { min: POLICY_TEXT_MIN })}
          </p>
        ) : null}

        {error ? (
          <p className="mt-card-gap font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        ) : null}

        <div className="mt-card-gap flex justify-end">
          <Button type="submit" disabled={!canSubmit}>
            {submitting
              ? t('admin.extract.submittingSeconds', { seconds: elapsedSeconds })
              : t('admin.extract.submit')}
          </Button>
        </div>
      </form>

      {result ? (
        <section className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding">
          <h2 className="mb-card-gap font-headline-lg text-headline-lg text-primary">
            {t('admin.extract.resultsTitle')}
          </h2>

          <dl className="mb-card-gap grid gap-card-gap sm:grid-cols-3">
            <div>
              <dt className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('admin.extract.documentName')}
              </dt>
              <dd className="mt-1 font-metadata text-metadata text-on-surface">
                {result.document_name || t('admin.extract.notFound')}
              </dd>
            </div>
            <div>
              <dt className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('admin.extract.documentDate')}
              </dt>
              <dd className="mt-1 font-metadata text-metadata text-on-surface">
                {result.document_date || t('admin.extract.notFound')}
              </dd>
            </div>
            <div>
              <dt className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('admin.extract.institution')}
              </dt>
              <dd className="mt-1 font-metadata text-metadata text-on-surface">
                {result.responsible_institution || t('admin.extract.notFound')}
              </dd>
            </div>
          </dl>

          <div className="mb-card-gap flex flex-wrap items-end gap-3">
            <div className="min-w-[16rem] flex-1">
              <label
                htmlFor="extract-document-url"
                className="mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant"
              >
                {t('admin.extract.url')}
              </label>
              <input
                id="extract-document-url"
                type="url"
                value={documentUrl}
                onChange={(event) => setDocumentUrl(event.target.value)}
                placeholder={t('admin.extract.urlPlaceholder')}
                className="w-full rounded-md border border-border-emphasis bg-surface-container-low px-3 py-2 font-metadata text-metadata text-on-surface outline-none transition-colors duration-ethos placeholder:text-text-tertiary focus:border-primary"
              />
            </div>
            <button
              type="button"
              disabled={documentSearchLoading}
              onClick={searchDocuments}
              className="inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
            >
              {documentSearchLoading
                ? t('admin.loading')
                : t('admin.extract.searchDocument')}
            </button>
          </div>

          <div className="mb-card-gap space-y-3">
            {documentSearchLoading ? (
              <p className="font-metadata text-metadata text-on-secondary-container">
                {t('admin.extract.searchingDocuments')}
              </p>
            ) : null}
            {documentSearchError ? (
              <p className="font-metadata text-metadata text-error" role="alert">
                {documentSearchError}
              </p>
            ) : null}
            {documentMatches ? (
              documentMatches.length === 0 ? (
                <p className="font-metadata text-metadata text-on-secondary-container opacity-65">
                  {t('admin.extract.noDocumentMatches')}
                </p>
              ) : (
                <ul className="space-y-2">
                  {documentMatches.map((candidate) => {
                    const doc = candidate.document
                    return (
                      <li
                        key={doc.id}
                        className="rounded-md border border-border-subtle bg-surface-container/40 px-3 py-2"
                      >
                        <div className="flex flex-wrap items-baseline justify-between gap-2">
                          <p className="font-metadata text-metadata text-on-surface">
                            {pickLocalized(doc.doc_citation, currentLanguage())}
                            <span className="ml-2 opacity-65">({doc.slug})</span>
                          </p>
                          <p className="font-metadata text-metadata text-on-secondary-container">
                            {candidate.match_kind === 'doc_citation'
                              ? t('admin.extract.matchByDocCitation')
                              : candidate.match_kind === 'url'
                                ? t('admin.extract.matchByUrl')
                                : t('admin.extract.matchByText')}
                            {' · '}
                            {scorePercent(candidate.score)}%
                          </p>
                        </div>
                        <p className="mt-1 font-metadata text-metadata text-on-secondary-container opacity-80">
                          {[
                            doc.category,
                            doc.date,
                            doc.url,
                          ]
                            .filter(Boolean)
                            .join(' · ')}
                        </p>
                      </li>
                    )
                  })}
                </ul>
              )
            ) : null}

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                disabled={addDocumentLoading}
                onClick={openAddDocument}
                className="inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
              >
                {addDocumentLoading
                  ? t('admin.loading')
                  : t('admin.extract.addDocument')}
              </button>
            </div>
            {addDocumentError ? (
              <p className="font-metadata text-metadata text-error" role="alert">
                {addDocumentError}
              </p>
            ) : null}
          </div>

          <h3 className="mb-2 font-label-caps text-label-caps uppercase text-on-surface-variant">
            {t('admin.extract.methods')}
          </h3>
          {result.methods?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[28rem] border-collapse text-left">
                <thead>
                  <tr className="border-b border-border-subtle">
                    <th className="w-10 px-2 py-2" aria-label={t('admin.extract.match')} />
                    <th className="px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant">
                      {t('admin.extract.methodCode')}
                    </th>
                    <th className="px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant">
                      {t('admin.extract.methodName')}
                    </th>
                    <th className="px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant">
                      {t('admin.extract.methodPurpose')}
                    </th>
                    <th className="px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant">
                      {t('admin.extract.regulatoryStatus')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle font-metadata text-metadata">
                  {result.methods.map((method, index) => (
                    <ExtractedMethodRow
                      key={`${method.code}-${method.name}-${index}`}
                      method={method}
                      documentDate={result.document_date}
                      institution={result.responsible_institution}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="font-metadata text-metadata text-on-secondary-container opacity-65">
              {t('admin.extract.noMethods')}
            </p>
          )}
        </section>
      ) : null}
      {addDocumentOpen && addDocumentSchema
        ? createPortal(
            <AddRowModal
              key={`extract-add-document-${result?.document_name ?? 'doc'}`}
              table="documents"
              columns={addDocumentColumns}
              comments={addDocumentSchema.column_comments}
              types={addDocumentSchema.column_types}
              requiredColumns={addDocumentSchema.required_columns}
              foreignKeys={addDocumentSchema.foreign_keys}
              columnOptions={addDocumentSchema.column_options}
              mode="create"
              title={t('admin.extract.addDocument')}
              initialValues={documentInitialValuesFromExtracted({
                documentName: result?.document_name,
                documentDate: result?.document_date,
                url: documentUrl,
              })}
              onClose={() => setAddDocumentOpen(false)}
              onSaved={() => setAddDocumentOpen(false)}
            />,
            document.body,
          )
        : null}
    </div>
  )
}

export default function AdminPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { section } = useParams()
  const activeSection = MAIN_TABS.includes(section) ? section : 'database'

  function selectSection(nextSection) {
    navigate(`/admin/${nextSection}`)
  }

  return (
    <main className="mx-auto w-full max-w-content flex-1 px-container-padding py-section-gap">
      <header className="mb-section-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('admin.title')}
        </h1>

        <div
          className="mt-card-gap flex flex-wrap gap-2 border-b border-border-subtle"
          role="tablist"
          aria-label={t('admin.tabsLabel')}
        >
          {MAIN_TABS.map((tab) => {
            const isActive = tab === activeSection
            return (
              <button
                key={tab}
                id={`admin-tab-${tab}`}
                type="button"
                role="tab"
                aria-selected={isActive}
                aria-controls={`admin-panel-${tab}`}
                onClick={() => selectSection(tab)}
                className={tabClass(isActive)}
              >
                {t(`admin.${tab}.label`)}
              </button>
            )
          })}
        </div>

        <p className="mt-card-gap font-body-base text-body-base text-on-secondary-container opacity-65">
          {t(`admin.${activeSection}.subtitle`)}
        </p>
      </header>

      <div
        id={`admin-panel-${activeSection}`}
        role="tabpanel"
        aria-labelledby={`admin-tab-${activeSection}`}
      >
        {activeSection === 'database' ? (
          <DatabasePanel />
        ) : activeSection === 'extract' ? (
          <ExtractPanel />
        ) : activeSection === 'docs' ? (
          <PlaceholderPanel messageKey="admin.docs.placeholder" />
        ) : (
          <PlaceholderPanel messageKey="admin.settings.placeholder" />
        )}
      </div>
    </main>
  )
}
