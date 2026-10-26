import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import HighlightedText from './HighlightedText'

const THREE_R_ORDER = ['replacement', 'reduction', 'refinement']

const threeRStyles = {
  replacement: {
    badge: 'bg-replacement-bg text-replacement-text border-replacement-border',
    accent: 'text-replacement-text',
  },
  reduction: {
    badge: 'bg-reduction-bg text-reduction-text border-reduction-border',
    accent: 'text-reduction-text',
  },
  refinement: {
    badge: 'bg-refinement-bg text-refinement-text border-refinement-border',
    accent: 'text-refinement-text',
  },
}

function isHttpUrl(value) {
  if (!value?.trim()) return false
  try {
    const parsed = new URL(value.trim())
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function urlsEquivalent(a, b) {
  if (!a || !b) return false
  try {
    const left = new URL(a.trim())
    const right = new URL(b.trim())
    return (
      left.href.replace(/\/$/, '') === right.href.replace(/\/$/, '') ||
      a.trim() === b.trim()
    )
  } catch {
    return a.trim() === b.trim()
  }
}

function ExternalLink({ href, children, className }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className={
        className ??
        'text-primary underline underline-offset-2 hover:opacity-90'
      }
    >
      {children}
    </a>
  )
}

function formatRegulationDate(value) {
  if (!value) return null
  const text = String(value).trim()
  if (!text) return null
  const day = text.match(/^(\d{4}-\d{2}-\d{2})/)
  if (day) return day[1]
  return text
}

function IndentedList({ items, highlightQuery }) {
  return (
    <ul className="ml-5 list-disc space-y-0.5">
      {items.map((entry, index) => (
        <li key={`${entry}-${index}`}>
          <HighlightedText text={entry} query={highlightQuery} />
        </li>
      ))}
    </ul>
  )
}

function Quote({ label, text, highlightQuery }) {
  return (
    <div>
      <p className="text-on-surface-variant">{label}:</p>
      <blockquote className="whitespace-pre-line border-l-2 border-border-emphasis pl-3 italic">
        <HighlightedText text={text} query={highlightQuery} />
      </blockquote>
    </div>
  )
}

export function RegulationDetail({
  item,
  statusLabel,
  purposeLabel,
  highlightQuery,
  onEdit,
  editLabel,
}) {
  const { t } = useTranslation()
  // The document citation has its own line and the regulation quote its own
  // block; the merged citation is used only when neither is available.
  const citation =
    item.documentCitation?.trim() ||
    (item.regulationQuote ? null : item.citation?.trim()) ||
    null
  const linkHref = item.url || (isHttpUrl(citation) ? citation : null)
  const date = formatRegulationDate(item.date)
  const publishedDate = formatRegulationDate(item.publishedDate)
  const effectiveDate = formatRegulationDate(item.effectiveDate)
  const deadline = formatRegulationDate(item.replacementDeadline)
  const endpoints = item.endpoints ?? []
  const statusHeading = date
    ? `${statusLabel} (${date})`
    : statusLabel

  return (
    <div className={`relative space-y-1.5 rounded-md bg-surface-container px-3 py-2 font-metadata text-metadata text-on-secondary-container ${onEdit ? 'pr-10' : ''}`}>
      {onEdit ? (
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation()
            onEdit(item)
          }}
          aria-label={editLabel}
          title={editLabel}
          className="absolute right-1 top-1 inline-flex h-7 w-7 items-center justify-center rounded-md text-primary transition-colors hover:bg-surface-container-lowest"
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
      ) : null}
      {item.body ? (
        <p className="font-medium">
          <HighlightedText text={item.body} query={highlightQuery} />
        </p>
      ) : null}
      {item.status ? (
        <p>
          <span className="text-on-surface-variant">{statusHeading}: </span>
          <HighlightedText text={item.status} query={highlightQuery} />
        </p>
      ) : date ? (
        <p>
          <span className="text-on-surface-variant">{statusLabel}: </span>
          {date}
        </p>
      ) : null}
      {publishedDate ? (
        <p>
          <span className="text-on-surface-variant">
            {t('s3.regulation.publishedDate')}:{' '}
          </span>
          {publishedDate}
        </p>
      ) : null}
      {effectiveDate ? (
        <p>
          <span className="text-on-surface-variant">
            {t('s3.regulation.effectiveDate')}:{' '}
          </span>
          {effectiveDate}
        </p>
      ) : null}
      {deadline ? (
        <p>
          <span className="text-on-surface-variant">
            {t('s3.regulation.replacementDeadline')}:{' '}
          </span>
          {deadline}
          {item.replacementTermYears
            ? ` (${t('s3.regulation.termYears', { count: item.replacementTermYears })})`
            : ''}
        </p>
      ) : null}
      {endpoints.length > 0 ? (
        <div>
          <p className="text-on-surface-variant">
            {t('s3.regulation.endpoints', { defaultValue: purposeLabel })}:
          </p>
          <IndentedList items={endpoints} highlightQuery={highlightQuery} />
        </div>
      ) : null}
      {item.endpointQuote ? (
        <Quote
          label={t('s3.regulation.endpointQuote')}
          text={item.endpointQuote}
          highlightQuery={highlightQuery}
        />
      ) : null}
      {item.regulationQuote ? (
        <Quote
          label={t('s3.regulation.regulationQuote')}
          text={item.regulationQuote}
          highlightQuery={highlightQuery}
        />
      ) : null}
      {citation ? (
        <p className="break-words">
          {linkHref ? (
            <ExternalLink href={linkHref}>
              <HighlightedText text={citation} query={highlightQuery} />
            </ExternalLink>
          ) : (
            <HighlightedText text={citation} query={highlightQuery} />
          )}
        </p>
      ) : linkHref ? (
        <ExternalLink href={linkHref}>
          <HighlightedText text={linkHref} query={highlightQuery} />
        </ExternalLink>
      ) : null}
    </div>
  )
}

export default function ResultCard({
  type = 'replacement',
  badges,
  title,
  score,
  dimmed = false,
  validationStatus,
  regulatoryStatuses = [],
  purposeLabel,
  regulationStatusLabel = 'Regulation status',
  validationStatusLabel = 'Validation status',
  approvedJurisdictionsLabel = 'Approved jurisdictions',
  matchedParams = [],
  description,
  primaryUrl,
  matchedParamsLabel,
  sourcesLabel,
  protocolCitation,
  referenceLabel = 'Reference',
  noCitationLabel,
  noRegulatoryCitationLabel,
  regulatoryLinkLabel = 'OECD / regulatory',
  closeLabel = 'Close',
  matchLabel = 'Relevance',
  highlightQuery,
  hideTitle = false,
  className = '',
  detailRows = [],
  endAction = null,
  titleExtra = null,
  headerMeta = null,
  onEditRegulation = null,
  editRegulationLabel = 'Edit',
}) {
  const { t } = useTranslation()
  const styles = threeRStyles[type] ?? threeRStyles.replacement
  const displayBadges = [...(badges ?? [{ type, label: type, rationale: null }])].sort(
    (a, b) =>
      THREE_R_ORDER.indexOf(a.type) - THREE_R_ORDER.indexOf(b.type),
  )
  const citationText = protocolCitation?.trim() || null
  const curationRow = detailRows.find((row) => row.key === 'review_status') ?? null
  const otherRows = detailRows.filter((row) => row.key !== 'review_status')
  const [selectedRegulation, setSelectedRegulation] = useState(null)
  const [activeRationale, setActiveRationale] = useState(null)
  const showHeader = !hideTitle || score != null
  const activeBadge =
    displayBadges.find((badge) => badge.type === activeRationale) ?? null

  const sourceHref =
    primaryUrl || (isHttpUrl(citationText) ? citationText : null)
  const citationIsOnlyUrl =
    citationText && isHttpUrl(citationText) && urlsEquivalent(citationText, sourceHref)

  return (
    <article
      className={`relative rounded-lg border border-border-subtle bg-surface-container-lowest transition-colors duration-ethos hover:border-border-emphasis ${hideTitle ? 'px-container-padding pb-container-padding pt-2' : 'p-container-padding'} ${dimmed ? 'opacity-65' : ''} ${className}`}
    >
      <div className="space-y-3">
        {showHeader ? (
          <div className="flex items-start justify-between gap-card-gap">
            {!hideTitle ? (
              <div className="min-w-0">
                <h3 className="font-card-title text-card-title text-primary">
                  <HighlightedText text={title} query={highlightQuery} />
                  {titleExtra}
                </h3>
                {headerMeta}
              </div>
            ) : (
              <span className="min-w-0 flex-1" />
            )}
            {score != null ? (
              <span
                className="group relative shrink-0 text-right font-metadata text-metadata text-text-tertiary"
                tabIndex={matchedParams.length > 0 ? 0 : undefined}
                aria-label={
                  matchedParams.length > 0
                    ? `${matchLabel} ${score}%. ${matchedParamsLabel}: ${matchedParams.join(', ')}`
                    : undefined
                }
              >
                {matchLabel}{' '}
                <span className="font-monospace-data text-monospace-data">
                  {score}%
                </span>
                {matchedParams.length > 0 ? (
                  <span
                    role="tooltip"
                    className="pointer-events-none absolute right-0 top-full z-10 mt-1 w-max max-w-[16rem] rounded border border-border-subtle bg-surface-container-lowest px-2 py-1.5 text-left font-metadata text-metadata text-on-secondary-container opacity-0 shadow-md transition-opacity duration-ethos group-hover:opacity-100 group-focus-within:opacity-100"
                  >
                    {matchedParamsLabel}: {matchedParams.join(', ')}
                  </span>
                ) : null}
              </span>
            ) : null}
          </div>
        ) : null}

        {curationRow ? (
          <p className="font-metadata text-metadata font-bold text-on-secondary-container">
            <span className="font-bold text-on-surface-variant">
              {curationRow.label}:{' '}
            </span>
            {curationRow.value}
          </p>
        ) : null}

        {description ? (
          <p className="pt-1 font-body-base text-body-base text-on-secondary-container">
            <HighlightedText text={description} query={highlightQuery} />
          </p>
        ) : null}

        {otherRows.length > 0 ? (
          <dl className="space-y-2 font-metadata text-metadata text-on-secondary-container">
            {otherRows.map((row) =>
              row.items?.length ? (
                <div key={row.key}>
                  <dt className="text-on-surface-variant">{row.label}</dt>
                  <dd>
                    <IndentedList
                      items={row.items}
                      highlightQuery={highlightQuery}
                    />
                  </dd>
                </div>
              ) : (
                <div key={row.key} className="flex flex-wrap gap-x-2">
                  <dt className="text-on-surface-variant">{row.label}</dt>
                  <dd>
                    <HighlightedText text={row.value} query={highlightQuery} />
                  </dd>
                </div>
              ),
            )}
          </dl>
        ) : null}

        {citationText || sourceHref ? (
          <div className="space-y-1.5 border-t border-border-subtle pt-3">
            {citationText && !citationIsOnlyUrl ? (
              <p className="break-words font-metadata text-metadata text-on-secondary-container">
                <span className="text-on-surface-variant">
                  {referenceLabel}:{' '}
                </span>
                {sourceHref ? (
                  <ExternalLink href={sourceHref}>
                    <HighlightedText
                      text={citationText}
                      query={highlightQuery}
                    />
                  </ExternalLink>
                ) : isHttpUrl(citationText) ? (
                  <ExternalLink href={citationText}>
                    <HighlightedText
                      text={citationText}
                      query={highlightQuery}
                    />
                  </ExternalLink>
                ) : (
                  <HighlightedText text={citationText} query={highlightQuery} />
                )}
              </p>
            ) : sourceHref ? (
              <p className="break-words font-metadata text-metadata">
                <span className="text-on-surface-variant">
                  {referenceLabel}:{' '}
                </span>
                <ExternalLink href={sourceHref}>
                  <HighlightedText
                    text={citationText && citationIsOnlyUrl ? citationText : sourceHref}
                    query={highlightQuery}
                  />
                </ExternalLink>
              </p>
            ) : (
              <p
                className="font-metadata text-metadata text-on-surface-variant"
                role="status"
              >
                {noCitationLabel}
              </p>
            )}
          </div>
        ) : noCitationLabel ? (
          <p
            className="font-metadata text-metadata text-on-surface-variant"
            role="status"
          >
            {noCitationLabel}
          </p>
        ) : null}

        {displayBadges.length > 0 ? (
          <div className="space-y-2 border-t border-border-subtle pt-3">
            <ul className="flex flex-wrap gap-1.5">
              {displayBadges.map((badge) => {
                const hasRationale = Boolean(badge.rationale)
                const isActive = activeRationale === badge.type
                const className = `w-fit rounded border px-2 py-0.5 font-badge-button text-badge-button uppercase tracking-tight bg-reduction-bg text-reduction-text border-reduction-border ${
                  hasRationale
                    ? 'cursor-pointer transition-opacity hover:opacity-90'
                    : ''
                } ${isActive ? 'ring-1 ring-primary/30' : ''}`

                if (!hasRationale) {
                  return (
                    <li key={badge.type}>
                      <span className={className}>
                        <HighlightedText
                          text={badge.label ?? badge.type}
                          query={highlightQuery}
                        />
                      </span>
                    </li>
                  )
                }

                return (
                  <li key={badge.type}>
                    <button
                      type="button"
                      aria-expanded={isActive}
                      aria-label={t('s3.toggleRationale', {
                        label: badge.label ?? badge.type,
                      })}
                      onClick={() =>
                        setActiveRationale(isActive ? null : badge.type)
                      }
                      className={className}
                    >
                      <HighlightedText
                        text={badge.label ?? badge.type}
                        query={highlightQuery}
                      />
                    </button>
                  </li>
                )
              })}
            </ul>
            {activeBadge?.rationale ? (
              <p className="rounded-md bg-surface-container px-3 py-2 font-metadata text-metadata text-on-secondary-container">
                <HighlightedText
                  text={activeBadge.rationale}
                  query={highlightQuery}
                />
              </p>
            ) : null}
          </div>
        ) : null}

        {(validationStatus ||
          regulatoryStatuses.length > 0) && (
          <div className="space-y-2">
            {validationStatus ? (
              <p
                className={`font-metadata text-metadata font-medium ${styles.accent}`}
              >
                <span className="font-normal text-on-surface-variant">
                  {validationStatusLabel}:{' '}
                </span>
                <HighlightedText
                  text={validationStatus}
                  query={highlightQuery}
                />
              </p>
            ) : null}
            {regulatoryStatuses.length > 0 ? (
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="font-metadata text-metadata text-on-surface-variant">
                    {approvedJurisdictionsLabel}:
                  </span>
                  {regulatoryStatuses.map((item) => {
                    const isActive = selectedRegulation?.key === item.key
                    return (
                      <button
                        key={item.key}
                        type="button"
                        aria-expanded={isActive}
                        onClick={() =>
                          setSelectedRegulation(isActive ? null : item)
                        }
                        className={`rounded border border-border-subtle bg-surface-container px-2 py-0.5 font-badge-button text-badge-button text-on-surface transition-colors hover:border-border-emphasis hover:bg-surface-container-low ${
                          isActive ? 'ring-1 ring-primary/30' : ''
                        }`}
                      >
                        <HighlightedText
                          text={item.label}
                          query={highlightQuery}
                        />
                      </button>
                    )
                  })}
                </div>
                {selectedRegulation ? (
                  <RegulationDetail
                    item={selectedRegulation}
                    statusLabel={regulationStatusLabel}
                    purposeLabel={purposeLabel}
                    highlightQuery={highlightQuery}
                    onEdit={
                      onEditRegulation && selectedRegulation.id != null
                        ? onEditRegulation
                        : null
                    }
                    editLabel={editRegulationLabel}
                  />
                ) : null}
              </div>
            ) : null}
          </div>
        )}
      </div>
      {endAction ? (
        <div className="absolute bottom-0 right-0 z-10">{endAction}</div>
      ) : null}
    </article>
  )
}
