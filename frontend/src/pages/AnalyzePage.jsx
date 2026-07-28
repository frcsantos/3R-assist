import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import ProtocolTextarea, { MIN_LENGTH } from '../components/ProtocolTextarea'
import { buildAnalysisState } from '../lib/analyze'
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

  const [protocolText, setProtocolText] = useState(restored?.protocolText ?? '')
  const [submitting, setSubmitting] = useState(false)
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

  const trimmedLength = protocolText.trim().length
  const canSubmit = trimmedLength >= MIN_LENGTH && !submitting

  function handleMock() {
    if (submitting) return

    setError(null)
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
          onChange={setProtocolText}
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
            disabled={submitting}
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
