import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import LiteratureSummary from '../components/LiteratureSummary'
import PubMedResultCard from '../components/PubMedResultCard'
import { analyzePubMed } from '../lib/pubmed'

const MIN_CHARS = 100
const MAX_CHARS = 8000

function LoadingState() {
  const { t } = useTranslation()
  return (
    <div className="flex flex-col items-center gap-card-gap py-section-gap text-on-secondary-container">
      <svg className="h-8 w-8 animate-spin text-primary" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <p className="font-body-base text-body-base">{t('litSearch.analyzing')}</p>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  const { t } = useTranslation()
  return (
    <div className="rounded-lg border border-error bg-error-container p-container-padding">
      <p className="font-body-base text-body-base text-on-error-container">
        {message ?? t('litSearch.error')}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-card-gap font-badge-button text-badge-button text-on-error-container underline-offset-2 hover:underline"
        >
          {t('litSearch.retry')}
        </button>
      )}
    </div>
  )
}

export default function LiteratureSearchPage() {
  const { t, i18n } = useTranslation()
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const charCount = text.length
  const tooShort = charCount > 0 && charCount < MIN_CHARS
  const canSubmit = charCount >= MIN_CHARS && !loading

  async function runAnalysis() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await analyzePubMed({
        protocol_text: text,
        params: null,
        lang: i18n.language,
      })
      setResult(data)
    } catch (err) {
      setError(err?.message ?? 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (canSubmit) runAnalysis()
  }

  const recommendations = result?.recommendations ?? []

  return (
    <main className="mx-auto w-full max-w-content flex-1 px-container-padding py-section-gap">
      <header className="mb-section-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('litSearch.title')}
        </h1>
        <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container">
          {t('litSearch.subtitle')}
        </p>
      </header>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="mb-section-gap flex flex-col gap-card-gap">
        <label
          htmlFor="study-text"
          className="font-label-caps text-label-caps uppercase text-on-surface-variant"
        >
          {t('litSearch.inputLabel')}
        </label>
        <textarea
          id="study-text"
          value={text}
          onChange={(e) => setText(e.target.value.slice(0, MAX_CHARS))}
          rows={12}
          placeholder={t('litSearch.placeholder')}
          className="w-full resize-y rounded-lg border border-border-subtle bg-surface-container-low p-container-padding font-body-base text-body-base text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none"
        />
        <div className="flex items-center justify-between">
          <span className={`font-metadata text-metadata ${tooShort ? 'text-error' : 'text-on-secondary-container'}`}>
            {tooShort
              ? t('litSearch.tooShort', { min: MIN_CHARS })
              : `${charCount} / ${MAX_CHARS}`}
          </span>
          <button
            type="submit"
            disabled={!canSubmit}
            className="rounded-md bg-primary px-6 py-2 font-nav-link text-nav-link text-on-primary transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? t('litSearch.analyzing') : t('litSearch.submit')}
          </button>
        </div>
      </form>

      {/* Results */}
      {loading && <LoadingState />}

      {!loading && error && (
        <ErrorState message={error} onRetry={runAnalysis} />
      )}

      {!loading && result && (
        <div className="flex flex-col gap-section-gap">
          {result.endpoint_hypothesis && (
            <p className="font-metadata text-metadata text-on-secondary-container">
              <span className="font-medium uppercase tracking-wide">
                {t('pubmed.page.endpointHypothesis')}
              </span>{' '}
              {result.endpoint_hypothesis}
            </p>
          )}

          {result.summary && (
            <LiteratureSummary summary={result.summary} citations={result.citations} />
          )}

          <section>
            <h2 className="mb-card-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
              {t('pubmed.page.literatureAlternatives')}
              <span className="ml-2 normal-case text-on-secondary-container">
                ({recommendations.length})
              </span>
            </h2>

            {result.total_candidates_searched > 0 && (
              <p className="mb-card-gap font-metadata text-metadata text-on-secondary-container">
                {t('pubmed.page.totalSearched', { count: result.total_candidates_searched })}
              </p>
            )}

            {result.no_literature_found || recommendations.length === 0 ? (
              <div className="rounded-lg border border-border-subtle bg-surface-container-low p-container-padding">
                <p className="font-body-base text-body-base text-on-secondary-container">
                  {t('pubmed.page.noLiterature')}
                </p>
              </div>
            ) : (
              <div className="grid gap-card-gap">
                {recommendations.map((rec) => (
                  <PubMedResultCard key={rec.record.pmid} recommendation={rec} />
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </main>
  )
}
