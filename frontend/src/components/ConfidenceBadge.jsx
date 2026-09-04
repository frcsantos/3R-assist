import { useTranslation } from 'react-i18next'

const styles = {
  high: 'border-border-emphasis bg-surface-container-low text-primary',
  medium: 'border-border-subtle bg-surface-container text-on-secondary-container',
  low: 'border-reduction-border bg-reduction-bg text-reduction-text',
}

export default function ConfidenceBadge({ level }) {
  const { t } = useTranslation()
  if (!level) return null

  return (
    <span
      className={`inline-flex shrink-0 items-center rounded border px-2.5 py-1 font-badge-button text-badge-button ${styles[level] ?? styles.medium}`}
    >
      {t(`pubmed.necessity.confidence.${level}`, { defaultValue: t(`s2.fieldConfidence.level.${level}`) })}
    </span>
  )
}
