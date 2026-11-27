import { useState } from 'react'
import { useTranslation } from 'react-i18next'

const ARTICLE_URL = (record) => {
  const id = record.doi || record.pmid
  if (!id) return null
  if (id.startsWith('10.')) return `https://doi.org/${id}`
  return `https://pubmed.ncbi.nlm.nih.gov/${id}/`
}

const THREE_R_STYLES = {
  replacement: {
    badge: 'bg-replacement-bg text-replacement-text border-replacement-border',
    rank: 'bg-replacement-bg text-replacement-text',
  },
  reduction: {
    badge: 'bg-reduction-bg text-reduction-text border-reduction-border',
    rank: 'bg-reduction-bg text-reduction-text',
  },
  refinement: {
    badge: 'bg-refinement-bg text-refinement-text border-refinement-border',
    rank: 'bg-refinement-bg text-refinement-text',
  },
}

export default function PubMedResultCard({ recommendation }) {
  const { t } = useTranslation()
  const {
    record,
    relevance_score,
    relevance_explanation,
    three_r_class,
    rank,
    search_path,
    supporting_papers = [],
  } = recommendation
  const [showSupporting, setShowSupporting] = useState(false)
  const articleUrl = ARTICLE_URL(record)

  const styles = THREE_R_STYLES[three_r_class] ?? THREE_R_STYLES.refinement
  const scorePercent = Math.round(relevance_score * 100)

  const authorsLine = [
    record.authors_display ?? record.authors
      ?.slice(0, 3)
      .map((a) => a.display_name ?? [a.fore_name, a.last_name].filter(Boolean).join(' '))
      .join(', '),
    record.authors?.length > 3 ? 'et al.' : null,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <article className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding transition-colors hover:border-border-emphasis">
      <div className="mb-3 flex items-start gap-card-gap">
        <span
          className={`shrink-0 flex h-6 w-6 items-center justify-center rounded-full text-center font-badge-button text-badge-button ${styles.rank}`}
          aria-label={`Rank ${rank}`}
        >
          {rank}
        </span>

        <div className="min-w-0 flex-1">
          <div className="mb-fine-gap flex flex-wrap items-center gap-fine-gap">
            <span
              className={`rounded border px-2 py-0.5 font-badge-button text-badge-button uppercase ${styles.badge}`}
            >
              {t(`s3.threeR.${three_r_class}`)}
            </span>
            <span className="font-metadata text-metadata text-text-tertiary">
              {t('pubmed.results.scoreLabel')}{' '}
              <span className="font-monospace-data text-monospace-data text-on-surface">
                {scorePercent}%
              </span>
            </span>
            <span className="rounded border border-border-subtle px-2 py-0.5 font-badge-button text-badge-button text-text-tertiary">
              {search_path === 'alternative_search' ? t('pubmed.results.pathAlternative') : t('pubmed.results.pathEndpoint')}
            </span>
          </div>

          <h3 className="font-card-title text-card-title text-primary">
            {articleUrl ? (
              <a
                href={articleUrl}
                target="_blank"
                rel="noreferrer"
                className="underline-offset-2 hover:underline"
              >
                {record.title}
              </a>
            ) : (
              record.title
            )}
          </h3>
        </div>
      </div>

      {(authorsLine || record.pub_year) && (
        <p className="mb-3 font-metadata text-metadata text-text-tertiary">
          {[authorsLine, record.pub_year].filter(Boolean).join(' · ')}
        </p>
      )}

      {relevance_explanation && (
        <p className="mb-3 font-body-base text-body-base text-on-secondary-container">
          {relevance_explanation}
        </p>
      )}

      {articleUrl && (
        <a
          href={articleUrl}
          target="_blank"
          rel="noreferrer"
          className="font-metadata text-metadata text-primary underline-offset-2 hover:underline"
        >
          {t('pubmed.results.pubmedLink')} ↗
        </a>
      )}

      {supporting_papers.length > 0 && (
        <div className="mt-3 border-t border-border-subtle pt-3">
          <button
            onClick={() => setShowSupporting((v) => !v)}
            className="font-metadata text-metadata text-text-tertiary transition-colors hover:text-primary"
          >
            {showSupporting
              ? t('pubmed.results.hideSimilar')
              : t('pubmed.results.showSimilar', { count: supporting_papers.length })}
            {' '}{showSupporting ? '▲' : '▼'}
          </button>
          {showSupporting && (
            <ul className="mt-2 flex flex-col gap-1">
              {supporting_papers.map((sp) => {
                const url = sp.doi?.startsWith('10.')
                  ? `https://doi.org/${sp.doi}`
                  : `https://pubmed.ncbi.nlm.nih.gov/${sp.pmid}/`
                return (
                  <li key={sp.pmid} className="font-metadata text-metadata">
                    <a
                      href={url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary underline-offset-2 hover:underline"
                    >
                      {sp.title}
                    </a>
                    {sp.pub_year && (
                      <span className="ml-1 text-text-tertiary">({sp.pub_year})</span>
                    )}
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      )}
    </article>
  )
}
