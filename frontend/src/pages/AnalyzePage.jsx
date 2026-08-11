import { useEffect, useId, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import ProtocolTextarea, {
  MAX_LENGTH,
  MIN_LENGTH,
} from '../components/ProtocolTextarea'
import { buildAnalysisState, uploadProtocolSource } from '../lib/analyze'
import { currentLanguage, setLanguage } from '../lib/i18n'
import {
  MOCK_ANALYZE_RESPONSE,
  MOCK_PROTOCOL_TEXT,
} from '../lib/mockAnalyzeResponse'

export default function AnalyzePage({ onSubmit }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const restored = location.state
  const uploadInputId = useId()
  const fileInputRef = useRef(null)

  const [protocolText, setProtocolText] = useState(restored?.protocolText ?? '')
  const [submitting, setSubmitting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadedFileName, setUploadedFileName] = useState(null)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (restored?.lang) {
      void setLanguage(restored.lang)
    }
  }, [restored?.lang])

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

  const busy = submitting || uploading
  const trimmedLength = protocolText.trim().length
  const canSubmit = trimmedLength >= MIN_LENGTH && !busy

  function clearUploadedFile() {
    setUploadedFileName(null)
    setProtocolText('')
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  function uploadErrorMessage(err) {
    const code = err?.code
    if (code === 'FILE_TYPE_UNSUPPORTED') return t('s1.uploadTypeError')
    if (code === 'FILE_TOO_LARGE') return t('s1.uploadTooLarge')
    if (code === 'FILE_NO_TEXT') return t('s1.uploadNoText')
    if (code === 'FILE_READ_FAILED') return t('s1.uploadReadError')
    return err.message ?? t('s1.uploadError')
  }

  async function handleUploadChange(event) {
    const file = event.target.files?.[0]
    if (!file || busy) return

    setError(null)
    setUploading(true)
    try {
      const uploaded = await uploadProtocolSource(file)
      const uploadedText = (uploaded.text ?? '').slice(0, MAX_LENGTH)
      setProtocolText(uploadedText)
      setUploadedFileName(uploaded.filename || file.name)
    } catch (err) {
      clearUploadedFile()
      setError(uploadErrorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  function handleMock() {
    if (busy) return

    setError(null)
    setUploadedFileName(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    setProtocolText(MOCK_PROTOCOL_TEXT)
    navigate('/parameters', {
      state: buildAnalysisState(MOCK_ANALYZE_RESPONSE, {
        protocolText: MOCK_PROTOCOL_TEXT,
        lang: currentLanguage(),
        isMock: true,
      }),
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return

    setError(null)
    setSubmitting(true)
    try {
      const lang = currentLanguage()
      const result = await onSubmit({
        protocolText: protocolText.trim(),
        lang,
      })
      navigate('/parameters', {
        state: buildAnalysisState(result, {
          protocolText: protocolText.trim(),
          lang,
        }),
      })
    } catch (err) {
      setError(err.message ?? 'Request failed')
    } finally {
      setSubmitting(false)
    }
  }

  const uploadControls = (
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
            title={t('s1.clearUpload')}
            aria-label={t('s1.clearUpload')}
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
        {uploading ? t('s1.uploading') : t('s1.upload')}
      </label>
    </div>
  )

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <header className="mb-section-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('s1.title')}
        </h1>
        <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container opacity-65">
          {t('s1.subtitle')}
        </p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-card-gap">
        <ProtocolTextarea
          value={protocolText}
          onChange={(next) => {
            setProtocolText(next)
            if (uploadedFileName) {
              setUploadedFileName(null)
            }
          }}
          headerAction={uploadControls}
          disabled={busy}
        />

        {trimmedLength > 0 && trimmedLength < MIN_LENGTH && (
          <p className="font-metadata text-metadata text-error" role="alert">
            {t('s1.tooShort', { min: MIN_LENGTH })}
          </p>
        )}

        {error && (
          <p className="font-metadata text-metadata text-error" role="alert">
            {error}
          </p>
        )}

        <div className="flex justify-end gap-card-gap">
          <Button
            type="button"
            variant="secondary"
            onClick={handleMock}
            disabled={busy}
          >
            {t('s1.mock')}
          </Button>
          <Button type="submit" disabled={!canSubmit}>
            {submitting
              ? t('s1.submittingSeconds', { seconds: elapsedSeconds })
              : t('s1.submit')}
            {!submitting && <span aria-hidden="true">→</span>}
          </Button>
        </div>
      </form>

      <div className="mt-section-gap border-t border-border-subtle pt-card-gap">
        <p className="font-body-base text-body-base text-on-secondary-container">
          {t('s1.searchLink')}{' '}
          <Link
            to="/explore"
            className="font-medium text-primary underline decoration-border-emphasis underline-offset-2 transition-colors hover:decoration-primary"
          >
            {t('s1.searchLinkAction')} →
          </Link>
        </p>
      </div>

      <p className="mt-section-gap text-center font-metadata text-metadata text-text-tertiary">
        {t('s1.anonymous')}
      </p>
    </main>
  )
}
