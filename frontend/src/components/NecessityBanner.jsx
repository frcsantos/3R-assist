import { useTranslation } from 'react-i18next'
import ConfidenceBadge from './ConfidenceBadge'

const VERDICT_STYLES = {
  not_necessary: {
    wrapper: 'border-replacement-border bg-replacement-bg',
    text: 'text-replacement-text',
    badge: 'bg-replacement-bg text-replacement-text border-replacement-border',
  },
  possibly_avoidable: {
    wrapper: 'border-reduction-border bg-reduction-bg',
    text: 'text-reduction-text',
    badge: 'bg-reduction-bg text-reduction-text border-reduction-border',
  },
  necessary: {
    wrapper: 'border-error bg-error-container',
    text: 'text-on-error-container',
    badge: 'bg-error-container text-on-error-container border-error',
  },
}

export default function NecessityBanner({ necessity }) {
  const { t } = useTranslation()
  const styles = VERDICT_STYLES[necessity.verdict] ?? VERDICT_STYLES.necessary

  return (
    <section
      className={`rounded-lg border p-container-padding ${styles.wrapper}`}
      aria-label={t('pubmed.necessity.title')}
    >
      <p className="mb-fine-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
        {t('pubmed.necessity.title')}
      </p>

      <div className="mb-card-gap flex flex-wrap items-center gap-fine-gap">
        <span
          className={`rounded border px-2.5 py-1 font-badge-button text-badge-button uppercase ${styles.badge}`}
        >
          {t(`pubmed.necessity.${necessity.verdict}`)}
        </span>
        <ConfidenceBadge level={necessity.confidence} />
      </div>

      <p className={`font-body-base text-body-base ${styles.text}`}>
        {necessity.rationale}
      </p>

      {necessity.key_concerns?.length > 0 && (
        <div className="mt-card-gap">
          <p className={`mb-fine-gap font-metadata text-metadata font-medium uppercase tracking-wide ${styles.text}`}>
            {t('pubmed.necessity.keyConcerns')}
          </p>
          <ul className={`list-disc pl-5 font-metadata text-metadata space-y-1 ${styles.text}`}>
            {necessity.key_concerns.map((concern, i) => (
              <li key={i}>{concern}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
