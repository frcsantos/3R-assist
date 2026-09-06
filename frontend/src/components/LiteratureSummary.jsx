import { useTranslation } from 'react-i18next'

const PUBMED_URL = (pmid) => `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`

function renderSummaryText(text) {
  const parts = text.split(/(\[PMID:\d+\])/g)
  return parts.map((part, i) => {
    const match = part.match(/\[PMID:(\d+)\]/)
    if (match) {
      return (
        <a
          key={i}
          href={PUBMED_URL(match[1])}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-info-text underline-offset-2 hover:underline"
        >
          [{match[1]}]
        </a>
      )
    }
    return <span key={i}>{part}</span>
  })
}

export default function LiteratureSummary({ summary, citations }) {
  const { t } = useTranslation()

  if (!summary) return null

  return (
    <section className="rounded-lg border border-info-border bg-info-bg p-container-padding">
      <p className="mb-card-gap font-label-caps text-label-caps uppercase text-info-text">
        {t('pubmed.summary.title')}
      </p>

      <p className="font-body-base text-body-base leading-relaxed text-info-text">
        {renderSummaryText(summary)}
      </p>

      {citations?.length > 0 && (
        <div className="mt-card-gap border-t border-info-border pt-card-gap">
          <p className="mb-fine-gap font-metadata text-metadata font-medium uppercase tracking-wide text-info-text">
            {t('pubmed.summary.citedArticles')}
          </p>
          <ol className="space-y-2">
            {citations.map((citation) => (
              <li
                key={citation.pmid}
                className="font-metadata text-metadata text-info-text"
              >
                <span className="font-medium">{citation.authors_display}</span>
                {citation.pub_year ? ` (${citation.pub_year}). ` : '. '}
                <a
                  href={PUBMED_URL(citation.pmid)}
                  target="_blank"
                  rel="noreferrer"
                  className="italic underline-offset-2 hover:underline"
                >
                  {citation.title}
                </a>
                {' '}
                <span className="text-text-tertiary">PMID: {citation.pmid}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}
