import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import ResultCard from '../components/ResultCard'
import Button from '../components/Button'
import MarkdownRenderer from '../components/MarkdownRenderer'
import {
  deleteAdminRows,
  estimateExtract,
  extractDocumentDraft,
  extractMethodDraft,
  extractPolicy,
  extractRegulationDraft,
  fetchAdminRowById,
  fetchAdminSettings,
  fetchAdminTable,
  fetchAdminTables,
  insertAdminRow,
  matchPolicyDocument,
  matchPolicyMethod,
  resolveExtractSource,
  updateAdminCell,
  updateAdminColumnComment,
  uploadExtractSource,
} from '../lib/admin'
import { currentLanguage } from '../lib/i18n'
import {
  formatRegulatoryStatusItems,
  JURISDICTION_LABELS,
  methodDescription,
  methodDetailRows,
  methodDisplayName,
  methodSourceCitation,
  methodThreeRBadges,
  pickLocalized,
  primaryThreeR,
  scorePercent,
} from '../lib/search'

const PAGE_SIZE = 10
const MAIN_TABS = ['database', 'extract', 'docs', 'settings']

const PROJECT_DOC_MODULES = import.meta.glob('../../../docs/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const PROJECT_DOCS = Object.entries(PROJECT_DOC_MODULES)
  .map(([path, content]) => {
    const filename = path.split(/[/\\]/).pop() ?? path
    return {
      id: filename,
      filename,
      content: typeof content === 'string' ? content : String(content ?? ''),
    }
  })
  .sort((a, b) => a.filename.localeCompare(b.filename))

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

function normalizeDraftForCompare(draft) {
  const trimmed = String(draft ?? '').trim()
  if (!trimmed) return ''
  try {
    return JSON.stringify(JSON.parse(trimmed))
  } catch {
    return trimmed
  }
}

function draftsEqual(a, b) {
  return normalizeDraftForCompare(a) === normalizeDraftForCompare(b)
}

function formatOriginalDraft(draft) {
  const trimmed = String(draft ?? '').trim()
  if (!trimmed) return '—'
  try {
    return JSON.stringify(JSON.parse(trimmed))
  } catch {
    return trimmed
  }
}

function isJsonColumnType(type) {
  return type === 'jsonb' || type === 'json'
}

function isBooleanColumnType(type) {
  return type === 'boolean'
}

function normalizeBooleanDraft(draft) {
  const trimmed = String(draft ?? '').trim().toLowerCase()
  if (trimmed === 'true' || trimmed === 't' || trimmed === '1' || trimmed === 'yes') {
    return 'true'
  }
  if (trimmed === 'false' || trimmed === 'f' || trimmed === '0' || trimmed === 'no') {
    return 'false'
  }
  return ''
}

/** Columns that store JSON arrays of vocabulary codes (admin multi-select). */
const MULTI_SELECT_COLUMNS = new Set([
  'routes_applicable',
  'categories',
  'test_system',
])

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

function nonemptyRationaleDraft(value) {
  if (value == null) return false
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return false
    try {
      const parsed = JSON.parse(trimmed)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return Object.values(parsed).some(
          (part) => typeof part === 'string' && part.trim() !== '',
        )
      }
    } catch {
      /* plain string rationale */
    }
    return true
  }
  if (typeof value === 'object') {
    return Object.values(value).some(
      (part) => typeof part === 'string' && part.trim() !== '',
    )
  }
  return false
}

function category3rFromRationales(values) {
  return RATIONALE_3R_COLUMNS.filter(([column]) =>
    nonemptyRationaleDraft(values[column]),
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

function fromDraft(draft, original, type) {
  const trimmed = draft.trim()
  if (trimmed === '') {
    return null
  }
  if (typeof original === 'object' && original !== null) {
    return JSON.parse(trimmed)
  }
  if (typeof original === 'boolean' || isBooleanColumnType(type)) {
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
  documentInitialValues = null,
  title = null,
  overlayClassName = 'z-50',
  onClose,
  onSaved,
}) {
  const { t } = useTranslation()
  const isEdit = mode === 'edit'
  const documentAssist = table === 'documents' && isEdit
  const methodAssist = table === 'methods' && (protocolAssist || isEdit)
  const regulationAssist = table === 'regulations' && isEdit
  const sourceAssist = methodAssist || documentAssist || regulationAssist
  const showOriginalValues = isEdit && sourceAssist
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
  const [originalValues] = useState(() =>
    Object.fromEntries(
      columns.map((column) => [
        column,
        initialValues ? toDraft(initialValues[column]) : '',
      ]),
    ),
  )
  const [fieldOptions, setFieldOptions] = useState(() => columnOptions ?? {})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [protocolText, setProtocolText] = useState('')
  const [extracting, setExtracting] = useState(false)
  const [extractElapsedSeconds, setExtractElapsedSeconds] = useState(0)
  const [uploadedFileName, setUploadedFileName] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)
  const uploadInputId = useId()
  const [nestedDocumentSchema, setNestedDocumentSchema] = useState(null)
  const [nestedDocumentOpen, setNestedDocumentOpen] = useState(false)
  const [nestedDocumentLoading, setNestedDocumentLoading] = useState(false)
  const [nestedDocumentError, setNestedDocumentError] = useState(null)

  useEffect(() => {
    setFieldOptions(columnOptions ?? {})
  }, [columnOptions])

  useEffect(() => {
    function onKeyDown(event) {
      if (
        event.key === 'Escape' &&
        !saving &&
        !extracting &&
        !uploading &&
        !nestedDocumentOpen
      ) {
        onClose()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose, saving, extracting, uploading, nestedDocumentOpen])

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

  async function openNestedDocument() {
    if (
      nestedDocumentLoading ||
      saving ||
      extracting ||
      uploading ||
      nestedDocumentOpen
    ) {
      return
    }
    setNestedDocumentError(null)
    setNestedDocumentLoading(true)
    try {
      const schema = await fetchAdminTable('documents', { limit: 1, offset: 0 })
      setNestedDocumentSchema(schema)
      setNestedDocumentOpen(true)
    } catch {
      setNestedDocumentError(t('admin.extract.addDocumentError'))
    } finally {
      setNestedDocumentLoading(false)
    }
  }

  async function handleNestedDocumentSaved(row) {
    setNestedDocumentOpen(false)
    if (row?.id != null) {
      updateValue('source_doc_id', String(row.id))
    }
    try {
      const schema = await fetchAdminTable(table, { limit: 1, offset: 0 })
      const refreshed = schema.column_options?.source_doc_id
      if (refreshed) {
        setFieldOptions((current) => ({
          ...current,
          source_doc_id: refreshed,
        }))
      }
    } catch {
      // Keep existing options; newly created id is still selected.
    }
  }

  function clearUploadedFile() {
    setUploadedFileName(null)
    setProtocolText('')
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  function protocolUploadErrorMessage(err) {
    const code = err?.code
    if (code === 'FILE_TYPE_UNSUPPORTED') return t('admin.extract.uploadTypeError')
    if (code === 'FILE_TOO_LARGE') return t('admin.extract.uploadTooLarge')
    if (code === 'FILE_NO_TEXT') return t('admin.extract.uploadNoText')
    if (code === 'FILE_READ_FAILED') return t('admin.extract.uploadReadError')
    return err.message ?? t('admin.extract.error')
  }

  async function handleProtocolUploadChange(event) {
    const file = event.target.files?.[0]
    if (!file || extracting || saving || uploading) return

    setError(null)
    setUploading(true)
    try {
      const uploaded = await uploadExtractSource(file)
      setProtocolText(uploaded.text ?? '')
      setUploadedFileName(uploaded.filename || file.name)
    } catch (err) {
      clearUploadedFile()
      setError(protocolUploadErrorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  function applyExtractedFields(fields) {
    setValues((current) => {
      const next = { ...current }
      for (const column of columns) {
        if (lockedSet.has(column) && column !== 'category_3r') continue
        if (!(column in fields)) continue
        const value = fields[column]
        if (value === null || value === undefined) continue
        if (typeof value === 'string' && value.trim() === '') continue
        if (Array.isArray(value) && value.length === 0) continue
        const draft = toDraft(value)
        if (draftsEqual(draft, current[column])) continue
        next[column] = draft
      }
      return withDerivedCategory3r(next, columns)
    })
  }

  async function extractFromProtocol(event) {
    event?.preventDefault?.()
    if (extracting || saving || uploading) return
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
      applyExtractedFields(result.fields ?? {})
    } catch (err) {
      setError(err.message ?? t('admin.extract.methodDraftError'))
    } finally {
      setExtracting(false)
    }
  }

  function documentExtractErrorMessage(err) {
    const code = err?.code
    if (code === 'INVALID_URL') return t('admin.extract.urlInvalid')
    if (code === 'URL_FETCH_FAILED') return t('admin.extract.urlFetchFailed')
    if (code === 'URL_NO_TEXT') return t('admin.extract.urlNoText')
    return err.message ?? t('admin.extract.documentDraftError')
  }

  async function extractFromDocument(event) {
    event?.preventDefault?.()
    if (extracting || saving || uploading) return
    const trimmed = protocolText.trim()
    const looksLikeUrl =
      /^(https?:\/\/|www\.)/i.test(trimmed) && !/\s/.test(trimmed)
    if (!looksLikeUrl && trimmed.length < POLICY_TEXT_MIN) {
      setError(t('admin.extract.tooShort', { min: POLICY_TEXT_MIN }))
      return
    }

    setExtracting(true)
    setError(null)
    try {
      const categoryHint = parseMultiSelectDraft(values.categories)[0]
      const result = await extractDocumentDraft({
        text: trimmed,
        lang: currentLanguage(),
        ...(categoryHint ? { categoryHint } : {}),
      })
      applyExtractedFields(result.fields ?? {})
    } catch (err) {
      setError(documentExtractErrorMessage(err))
    } finally {
      setExtracting(false)
    }
  }

  function regulationExtractErrorMessage(err) {
    const code = err?.code
    if (code === 'INVALID_URL') return t('admin.extract.urlInvalid')
    if (code === 'URL_FETCH_FAILED') return t('admin.extract.urlFetchFailed')
    if (code === 'URL_NO_TEXT') return t('admin.extract.urlNoText')
    return err.message ?? t('admin.extract.regulationDraftError')
  }

  async function extractFromRegulation(event) {
    event?.preventDefault?.()
    if (extracting || saving || uploading) return
    const trimmed = protocolText.trim()
    const looksLikeUrl =
      /^(https?:\/\/|www\.)/i.test(trimmed) && !/\s/.test(trimmed)
    if (!looksLikeUrl && trimmed.length < POLICY_TEXT_MIN) {
      setError(t('admin.extract.tooShort', { min: POLICY_TEXT_MIN }))
      return
    }

    setExtracting(true)
    setError(null)
    try {
      const result = await extractRegulationDraft({
        text: trimmed,
        lang: currentLanguage(),
      })
      applyExtractedFields(result.fields ?? {})
    } catch (err) {
      setError(regulationExtractErrorMessage(err))
    } finally {
      setExtracting(false)
    }
  }

  async function submit() {
    if (saving || extracting || uploading) return

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
  const protocolBusy = extracting || saving || uploading
  const protocolTextLocked = Boolean(uploadedFileName)
  const sourceLooksLikeUrl =
    /^(https?:\/\/|www\.)/i.test(protocolText.trim()) &&
    !/\s/.test(protocolText.trim())
  const canExtract =
    sourceAssist &&
    !protocolBusy &&
    ((documentAssist || regulationAssist)
      ? sourceLooksLikeUrl || protocolTrimmedLength >= POLICY_TEXT_MIN
      : protocolTrimmedLength >= POLICY_TEXT_MIN)
  const nestedDocumentColumns =
    nestedDocumentSchema?.columns.filter(
      (column) => !(nestedDocumentSchema.auto_columns ?? []).includes(column),
    ) ?? []
  const sourceTextId = documentAssist
    ? 'document-source-text'
    : regulationAssist
      ? 'regulation-source-text'
      : 'method-protocol-text'
  const onExtractSubmit = documentAssist
    ? extractFromDocument
    : regulationAssist
      ? extractFromRegulation
      : extractFromProtocol
  const sourceLabel = documentAssist
    ? t('admin.extract.documentSourceLabel')
    : regulationAssist
      ? t('admin.extract.regulationSourceLabel')
      : t('admin.extract.methodProtocolLabel')
  const sourcePlaceholder = protocolTextLocked
    ? t('admin.extract.uploadPlaceholder')
    : documentAssist
      ? t('admin.extract.documentSourcePlaceholder')
      : regulationAssist
        ? t('admin.extract.regulationSourcePlaceholder')
        : t('admin.extract.methodProtocolPlaceholder')
  const sourceHint = documentAssist
    ? t('admin.extract.documentSourceHint')
    : regulationAssist
      ? t('admin.extract.regulationSourceHint')
      : t('admin.extract.methodProtocolHint')

  return (
    <>
    <div
      className={`fixed inset-0 ${overlayClassName} flex items-center justify-center bg-on-surface/40 px-container-padding py-section-gap`}
      role="presentation"
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
            disabled={protocolBusy}
            onClick={onClose}
          />
        </div>

        {error && (
          <p className="mb-card-gap font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        )}

        <div className="min-h-0 flex-1 space-y-card-gap overflow-y-auto pr-1">
          {sourceAssist ? (
            <form
              onSubmit={onExtractSubmit}
              className="space-y-2 border-b border-border-subtle pb-card-gap"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <label
                  htmlFor={sourceTextId}
                  className="block font-label-caps text-label-caps uppercase text-on-surface-variant"
                >
                  {sourceLabel}
                </label>
                <div className="flex flex-wrap items-center gap-2">
                  {uploadedFileName ? (
                    <span className="inline-flex max-w-[16rem] items-center gap-2 rounded-md border border-border-subtle bg-surface-container-low px-2 py-1 font-metadata text-metadata text-on-surface">
                      <span className="truncate" title={uploadedFileName}>
                        {uploadedFileName}
                      </span>
                      <button
                        type="button"
                        disabled={protocolBusy}
                        onClick={clearUploadedFile}
                        className="shrink-0 text-on-secondary-container transition-colors hover:text-error disabled:opacity-50"
                        title={t('admin.extract.clearUpload')}
                        aria-label={t('admin.extract.clearUpload')}
                      >
                        ×
                      </button>
                    </span>
                  ) : null}
                  <input
                    ref={fileInputRef}
                    id={uploadInputId}
                    type="file"
                    accept=".pdf,.html,.htm,.txt,application/pdf,text/html,text/plain"
                    className="sr-only"
                    disabled={protocolBusy}
                    onChange={handleProtocolUploadChange}
                  />
                  <label
                    htmlFor={uploadInputId}
                    className={`inline-flex cursor-pointer items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-3 py-1.5 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container ${
                      protocolBusy ? 'pointer-events-none opacity-50' : ''
                    }`}
                  >
                    {uploading
                      ? t('admin.extract.uploading')
                      : t('admin.extract.upload')}
                  </label>
                </div>
              </div>
              <textarea
                id={sourceTextId}
                rows={6}
                value={protocolText}
                disabled={protocolBusy || protocolTextLocked}
                readOnly={protocolTextLocked}
                onChange={(event) => setProtocolText(event.target.value)}
                placeholder={sourcePlaceholder}
                className="w-full rounded border border-border-subtle bg-surface-container-lowest px-3 py-2 font-metadata text-metadata text-on-surface outline-none focus:border-primary disabled:cursor-not-allowed disabled:opacity-60"
              />
              <p className="font-metadata text-metadata text-on-secondary-container opacity-65">
                {sourceHint}
              </p>
              {protocolTrimmedLength > 0 &&
              !sourceLooksLikeUrl &&
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
            const options = fieldOptions?.[column] ?? []
            const foreignKey = foreignKeys?.[column]
            const useSelect = options.length > 0
            const useMultiSelect = isMultiSelectColumn(column, type, options)
            const useBooleanSelect = !useSelect && isBooleanColumnType(type)
            const autoFocus = !sourceAssist && index === firstEditableIndex
            const labelId = `row-field-${column}-label`
            const fieldId = `row-field-${column}`
            const selectedValues = useMultiSelect
              ? parseMultiSelectDraft(values[column])
              : []
            const canAddDocument =
              column === 'source_doc_id' && foreignKey?.table === 'documents'
            const showOriginal =
              showOriginalValues &&
              !draftsEqual(values[column], originalValues[column])
            const booleanDraft = useBooleanSelect
              ? normalizeBooleanDraft(values[column])
              : ''

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
                              disabled={protocolBusy || locked}
                              autoFocus={autoFocus && optionIndex === 0}
                              onChange={() => toggleMultiOption(optionValue)}
                              className="h-4 w-4 shrink-0 rounded border-border-subtle text-primary accent-primary"
                            />
                            {option.label}
                          </label>
                        )
                      })}
                    </div>
                  ) : useBooleanSelect ? (
                    <select
                      id={fieldId}
                      autoFocus={autoFocus}
                      value={booleanDraft}
                      disabled={protocolBusy || locked}
                      required={required}
                      onChange={(event) => updateValue(column, event.target.value)}
                      className={fieldClass}
                    >
                      <option value="">
                        {required
                          ? t('admin.selectRequired')
                          : t('admin.selectOptional')}
                      </option>
                      <option value="true">{t('admin.booleanTrue')}</option>
                      <option value="false">{t('admin.booleanFalse')}</option>
                    </select>
                  ) : useSelect ? (
                    <select
                      id={fieldId}
                      autoFocus={autoFocus}
                      value={values[column] ?? ''}
                      disabled={protocolBusy || locked}
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
                      disabled={protocolBusy || locked}
                      required={required}
                      onChange={(event) => updateValue(column, event.target.value)}
                      className={fieldClass}
                    />
                  )}
                  {showOriginal ? (
                    <button
                      type="button"
                      disabled={protocolBusy || locked}
                      onClick={() => updateValue(column, originalValues[column] ?? '')}
                      title={t('admin.restoreOriginal')}
                      className="mt-1 block max-w-full text-left whitespace-pre-wrap break-words font-metadata text-metadata text-on-secondary-container underline decoration-dotted underline-offset-2 opacity-70 transition-opacity hover:opacity-100 disabled:cursor-not-allowed disabled:no-underline disabled:opacity-40"
                    >
                      {t('admin.originalValue', {
                        value: formatOriginalDraft(originalValues[column]),
                      })}
                    </button>
                  ) : null}
                    {canAddDocument ? (
                      <div className="mt-2 flex flex-wrap items-center gap-3">
                        <button
                          type="button"
                          disabled={
                            protocolBusy ||
                            locked ||
                            nestedDocumentLoading ||
                            nestedDocumentOpen
                          }
                          onClick={openNestedDocument}
                          className="inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-3 py-1.5 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {nestedDocumentLoading
                            ? t('admin.loading')
                            : t('admin.extract.addNewDocument')}
                        </button>
                        {nestedDocumentError ? (
                          <p
                            className="font-metadata text-metadata text-error"
                            role="alert"
                          >
                            {nestedDocumentError}
                          </p>
                        ) : null}
                      </div>
                    ) : null}
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
            disabled={protocolBusy}
            onClick={submit}
            className="font-metadata text-metadata text-primary hover:underline disabled:opacity-40"
          >
            {saving ? t('admin.saving') : t('admin.ok')}
          </button>
          <button
            type="button"
            disabled={protocolBusy}
            onClick={onClose}
            className="font-metadata text-metadata text-on-secondary-container hover:underline disabled:opacity-40"
          >
            {t('admin.cancel')}
          </button>
        </div>
      </div>
    </div>
    {nestedDocumentOpen && nestedDocumentSchema
      ? createPortal(
          <AddRowModal
            key="nested-add-document"
            table="documents"
            columns={nestedDocumentColumns}
            comments={nestedDocumentSchema.column_comments}
            types={nestedDocumentSchema.column_types}
            requiredColumns={nestedDocumentSchema.required_columns}
            foreignKeys={nestedDocumentSchema.foreign_keys}
            columnOptions={nestedDocumentSchema.column_options}
            mode="create"
            title={t('admin.extract.addDocument')}
            initialValues={documentInitialValues}
            overlayClassName="z-[60]"
            onClose={() => setNestedDocumentOpen(false)}
            onSaved={handleNestedDocumentSaved}
          />,
          document.body,
        )
      : null}
    </>
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
  const [sortBy, setSortBy] = useState(null)
  const [sortDir, setSortDir] = useState('asc')

  function tableFetchOpts({ limit = PAGE_SIZE, offset = 0 } = {}) {
    return {
      limit,
      offset,
      ...(sortBy ? { sortBy, sortDir } : {}),
    }
  }

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
      setActiveTable((current) => {
        if (current !== fromHash) {
          setPage(0)
          setSortBy(null)
          setSortDir('asc')
        }
        return fromHash
      })
      return
    }

    setActiveTable((current) => current ?? tables[0])
  }, [tables, location.hash])

  function selectTable(table) {
    setActiveTable(table)
    setPage(0)
    setSortBy(null)
    setSortDir('asc')
    setEdit(null)
    setSelected({})
    setConfirmDelete(false)
    setCommentColumn(null)
    setRowModal(null)
    navigate(`/admin/database#${table}`, { replace: true })
  }

  function toggleSort(column) {
    if (saving || deleting || exporting || loadingData) return
    setPage(0)
    setSelected({})
    setConfirmDelete(false)
    setEdit(null)
    if (sortBy === column) {
      setSortDir((current) => (current === 'asc' ? 'desc' : 'asc'))
      return
    }
    setSortBy(column)
    setSortDir('asc')
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
        const result = await fetchAdminTable(
          activeTable,
          tableFetchOpts({
            limit: PAGE_SIZE,
            offset: page * PAGE_SIZE,
          }),
        )
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
  }, [activeTable, page, sortBy, sortDir, t])

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
        const result = await fetchAdminTable(
          activeTable,
          tableFetchOpts({
            limit: EXPORT_PAGE_SIZE,
            offset,
          }),
        )
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
        const refreshed = await fetchAdminTable(
          activeTable,
          tableFetchOpts({
            limit: PAGE_SIZE,
            offset: page * PAGE_SIZE,
          }),
        )
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
      value = fromDraft(
        edit.draft,
        edit.original,
        tableData?.column_types?.[edit.column],
      )
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
                              const isSorted = sortBy === column
                              const sortLabel = isSorted
                                ? sortDir === 'asc'
                                  ? t('admin.sortAscending')
                                  : t('admin.sortDescending')
                                : t('admin.sortByColumn', { column })
                              return (
                                <th
                                  key={column}
                                  className="whitespace-nowrap px-3 py-2 font-label-caps text-label-caps uppercase text-on-surface-variant"
                                  aria-sort={
                                    isSorted
                                      ? sortDir === 'asc'
                                        ? 'ascending'
                                        : 'descending'
                                      : 'none'
                                  }
                                >
                                  <span className="inline-flex items-center gap-0.5">
                                    <button
                                      type="button"
                                      onClick={() => toggleSort(column)}
                                      disabled={saving || deleting || exporting || loadingData}
                                      title={sortLabel}
                                      aria-label={sortLabel}
                                      className="inline-flex items-center gap-1 rounded px-0.5 py-0.5 transition-colors hover:text-primary disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                      <span>{column}</span>
                                      {isSorted ? (
                                        <span aria-hidden="true" className="font-metadata text-metadata normal-case text-primary">
                                          {sortDir === 'asc' ? '↑' : '↓'}
                                        </span>
                                      ) : null}
                                    </button>
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
                                  const columnType = tableData.column_types?.[column]
                                  const useBooleanSelect =
                                    isEditing && isBooleanColumnType(columnType)
                                  const useTextarea =
                                    isEditing &&
                                    !useBooleanSelect &&
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
                                          {useBooleanSelect ? (
                                            <select
                                              autoFocus
                                              value={normalizeBooleanDraft(edit.draft)}
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
                                            >
                                              <option value="">
                                                {t('admin.selectOptional')}
                                              </option>
                                              <option value="true">
                                                {t('admin.booleanTrue')}
                                              </option>
                                              <option value="false">
                                                {t('admin.booleanFalse')}
                                              </option>
                                            </select>
                                          ) : useTextarea ? (
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
                    const refreshed = await fetchAdminTable(
                      activeTable,
                      tableFetchOpts({ limit: PAGE_SIZE, offset: 0 }),
                    )
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
                  const refreshed = await fetchAdminTable(
                    activeTable,
                    tableFetchOpts({
                      limit: PAGE_SIZE,
                      offset: page * PAGE_SIZE,
                    }),
                  )
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

function SettingsPanel() {
  const { t } = useTranslation()
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchAdminSettings()
      .then((data) => {
        if (!cancelled) setSettings(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message || t('admin.settings.error'))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [t])

  if (loading) {
    return (
      <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('admin.settings.loading')}
      </p>
    )
  }

  if (error || !settings) {
    return (
      <p className="font-body-base text-body-base text-error">
        {error || t('admin.settings.error')}
      </p>
    )
  }

  const rows = [
    { key: 'environment', label: t('admin.settings.environment'), value: settings.app_env },
    { key: 'modelName', label: t('admin.settings.modelName'), value: settings.llm_model },
  ]

  return (
    <dl className="divide-y divide-border-subtle rounded-lg border border-border-subtle bg-surface-container-lowest">
      {rows.map((row) => (
        <div
          key={row.key}
          className="flex flex-col gap-1 px-container-padding py-3 sm:flex-row sm:items-baseline sm:justify-between sm:gap-4"
        >
          <dt className="font-label-caps text-label-caps uppercase text-on-surface-variant">
            {row.label}
          </dt>
          <dd className="font-monospace-data text-monospace-data text-on-surface sm:text-right">
            {row.value || '—'}
          </dd>
        </div>
      ))}
    </dl>
  )
}

function ProjectDocModal({ doc, onClose, closeLabel }) {
  const titleId = useId()

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])

  if (!doc) return null

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 px-container-padding py-section-gap"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="flex max-h-[min(90vh,56rem)] w-full max-w-3xl flex-col overflow-hidden rounded-lg border border-border-subtle bg-surface-container-lowest shadow-lg"
      >
        <div className="flex shrink-0 items-start justify-between gap-3 border-b border-border-subtle px-container-padding py-3">
          <h3
            id={titleId}
            className="font-card-title text-card-title text-primary"
          >
            {doc.filename}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="-mr-1 -mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded text-2xl leading-none text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
            aria-label={closeLabel}
          >
            ×
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-container-padding py-card-gap">
          <MarkdownRenderer>{doc.content}</MarkdownRenderer>
        </div>
      </div>
    </div>,
    document.body,
  )
}

function DocsPanel() {
  const { t } = useTranslation()
  const [openDocId, setOpenDocId] = useState(null)
  const openDoc = PROJECT_DOCS.find((doc) => doc.id === openDocId) ?? null

  if (PROJECT_DOCS.length === 0) {
    return (
      <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('admin.docs.empty')}
      </p>
    )
  }

  return (
    <>
      <ul className="divide-y divide-border-subtle rounded-lg border border-border-subtle bg-surface-container-lowest">
        {PROJECT_DOCS.map((doc) => (
          <li key={doc.id}>
            <button
              type="button"
              onClick={() => setOpenDocId(doc.id)}
              className="flex w-full items-center px-container-padding py-3 text-left transition-colors hover:bg-surface-container-low"
            >
              <span className="min-w-0 flex-1 font-body-base text-body-base text-primary">
                {doc.filename}
              </span>
            </button>
          </li>
        ))}
      </ul>
      {openDoc ? (
        <ProjectDocModal
          doc={openDoc}
          onClose={() => setOpenDocId(null)}
          closeLabel={t('admin.docs.close')}
        />
      ) : null}
    </>
  )
}

const POLICY_TEXT_MIN = 20
const POLICY_TEXT_MAX = 50000
const EXTRACT_HISTORY_KEY = '3r_assist.extract.history'
const EXTRACT_HISTORY_MAX = 20

function looksLikeDocumentUrl(value) {
  const candidate = String(value ?? '').trim()
  if (!candidate || /\s/.test(candidate)) return false
  try {
    const withScheme = /^https?:\/\//i.test(candidate)
      ? candidate
      : candidate.toLowerCase().startsWith('www.')
        ? `https://${candidate}`
        : null
    if (!withScheme) return false
    const parsed = new URL(withScheme)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function normalizeDocumentUrl(value) {
  const candidate = String(value ?? '').trim()
  if (!looksLikeDocumentUrl(candidate)) return ''
  return /^https?:\/\//i.test(candidate) ? candidate : `https://${candidate}`
}

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
  if (entry?.kind === 'document') {
    const citation = entry?.documentFields?.doc_citation
    const localized =
      citation && typeof citation === 'object'
        ? citation['en-us'] || citation['pt-br']
        : null
    if (localized?.trim()) return localized.trim()
  }
  const name = entry?.result?.document_name?.trim()
  if (name) return name
  const preview = entry?.text?.trim()?.slice(0, 48)
  if (preview) return preview.length < entry.text.trim().length ? `${preview}…` : preview
  return entry?.savedAt ?? '—'
}

function oecdTgNumberFromRef(ref) {
  if (!ref) return null
  const match = String(ref).match(/\b(?:OECD\s+)?TG\s*(\d{3,4}[A-Z]?)\b/i)
  return match?.[1]?.toUpperCase() ?? null
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

const DOCUMENT_TYPE_OPTIONS = [
  { value: 'regulation', labelKey: 'admin.extract.documentType.regulation' },
  { value: 'method_protocol', labelKey: 'admin.extract.documentType.protocol' },
  { value: 'guideline', labelKey: 'admin.extract.documentType.guideline' },
  { value: 'other', labelKey: 'admin.extract.documentType.other' },
]

function isPolicyExtractionType(documentType) {
  return !documentType || documentType === 'regulation'
}

function documentInitialValuesFromExtracted({
  documentName,
  documentDate,
  url,
  categories,
  category,
  institution,
  slug,
  docCitation,
  description,
} = {}) {
  const citation = documentName?.trim() ?? ''
  const citationValue =
    docCitation && typeof docCitation === 'object'
      ? docCitation
      : { 'en-us': citation, 'pt-br': citation }
  const descriptionValue =
    description && typeof description === 'object'
      ? description
      : {
          'en-us': typeof description === 'string' ? description.trim() : '',
          'pt-br': typeof description === 'string' ? description.trim() : '',
        }
  const institutionValue =
    institution && typeof institution === 'object'
      ? institution
      : institution
        ? {
            'en-us': String(institution).trim(),
            'pt-br': String(institution).trim(),
          }
        : { 'en-us': '', 'pt-br': '' }
  const categoryList = Array.isArray(categories)
    ? categories.filter(Boolean)
    : category
      ? [category]
      : ['regulation']
  return {
    slug: slug || slugifyMethodDraft(citation || citationValue['en-us']),
    doc_citation: citationValue,
    description: descriptionValue,
    date: regulationDateFromDocument(documentDate),
    categories: categoryList,
    institution: institutionValue,
    url: url?.trim() ?? '',
  }
}

function documentInitialValuesFromDraftFields(fields, { categoryHint, sourceUrl } = {}) {
  return documentInitialValuesFromExtracted({
    slug: fields?.slug,
    documentDate: fields?.date,
    url: fields?.url || sourceUrl || '',
    categories: fields?.categories?.length
      ? fields.categories
      : fields?.category
        ? [fields.category]
        : categoryHint
          ? [categoryHint]
          : ['other'],
    institution: fields?.institution,
    docCitation: fields?.doc_citation,
    description: fields?.description,
  })
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

function ExtractedMethodRow({
  method,
  documentDate,
  institution,
  documentName,
  documentUrl,
  documentType,
  documentDescription,
}) {
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
  const [editMethodSchema, setEditMethodSchema] = useState(null)
  const [editMethodRow, setEditMethodRow] = useState(null)
  const [editMethodOpen, setEditMethodOpen] = useState(false)
  const [editMethodLoadingId, setEditMethodLoadingId] = useState(null)
  const [editMethodError, setEditMethodError] = useState(null)

  async function toggle() {
    const next = !open
    setOpen(next)
    if (!next || loading) return

    setLoading(true)
    setError(null)
    setMatchResult(null)
    setAddMethodError(null)
    setAddRegulationError(null)
    setEditMethodError(null)
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

  async function refreshMatches() {
    setLoading(true)
    setError(null)
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
    if (addMethodLoading || addRegulationLoading || editMethodLoadingId != null) return
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
    if (addRegulationLoading || addMethodLoading || editMethodLoadingId != null) return
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

  async function openEditMethod(dbMethod) {
    if (
      editMethodLoadingId != null ||
      addMethodLoading ||
      addRegulationLoading ||
      !dbMethod?.id
    ) {
      return
    }
    setEditMethodError(null)
    setEditMethodLoadingId(dbMethod.id)
    try {
      const { schema, row } = await fetchAdminRowById('methods', dbMethod.id)
      setEditMethodSchema(schema)
      setEditMethodRow(row)
      setEditMethodOpen(true)
    } catch {
      setEditMethodError(t('admin.extract.editMethodError'))
    } finally {
      setEditMethodLoadingId(null)
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
  const editMethodColumns =
    editMethodSchema?.columns.filter(
      (column) => !(editMethodSchema.auto_columns ?? []).includes(column),
    ) ?? []
  const editMethodPrimaryKey = editMethodSchema?.primary_key ?? []
  const rowActionsBusy =
    addMethodLoading || addRegulationLoading || editMethodLoadingId != null

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
                      const contexts = dbMethod.regulatory_contexts ?? []
                      const protocolCitation = methodSourceCitation(
                        dbMethod,
                        lang,
                      )
                      return (
                        <li key={`${candidate.match_kind}-${dbMethod.id}`}>
                          <ResultCard
                            type={primaryThreeR(dbMethod)}
                            badges={methodThreeRBadges(dbMethod, t, lang)}
                            title={methodDisplayName(dbMethod, lang)}
                            titleExtra={
                              <span className="ml-2 inline-flex items-center gap-1 align-middle">
                                <span className="font-metadata text-metadata font-normal text-on-surface-variant">
                                  ({dbMethod.slug})
                                </span>
                                <EditIconButton
                                  label={t('admin.edit')}
                                  disabled={rowActionsBusy}
                                  onClick={() => openEditMethod(dbMethod)}
                                />
                              </span>
                            }
                            headerMeta={
                              <p className="mt-1 font-metadata text-metadata text-on-surface-variant">
                                {dbMethod.active
                                  ? t('admin.extract.active')
                                  : t('admin.extract.inactive')}
                                {' · '}
                                {candidate.match_kind === 'oecd_ref'
                                  ? t('admin.extract.matchByOecd')
                                  : t('admin.extract.matchByText')}
                              </p>
                            }
                            score={scorePercent(candidate.score)}
                            matchLabel={t('s3.matchLabel')}
                            dimmed={!dbMethod.active}
                            validationStatus={
                              dbMethod.validation_status
                                ? t(
                                    `s3.validationStatus.${dbMethod.validation_status}`,
                                  )
                                : null
                            }
                            regulatoryStatuses={formatRegulatoryStatusItems(
                              contexts,
                              lang,
                              t,
                            )}
                            purposeLabel={t('s3.purposeLabel')}
                            regulationStatusLabel={t(
                              's3.regulationStatusLabel',
                            )}
                            validationStatusLabel={t(
                              's3.validationStatusLabel',
                            )}
                            approvedJurisdictionsLabel={t(
                              's3.approvedJurisdictionsLabel',
                            )}
                            description={methodDescription(dbMethod, lang)}
                            detailRows={methodDetailRows(dbMethod, t)}
                            protocolCitation={protocolCitation}
                            noCitationLabel={t('s3.noProtocolCitation')}
                            noRegulatoryCitationLabel={t(
                              's3.noRegulatoryCitation',
                            )}
                            primaryUrl={dbMethod.source_url || null}
                            sourcesLabel={t('s3.sourceLink')}
                            referenceLabel={t('s3.referenceLabel')}
                            regulatoryLinkLabel={t('s3.regulatoryLink')}
                            closeLabel={t('s3.close')}
                          />
                        </li>
                      )
                    })}
                  </ul>
                )}
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    disabled={rowActionsBusy}
                    onClick={openAddRegulation}
                    className="order-1 inline-flex items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {addRegulationLoading
                      ? t('admin.loading')
                      : t('admin.extract.addRegulation')}
                  </button>
                  <button
                    type="button"
                    disabled={rowActionsBusy}
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
                {editMethodError ? (
                  <p
                    className="font-metadata text-metadata text-error"
                    role="alert"
                  >
                    {editMethodError}
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
              documentInitialValues={documentInitialValuesFromExtracted({
                documentName,
                documentDate,
                url: documentUrl,
                category: documentType,
                institution,
                description: documentDescription,
              })}
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
      {editMethodOpen && editMethodSchema && editMethodRow
        ? createPortal(
            <AddRowModal
              key={`extract-edit-method-${editMethodRow.id}`}
              table="methods"
              columns={editMethodColumns}
              comments={editMethodSchema.column_comments}
              types={editMethodSchema.column_types}
              requiredColumns={editMethodSchema.required_columns}
              foreignKeys={editMethodSchema.foreign_keys}
              columnOptions={editMethodSchema.column_options}
              mode="edit"
              title={t('admin.editRow')}
              initialValues={editMethodRow}
              lockedColumns={editMethodPrimaryKey}
              primaryKey={primaryKeyValues(editMethodRow, editMethodPrimaryKey)}
              onClose={() => {
                setEditMethodOpen(false)
                setEditMethodRow(null)
              }}
              onSaved={async () => {
                setEditMethodOpen(false)
                setEditMethodRow(null)
                await refreshMatches()
              }}
            />,
            document.body,
          )
        : null}
    </>
  )
}

function formatUsd(amount) {
  const value = Number(amount)
  if (!Number.isFinite(value)) return '$0.00'
  if (value === 0) return '$0.00'
  if (value < 0.01) return `$${value.toFixed(4)}`
  return `$${value.toFixed(3)}`
}

function ExtractPanel() {
  const { t, i18n } = useTranslation()
  const [text, setText] = useState('')
  const [submitPhase, setSubmitPhase] = useState(null)
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
  const [editDocumentSchema, setEditDocumentSchema] = useState(null)
  const [editDocumentRow, setEditDocumentRow] = useState(null)
  const [editDocumentOpen, setEditDocumentOpen] = useState(false)
  const [editDocumentLoadingId, setEditDocumentLoadingId] = useState(null)
  const [editDocumentError, setEditDocumentError] = useState(null)
  const [documentDraftValues, setDocumentDraftValues] = useState(null)
  const [history, setHistory] = useState(() => readExtractHistory())
  const [activeHistoryId, setActiveHistoryId] = useState(null)
  const [documentType, setDocumentType] = useState('')
  const [costEstimate, setCostEstimate] = useState(null)
  const [readyToProceed, setReadyToProceed] = useState(false)
  const [resolvedSourceText, setResolvedSourceText] = useState(null)
  const [resolvedSourceUrl, setResolvedSourceUrl] = useState('')
  const [uploadedFileName, setUploadedFileName] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)
  const uploadInputId = useId()
  const submitAbortRef = useRef(null)

  useEffect(() => {
    if (!submitPhase) {
      setElapsedSeconds(0)
      return undefined
    }

    setElapsedSeconds(0)
    const startedAt = Date.now()
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000))
    }, 250)

    return () => window.clearInterval(timer)
  }, [submitPhase])

  useEffect(() => {
    return () => {
      submitAbortRef.current?.abort()
    }
  }, [])

  const trimmedLength = text.trim().length
  const inputIsUrl = !uploadedFileName && looksLikeDocumentUrl(text)
  const busy =
    submitPhase != null ||
    addDocumentLoading ||
    editDocumentLoadingId != null ||
    uploading
  const textLocked = Boolean(uploadedFileName)
  const canSubmit =
    (inputIsUrl || trimmedLength >= POLICY_TEXT_MIN) &&
    (!busy || submitPhase != null)
  const dateLocale = i18n.language?.startsWith('pt') ? 'pt-BR' : 'en-US'

  function clearCostEstimate() {
    setCostEstimate(null)
    setReadyToProceed(false)
    setResolvedSourceText(null)
    setResolvedSourceUrl('')
  }

  function cancelSubmit() {
    submitAbortRef.current?.abort()
  }

  function clearUploadedFile() {
    setUploadedFileName(null)
    setText('')
    clearCostEstimate()
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

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
    setUploadedFileName(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    setText(entry.text ?? '')
    setDocumentType(entry.documentType ?? '')
    setDocumentUrl(
      entry.result?.url
        || (looksLikeDocumentUrl(entry.text) ? normalizeDocumentUrl(entry.text) : '')
        || entry.documentFields?.url
        || '',
    )
    clearDocumentSearch()
    setAddDocumentError(null)
    clearCostEstimate()
    setActiveHistoryId(entry.id)

    if (entry.kind === 'document') {
      setResult(null)
      void openDocumentDraftForm(
        documentInitialValuesFromDraftFields(entry.documentFields, {
          categoryHint: entry.documentType,
          sourceUrl: looksLikeDocumentUrl(entry.text)
            ? normalizeDocumentUrl(entry.text)
            : '',
        }),
      )
      return
    }

    setDocumentDraftValues(null)
    setAddDocumentOpen(false)
    setResult(entry.result ?? null)
  }

  async function openDocumentDraftForm(initialValues) {
    setAddDocumentError(null)
    setAddDocumentLoading(true)
    try {
      const schema = await fetchAdminTable('documents', { limit: 1, offset: 0 })
      setAddDocumentSchema(schema)
      setDocumentDraftValues(initialValues)
      setAddDocumentOpen(true)
    } catch {
      setAddDocumentError(t('admin.extract.addDocumentError'))
    } finally {
      setAddDocumentLoading(false)
    }
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
    if (addDocumentLoading || editDocumentLoadingId != null || !result) return
    setAddDocumentError(null)
    setAddDocumentLoading(true)
    try {
      const schema = await fetchAdminTable('documents', { limit: 1, offset: 0 })
      setAddDocumentSchema(schema)
      setDocumentDraftValues(
        documentInitialValuesFromExtracted({
          documentName: result.document_name,
          documentDate: result.document_date,
          url: documentUrl,
          category: documentType || 'regulation',
          institution: result.responsible_institution,
          description: result.description,
        }),
      )
      setAddDocumentOpen(true)
    } catch {
      setAddDocumentError(t('admin.extract.addDocumentError'))
    } finally {
      setAddDocumentLoading(false)
    }
  }

  async function openEditDocument(doc) {
    if (
      editDocumentLoadingId != null ||
      addDocumentLoading ||
      !doc?.id
    ) {
      return
    }
    setEditDocumentError(null)
    setEditDocumentLoadingId(doc.id)
    try {
      const { schema, row } = await fetchAdminRowById('documents', doc.id)
      setEditDocumentSchema(schema)
      setEditDocumentRow(row)
      setEditDocumentOpen(true)
    } catch {
      setEditDocumentError(t('admin.extract.editDocumentError'))
    } finally {
      setEditDocumentLoadingId(null)
    }
  }

  function removeHistoryEntry(entryId) {
    const next = history.filter((entry) => entry.id !== entryId)
    persistHistory(next)
    if (activeHistoryId === entryId) {
      setActiveHistoryId(null)
    }
  }

  function extractionErrorMessage(err) {
    const code = err?.code
    if (code === 'ABORTED' || err?.name === 'AbortError') {
      return t('admin.extract.cancelled')
    }
    if (code === 'INVALID_URL') return t('admin.extract.urlInvalid')
    if (code === 'URL_FETCH_FAILED') return t('admin.extract.urlFetchFailed')
    if (code === 'URL_NO_TEXT') return t('admin.extract.urlNoText')
    if (code === 'FILE_TYPE_UNSUPPORTED') return t('admin.extract.uploadTypeError')
    if (code === 'FILE_TOO_LARGE') return t('admin.extract.uploadTooLarge')
    if (code === 'FILE_NO_TEXT') return t('admin.extract.uploadNoText')
    if (code === 'FILE_READ_FAILED') return t('admin.extract.uploadReadError')
    return err.message ?? t('admin.extract.error')
  }

  async function runCostEstimate({
    workingText,
    workingUrl = '',
    type = documentType,
    signal,
  }) {
    const policyMode = isPolicyExtractionType(type)
    setSubmitPhase('estimating')
    const estimate = await estimateExtract({
      text: workingText,
      lang: currentLanguage(),
      mode: policyMode ? 'policy' : 'document',
      categoryHint: policyMode ? undefined : type,
      sourceUrl: workingUrl || undefined,
      signal,
    })
    setCostEstimate(estimate)
    setReadyToProceed(true)
    return estimate
  }

  async function estimateUploadedText(sourceText, type = documentType) {
    const trimmed = sourceText.trim()
    if (trimmed.length < POLICY_TEXT_MIN) return

    cancelSubmit()
    const controller = new AbortController()
    submitAbortRef.current = controller
    setError(null)
    clearCostEstimate()

    try {
      await runCostEstimate({
        workingText: trimmed,
        type,
        signal: controller.signal,
      })
    } catch (err) {
      clearCostEstimate()
      if (err?.code !== 'ABORTED' && err?.name !== 'AbortError') {
        setError(extractionErrorMessage(err))
      } else {
        setError(null)
      }
    } finally {
      if (submitAbortRef.current === controller) {
        submitAbortRef.current = null
      }
      setSubmitPhase(null)
    }
  }

  async function handleUploadChange(event) {
    const file = event.target.files?.[0]
    if (!file || busy) return

    setError(null)
    setUploading(true)
    clearCostEstimate()
    try {
      const uploaded = await uploadExtractSource(file)
      const uploadedText = uploaded.text ?? ''
      setText(uploadedText)
      setUploadedFileName(uploaded.filename || file.name)
      setResult(null)
      setDocumentUrl('')
      clearDocumentSearch()
      setUploading(false)
      await estimateUploadedText(uploadedText, documentType)
    } catch (err) {
      clearUploadedFile()
      setError(extractionErrorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  async function handleDocumentTypeChange(event) {
    const nextType = event.target.value
    setDocumentType(nextType)
    clearCostEstimate()
    if (uploadedFileName && text.trim().length >= POLICY_TEXT_MIN && !busy) {
      await estimateUploadedText(text, nextType)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (submitPhase) {
      cancelSubmit()
      return
    }
    if (!canSubmit) return

    setError(null)
    const sourceText = text.trim()
    const sourceUrl = inputIsUrl ? normalizeDocumentUrl(sourceText) : ''
    const policyMode = isPolicyExtractionType(documentType)
    const controller = new AbortController()
    submitAbortRef.current = controller
    const { signal } = controller

    if (!readyToProceed) {
      try {
        let workingText = resolvedSourceText || sourceText
        let workingUrl = resolvedSourceUrl || sourceUrl

        if (inputIsUrl && !resolvedSourceText) {
          setSubmitPhase('fetching')
          const resolved = await resolveExtractSource({
            text: sourceText,
            signal,
          })
          workingText = resolved.text
          workingUrl = resolved.source_url || sourceUrl
          setResolvedSourceText(workingText)
          setResolvedSourceUrl(workingUrl)
        }

        await runCostEstimate({
          workingText,
          workingUrl,
          signal,
        })
      } catch (err) {
        clearCostEstimate()
        if (err?.code !== 'ABORTED' && err?.name !== 'AbortError') {
          setError(extractionErrorMessage(err))
        } else {
          setError(null)
        }
      } finally {
        if (submitAbortRef.current === controller) {
          submitAbortRef.current = null
        }
        setSubmitPhase(null)
      }
      return
    }

    setSubmitPhase('extracting')
    const extractText = resolvedSourceText || sourceText
    const extractUrl = resolvedSourceUrl || sourceUrl
    try {
      if (policyMode) {
        const extracted = await extractPolicy({
          text: extractText,
          lang: currentLanguage(),
          sourceUrl: extractUrl || undefined,
          signal,
        })
        const entry = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          savedAt: new Date().toISOString(),
          text: sourceText,
          documentType,
          kind: 'policy',
          result: extracted,
        }
        persistHistory([entry, ...history].slice(0, EXTRACT_HISTORY_MAX))
        setActiveHistoryId(entry.id)
        setResult(extracted)
        setDocumentDraftValues(null)
        setAddDocumentOpen(false)
        setDocumentUrl(extracted.url || extractUrl || '')
        clearDocumentSearch()
        setAddDocumentError(null)
        clearCostEstimate()
        return
      }

      const extracted = await extractDocumentDraft({
        text: extractText,
        lang: currentLanguage(),
        categoryHint: documentType,
        sourceUrl: extractUrl || undefined,
        signal,
      })
      const fields = extracted.fields ?? {}
      const initialValues = documentInitialValuesFromDraftFields(fields, {
        categoryHint: documentType,
        sourceUrl: extractUrl,
      })
      const entry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        savedAt: new Date().toISOString(),
        text: sourceText,
        documentType,
        kind: 'document',
        documentFields: fields,
        result: null,
      }
      persistHistory([entry, ...history].slice(0, EXTRACT_HISTORY_MAX))
      setActiveHistoryId(entry.id)
      setResult(null)
      setDocumentUrl(extractUrl || fields.url || '')
      clearDocumentSearch()
      clearCostEstimate()
      await openDocumentDraftForm(initialValues)
    } catch (err) {
      if (err?.code === 'ABORTED' || err?.name === 'AbortError') {
        setError(null)
      } else {
        setResult(null)
        setDocumentUrl('')
        clearDocumentSearch()
        setAddDocumentOpen(false)
        setDocumentDraftValues(null)
        clearCostEstimate()
        setError(extractionErrorMessage(err))
      }
    } finally {
      if (submitAbortRef.current === controller) {
        submitAbortRef.current = null
      }
      setSubmitPhase(null)
    }
  }

  const addDocumentColumns =
    addDocumentSchema?.columns.filter(
      (column) => !(addDocumentSchema.auto_columns ?? []).includes(column),
    ) ?? []
  const editDocumentColumns =
    editDocumentSchema?.columns.filter(
      (column) => !(editDocumentSchema.auto_columns ?? []).includes(column),
    ) ?? []
  const editDocumentPrimaryKey = editDocumentSchema?.primary_key ?? []
  const documentActionsBusy =
    addDocumentLoading || editDocumentLoadingId != null

  return (
    <div className="space-y-section-gap">
      <div className="space-y-[calc(var(--spacing-section-gap)/2)]">
      {history.length > 0 ? (
        <section className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding">
          <h2 className="mb-card-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
            {t('admin.extract.savedTitle')}
          </h2>
          <ul className="max-h-[11.25rem] divide-y divide-border-subtle overflow-y-auto">
            {history.map((entry) => {
              const isActive = entry.id === activeHistoryId
              const methodCount = entry.result?.methods?.length ?? 0
              const savedLabel = new Date(entry.savedAt).toLocaleString(dateLocale, {
                dateStyle: 'short',
                timeStyle: 'short',
              })
              const metaLabel =
                entry.kind === 'document'
                  ? t('admin.extract.savedMetaDocument', { date: savedLabel })
                  : t('admin.extract.savedMeta', {
                      date: savedLabel,
                      count: methodCount,
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
                      {metaLabel}
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
        <div className="mb-card-gap flex flex-wrap items-start justify-between gap-3">
          <label
            htmlFor="document-extraction-text"
            className="block font-label-caps text-label-caps uppercase text-on-surface-variant"
          >
            {t('admin.extract.policyLabel')}
          </label>
          <div className="flex flex-wrap items-center gap-2">
            {uploadedFileName ? (
              <span className="inline-flex max-w-[16rem] items-center gap-2 rounded-md border border-border-subtle bg-surface-container-low px-2 py-1 font-metadata text-metadata text-on-surface">
                <span className="truncate" title={uploadedFileName}>
                  {uploadedFileName}
                </span>
                <button
                  type="button"
                  disabled={busy}
                  onClick={clearUploadedFile}
                  className="shrink-0 text-on-secondary-container transition-colors hover:text-error disabled:opacity-50"
                  title={t('admin.extract.clearUpload')}
                  aria-label={t('admin.extract.clearUpload')}
                >
                  ×
                </button>
              </span>
            ) : null}
            <input
              ref={fileInputRef}
              id={uploadInputId}
              type="file"
              accept=".pdf,.html,.htm,.txt,application/pdf,text/html,text/plain"
              className="sr-only"
              disabled={busy}
              onChange={handleUploadChange}
            />
            <label
              htmlFor={uploadInputId}
              className={`inline-flex cursor-pointer items-center justify-center rounded-md border border-border-emphasis bg-surface-container-lowest px-3 py-1.5 font-nav-link text-nav-link text-on-surface transition-all duration-ethos hover:bg-surface-container ${
                busy ? 'pointer-events-none opacity-50' : ''
              }`}
            >
              {uploading
                ? t('admin.extract.uploading')
                : t('admin.extract.upload')}
            </label>
          </div>
        </div>
        <div className="relative">
          <textarea
            id="document-extraction-text"
            value={text}
            onChange={(event) => {
              setText(event.target.value)
              clearCostEstimate()
            }}
            maxLength={POLICY_TEXT_MAX}
            rows={12}
            disabled={busy || textLocked}
            readOnly={textLocked}
            placeholder={
              textLocked
                ? t('admin.extract.uploadPlaceholder')
                : t('admin.extract.policyPlaceholder')
            }
            className="w-full resize-y rounded-lg border border-border-emphasis bg-surface-container-low p-container-padding pb-10 font-monospace-data text-monospace-data text-on-surface outline-none transition-colors duration-ethos placeholder:text-text-tertiary focus:border-primary disabled:opacity-60"
          />
          <div
            className="pointer-events-none absolute bottom-3 right-4 font-metadata text-metadata text-text-tertiary"
            aria-live="polite"
          >
            {t('admin.extract.charCount', {
              count: text.length,
              max: POLICY_TEXT_MAX,
            })}
          </div>
        </div>

        {trimmedLength > 0 && !inputIsUrl && trimmedLength < POLICY_TEXT_MIN ? (
          <p className="mt-card-gap font-metadata text-metadata text-error" role="alert">
            {t('admin.extract.tooShort', { min: POLICY_TEXT_MIN })}
          </p>
        ) : null}

        {error ? (
          <p className="mt-card-gap font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        ) : null}

        <div className="mt-card-gap flex flex-wrap items-end justify-between gap-3">
          <div className="flex min-w-0 flex-wrap items-end gap-3">
            <div className="min-w-[12rem]">
              <label
                htmlFor="document-extraction-type"
                className="mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant"
              >
                {t('admin.extract.documentTypeLabel')}
              </label>
              <select
                id="document-extraction-type"
                value={documentType}
                disabled={busy}
                onChange={handleDocumentTypeChange}
                className="w-full rounded-md border border-border-emphasis bg-surface-container-low px-3 py-2 font-metadata text-metadata text-on-surface outline-none transition-colors duration-ethos focus:border-primary disabled:opacity-60"
              >
                <option value="">{t('admin.selectOptional')}</option>
                {DOCUMENT_TYPE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {t(option.labelKey)}
                  </option>
                ))}
              </select>
            </div>
            {costEstimate ? (
              <p
                className="pb-2 font-metadata text-metadata text-on-secondary-container"
                aria-live="polite"
              >
                {t('admin.extract.costEstimate', {
                  cost: formatUsd(costEstimate.estimated_cost_usd),
                  inputTokens: costEstimate.input_tokens ?? 0,
                  outputTokens: costEstimate.output_tokens ?? 0,
                })}
              </p>
            ) : null}
          </div>
          <Button type="submit" disabled={!canSubmit}>
            {submitPhase === 'fetching'
              ? t('admin.extract.fetchingSeconds', { seconds: elapsedSeconds })
              : submitPhase === 'estimating'
                ? t('admin.extract.estimatingSeconds', {
                    seconds: elapsedSeconds,
                  })
                : submitPhase === 'extracting'
                  ? t('admin.extract.submittingSeconds', {
                      seconds: elapsedSeconds,
                    })
                  : readyToProceed
                    ? t('admin.extract.proceed')
                    : t('admin.extract.submit')}
          </Button>
        </div>
      </form>
      </div>

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
            <div className="sm:col-span-3">
              <dt className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('admin.extract.documentDescription')}
              </dt>
              <dd className="mt-1 font-metadata text-metadata text-on-surface">
                {result.description || t('admin.extract.notFound')}
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
                          <div className="flex min-w-0 items-center gap-1">
                            <p className="font-metadata text-metadata text-on-surface">
                              {pickLocalized(doc.doc_citation, currentLanguage())}
                              <span className="ml-2 opacity-65">({doc.slug})</span>
                            </p>
                            <EditIconButton
                              label={t('admin.edit')}
                              disabled={documentActionsBusy}
                              onClick={() => openEditDocument(doc)}
                            />
                          </div>
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
                            (doc.categories || []).join(', ') || doc.category,
                            pickLocalized(doc.institution, currentLanguage()),
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
                disabled={documentActionsBusy}
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
            {editDocumentError ? (
              <p className="font-metadata text-metadata text-error" role="alert">
                {editDocumentError}
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
                      documentName={result.document_name}
                      documentUrl={documentUrl}
                      documentType={documentType}
                      documentDescription={result.description}
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
      {addDocumentOpen && addDocumentSchema && documentDraftValues
        ? createPortal(
            <AddRowModal
              key={`extract-add-document-${documentDraftValues.slug ?? 'doc'}-${activeHistoryId ?? 'new'}`}
              table="documents"
              columns={addDocumentColumns}
              comments={addDocumentSchema.column_comments}
              types={addDocumentSchema.column_types}
              requiredColumns={addDocumentSchema.required_columns}
              foreignKeys={addDocumentSchema.foreign_keys}
              columnOptions={addDocumentSchema.column_options}
              mode="create"
              title={t('admin.extract.addDocument')}
              initialValues={documentDraftValues}
              onClose={() => {
                setAddDocumentOpen(false)
                setDocumentDraftValues(null)
              }}
              onSaved={() => {
                setAddDocumentOpen(false)
                setDocumentDraftValues(null)
              }}
            />,
            document.body,
          )
        : null}
      {editDocumentOpen && editDocumentSchema && editDocumentRow
        ? createPortal(
            <AddRowModal
              key={`extract-edit-document-${editDocumentRow.id}`}
              table="documents"
              columns={editDocumentColumns}
              comments={editDocumentSchema.column_comments}
              types={editDocumentSchema.column_types}
              requiredColumns={editDocumentSchema.required_columns}
              foreignKeys={editDocumentSchema.foreign_keys}
              columnOptions={editDocumentSchema.column_options}
              mode="edit"
              title={t('admin.editRow')}
              initialValues={editDocumentRow}
              lockedColumns={editDocumentPrimaryKey}
              primaryKey={primaryKeyValues(
                editDocumentRow,
                editDocumentPrimaryKey,
              )}
              onClose={() => {
                setEditDocumentOpen(false)
                setEditDocumentRow(null)
              }}
              onSaved={async () => {
                setEditDocumentOpen(false)
                setEditDocumentRow(null)
                await searchDocuments()
              }}
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
          <DocsPanel />
        ) : (
          <SettingsPanel />
        )}
      </div>
    </main>
  )
}
