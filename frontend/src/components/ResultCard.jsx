import { useEffect, useId, useState } from 'react'
import HighlightedText from './HighlightedText'

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

function RegulationModal({
  item,
  onClose,
  closeLabel,
  noCitationLabel,
  linkLabel,
  highlightQuery,
}) {
  const titleId = useId()

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])

  if (!item) return null

  const citation = item.citation?.trim() || null
  const citationIsUrl = isHttpUrl(citation)
  const linkHref = item.url || (citationIsUrl ? citation : null)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="w-full max-w-sm rounded-lg border border-border-subtle bg-surface-container-lowest p-4 shadow-lg"
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <h4
            id={titleId}
            className="font-card-title text-card-title text-primary"
          >
            <HighlightedText text={item.label} query={highlightQuery} />
          </h4>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 -mr-1 -mt-1 flex h-9 w-9 items-center justify-center rounded text-2xl leading-none text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
            aria-label={closeLabel}
          >
            ×
          </button>
        </div>
        {citation ? (
          <p className="break-words font-body-base text-body-base text-on-secondary-container">
            {citationIsUrl ? (
              <ExternalLink href={citation}>
                <HighlightedText text={citation} query={highlightQuery} />
              </ExternalLink>
            ) : (
              <HighlightedText text={citation} query={highlightQuery} />
            )}
          </p>
        ) : (
          <p className="font-metadata text-metadata text-on-surface-variant" role="status">
            {noCitationLabel}
          </p>
        )}
        {linkHref && !citationIsUrl ? (
          <ExternalLink
            href={linkHref}
            className="mt-3 inline-block break-all font-metadata text-metadata text-primary underline underline-offset-2 hover:opacity-90"
          >
            <HighlightedText
              text={item.url || linkLabel}
              query={highlightQuery}
            />
          </ExternalLink>
        ) : null}
      </div>
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
  purpose,
  purposeLabel,
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
  matchLabel = 'Match',
  highlightQuery,
  hideTitle = false,
  className = '',
}) {
  const styles = threeRStyles[type] ?? threeRStyles.replacement
  // undefined badges → legacy single-type fallback; [] → no 3R qualification yet
  const displayBadges = badges ?? [{ type, label: type, rationale: null }]
  const citationText = protocolCitation?.trim() || null
  const [selectedRegulation, setSelectedRegulation] = useState(null)
  const showHeader = !hideTitle || score != null

  return (
    <article
      className={`rounded-lg border border-border-subtle bg-surface-container-lowest transition-colors duration-ethos hover:border-border-emphasis ${hideTitle ? 'px-container-padding pb-container-padding pt-2' : 'p-container-padding'} ${dimmed ? 'opacity-65' : ''} ${className}`}
    >
      {showHeader ? (
        <div className="mb-2 flex items-start justify-between gap-card-gap">
          {!hideTitle ? (
            <h3 className="font-card-title text-card-title text-primary">
              <HighlightedText text={title} query={highlightQuery} />
            </h3>
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
              <span className="font-monospace-data text-monospace-data">{score}%</span>
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
      {description && (
        <p className="mb-3 font-body-base text-body-base text-on-secondary-container">
          <HighlightedText text={description} query={highlightQuery} />
        </p>
      )}
      {citationText ? (
        <p className="mb-3 break-words font-metadata text-metadata text-on-secondary-container">
          {referenceLabel}:
          <br />
          {isHttpUrl(citationText) ? (
            <ExternalLink href={citationText}>
              <HighlightedText text={citationText} query={highlightQuery} />
            </ExternalLink>
          ) : (
            <HighlightedText text={citationText} query={highlightQuery} />
          )}
          {primaryUrl ? (
            <>
              {' '}
              <ExternalLink href={primaryUrl}>
                <HighlightedText
                  text={isHttpUrl(primaryUrl) ? primaryUrl : sourcesLabel}
                  query={highlightQuery}
                />
              </ExternalLink>
            </>
          ) : null}
        </p>
      ) : (
        <p
          className="mb-3 font-metadata text-metadata text-on-surface-variant"
          role="status"
        >
          {noCitationLabel}
        </p>
      )}
      {displayBadges.length > 0 && (
        <ul className="mb-3 flex flex-col gap-2">
          {displayBadges.map((badge) => {
            const badgeStyles = threeRStyles[badge.type] ?? threeRStyles.replacement
            return (
              <li
                key={badge.type}
                className="flex flex-col gap-1 sm:flex-row sm:items-start sm:gap-card-gap"
              >
                <span
                  className={`w-fit shrink-0 rounded border px-2 py-0.5 font-badge-button text-badge-button uppercase tracking-tight ${badgeStyles.badge}`}
                >
                  <HighlightedText
                    text={badge.label ?? badge.type}
                    query={highlightQuery}
                  />
                </span>
                {badge.rationale ? (
                  <p className="font-metadata text-metadata text-on-secondary-container">
                    <HighlightedText
                      text={badge.rationale}
                      query={highlightQuery}
                    />
                  </p>
                ) : null}
              </li>
            )
          })}
        </ul>
      )}
      {validationStatus && (
        <p className={`font-metadata text-metadata font-medium ${styles.accent}`}>
          {validationStatusLabel}:{' '}
          <HighlightedText text={validationStatus} query={highlightQuery} />
        </p>
      )}
      {regulatoryStatuses.length > 0 && (
        <div className="mt-2">
          <p className="mb-1 font-metadata text-metadata text-on-surface-variant">
            {approvedJurisdictionsLabel}:
          </p>
          <div className="flex flex-wrap items-center gap-fine-gap">
            {regulatoryStatuses.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => setSelectedRegulation(item)}
                className="rounded border border-border-subtle bg-surface-container px-2 py-0.5 font-badge-button text-badge-button text-on-surface transition-colors hover:border-border-emphasis hover:bg-surface-container-low"
              >
                <HighlightedText text={item.label} query={highlightQuery} />
              </button>
            ))}
          </div>
        </div>
      )}
      {purpose ? (
        <p className="mt-2 font-metadata text-metadata text-on-secondary-container">
          {purposeLabel ? (
            <>
              {purposeLabel}:{' '}
              <HighlightedText text={purpose} query={highlightQuery} />
            </>
          ) : (
            <HighlightedText text={purpose} query={highlightQuery} />
          )}
        </p>
      ) : null}
      <RegulationModal
        item={selectedRegulation}
        onClose={() => setSelectedRegulation(null)}
        closeLabel={closeLabel}
        noCitationLabel={noRegulatoryCitationLabel}
        linkLabel={regulatoryLinkLabel}
        highlightQuery={highlightQuery}
      />
    </article>
  )
}
