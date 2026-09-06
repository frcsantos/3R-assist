import { useTranslation } from 'react-i18next'

const PUBMED_URL = (pmid) => `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`

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
  const { record, relevance_score, relevance_explanation, three_r_class, rank } =
    recommendation

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
          </div>

          <h3 className="font-card-title text-card-title text-primary">
            <a
              href={PUBMED_URL(record.pmid)}
              target="_blank"
              rel="noreferrer"
              className="underline-offset-2 hover:underline"
            >
              {record.title}
            </a>
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

      <a
        href={PUBMED_URL(record.pmid)}
        target="_blank"
        rel="noreferrer"
        className="font-metadata text-metadata text-primary underline-offset-2 hover:underline"
      >
        {t('pubmed.results.pubmedLink')} ↗
      </a>
    </article>
  )
}
