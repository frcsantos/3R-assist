import { useEffect, useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useParams } from 'react-router-dom'
import ResultCard from '../components/ResultCard'
import FeedbackModal from '../components/FeedbackModal'
import HighlightedText from '../components/HighlightedText'
import {
  fetchDocumentsCatalogue,
  fetchMethodsCatalogue,
} from '../lib/explore'
import {
  formatOecdReference,
  methodDescription,
  methodDisplayName,
  methodThreeRBadges,
  pickLocalized,
  primaryRegulatoryContext,
  primaryThreeR,
  jurisdictionLabel,
} from '../lib/search'

const TABS = ['methods', 'regulations', 'documents']

const DOCUMENT_CATEGORIES = {
  regulations: ['regulation', 'guideline'],
  documents: null,
}

function tabClass(isActive) {
  return isActive
    ? 'border-b-2 border-primary px-3 py-2 font-nav-link text-nav-link font-medium text-primary'
    : 'px-3 py-2 font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary'
}

function ExpandArrow({ open }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 12 12"
      className={`h-3 w-3 shrink-0 transition-transform ${open ? 'rotate-90' : ''}`}
    >
      <path
        d="M4 2.5L8 6L4 9.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function FeedbackIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
      <circle
        cx="10"
        cy="10"
        r="8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M10 6v5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <circle cx="10" cy="14" r="1" fill="currentColor" />
    </svg>
  )
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

const SKIP_SEARCH_KEYS = new Set([
  'embedding_json',
  'text_for_embedding',
  'id',
  'source_doc_id',
  'regulatory_doc_id',
  'created_at',
  'updated_at',
  'active',
])

function collectSearchText(value, parts = []) {
  if (value == null) return parts
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed) parts.push(trimmed)
    return parts
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    parts.push(String(value))
    return parts
  }
  if (Array.isArray(value)) {
    for (const entry of value) collectSearchText(entry, parts)
    return parts
  }
  if (typeof value === 'object') {
    for (const [key, entry] of Object.entries(value)) {
      if (SKIP_SEARCH_KEYS.has(key)) continue
      collectSearchText(entry, parts)
    }
  }
  return parts
}

function itemMatchesFilter(item, query) {
  return collectSearchText(item)
    .join(' ')
    .toLocaleLowerCase()
    .includes(query)
}

function DocumentCard({ document: doc, t, lang, highlightQuery, hideTitle = false, className = '' }) {
  const categoryLabels = (doc.categories?.length ? doc.categories : [doc.category])
    .filter(Boolean)
    .map((category) =>
      t(`s4.documentCategory.${category}`, {
        defaultValue: category,
      }),
    )
  const categoryLabel = categoryLabels.join(', ')
  const dateLabel = doc.date
    ? new Date(`${doc.date}T00:00:00`).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : null
  const citation = pickLocalized(doc.doc_citation, lang)
  const description = pickLocalized(doc.description, lang)
  const institution = pickLocalized(doc.institution, lang)

  return (
    <article
      className={`rounded-lg border border-border-subtle bg-surface-container-lowest ${hideTitle ? 'px-container-padding pb-container-padding pt-2' : 'p-container-padding'} ${className}`}
    >
      {!hideTitle ? (
        <h3 className="font-card-title text-card-title text-primary">
          <HighlightedText text={citation} query={highlightQuery} />
        </h3>
      ) : null}
      {description ? (
        <p className={`font-body-base text-body-base text-on-secondary-container ${hideTitle ? '' : 'mt-2'}`}>
          <HighlightedText text={description} query={highlightQuery} />
        </p>
      ) : null}
      <dl className="mt-3 space-y-2 font-metadata text-metadata text-on-secondary-container">
        {categoryLabel ? (
          <div className="flex flex-wrap gap-x-2">
            <dt className="text-on-surface-variant">{t('s4.fields.categories')}</dt>
            <dd>
              <HighlightedText text={categoryLabel} query={highlightQuery} />
            </dd>
          </div>
        ) : null}
        {institution ? (
          <div className="flex flex-wrap gap-x-2">
            <dt className="text-on-surface-variant">{t('s4.fields.institution')}</dt>
            <dd>
              <HighlightedText text={institution} query={highlightQuery} />
            </dd>
          </div>
        ) : null}
        {dateLabel ? (
          <div className="flex flex-wrap gap-x-2">
            <dt className="text-on-surface-variant">{t('s4.fields.date')}</dt>
            <dd>
              <HighlightedText text={dateLabel} query={highlightQuery} />
            </dd>
          </div>
        ) : null}
        {doc.url ? (
          <div className="flex flex-wrap gap-x-2">
            <dt className="text-on-surface-variant">{t('s4.fields.url')}</dt>
            <dd>
              {isHttpUrl(doc.url) ? (
                <a
                  href={doc.url}
                  target="_blank"
                  rel="noreferrer"
                  className="break-all text-primary underline underline-offset-2 hover:opacity-90"
                >
                  <HighlightedText text={doc.url} query={highlightQuery} />
                </a>
              ) : (
                <HighlightedText text={doc.url} query={highlightQuery} />
              )}
            </dd>
          </div>
        ) : null}
      </dl>
    </article>
  )
}

function ExpandableList({
  items,
  getKey,
  getLabel,
  renderCard,
  emptyLabel,
  noMatchesLabel,
  filterPlaceholder,
  expandLabel,
  collapseLabel,
  feedbackLabel,
}) {
  const [openKey, setOpenKey] = useState(null)
  const [filter, setFilter] = useState('')
  const [feedbackObject, setFeedbackObject] = useState(null)
  const listId = useId()
  const filterId = useId()

  const query = filter.trim().toLocaleLowerCase()
  const filteredItems = query
    ? items.filter((item) => itemMatchesFilter(item, query))
    : items

  return (
    <div className="space-y-card-gap">
      <div>
        <label htmlFor={filterId} className="sr-only">
          {filterPlaceholder}
        </label>
        <input
          id={filterId}
          type="search"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder={filterPlaceholder}
          autoComplete="off"
          className="w-full rounded-md border border-border-subtle bg-surface-container-lowest px-3 py-2 font-body-base text-body-base text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:outline-none"
        />
      </div>

      {items.length === 0 ? (
        <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
          {emptyLabel}
        </p>
      ) : filteredItems.length === 0 ? (
        <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
          {noMatchesLabel}
        </p>
      ) : (
        <ul className="divide-y divide-border-subtle rounded-lg border border-border-subtle bg-surface-container-lowest">
          {filteredItems.map((item, index) => {
            const key = getKey(item, index)
            const open = openKey === key
            const label = getLabel(item)
            const panelId = `${listId}-panel-${key}`
            const buttonId = `${listId}-button-${key}`
            return (
              <li key={key}>
                <button
                  id={buttonId}
                  type="button"
                  aria-expanded={open}
                  aria-controls={panelId}
                  aria-label={open ? collapseLabel : expandLabel}
                  onClick={() => setOpenKey(open ? null : key)}
                  className="flex w-full items-center gap-3 px-container-padding py-3 text-left transition-colors hover:bg-surface-container-low"
                >
                  <ExpandArrow open={open} />
                  <span className="min-w-0 flex-1 font-body-base text-body-base text-primary">
                    <HighlightedText text={label} query={query} />
                  </span>
                </button>
                {open ? (
                  <div
                    id={panelId}
                    role="region"
                    aria-labelledby={buttonId}
                    className="relative border-t border-border-subtle bg-surface-container-low"
                  >
                    {renderCard(item, query)}
                    <button
                      type="button"
                      aria-label={feedbackLabel}
                      title={feedbackLabel}
                      onClick={() => setFeedbackObject(label)}
                      className="absolute bottom-2 right-2 z-10 flex h-8 w-8 items-center justify-center rounded text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
                    >
                      <FeedbackIcon />
                    </button>
                  </div>
                ) : null}
              </li>
            )
          })}
        </ul>
      )}

      {feedbackObject ? (
        <FeedbackModal
          object={feedbackObject}
          url={window.location.href}
          onClose={() => setFeedbackObject(null)}
        />
      ) : null}
    </div>
  )
}

function MethodsPanel({ lang, t }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchMethodsCatalogue(lang)
      .then((result) => {
        if (!cancelled) setItems(result.methods ?? [])
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || t('s4.loadError'))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [lang, t])

  if (loading) {
    return (
      <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('s4.loading')}
      </p>
    )
  }
  if (error) {
    return (
      <p className="font-body-base text-body-base text-error" role="alert">
        {error}
      </p>
    )
  }

  return (
    <ExpandableList
      items={items}
      getKey={(item) => item.method.slug}
      getLabel={(item) => methodDisplayName(item.method, lang)}
      emptyLabel={t('s4.methods.empty')}
      noMatchesLabel={t('s4.noMatches')}
      filterPlaceholder={t('s4.filterPlaceholder')}
      expandLabel={t('s4.expand')}
      collapseLabel={t('s4.collapse')}
      feedbackLabel={t('s4.reportFeedback')}
      renderCard={(item, highlightQuery) => {
        const method = item.method
        const contexts = item.regulatory_contexts ?? []
        const primaryContext = primaryRegulatoryContext(contexts)
        const protocolCitation =
          method.source_citation?.trim() ||
          formatOecdReference(method.oecd_ref) ||
          null
        return (
          <ResultCard
            type={primaryThreeR(method)}
            badges={methodThreeRBadges(method, t, lang)}
            title={methodDisplayName(method, lang)}
            hideTitle
            className="rounded-none border-0 bg-transparent hover:border-transparent"
            validationStatus={
              method.validation_status
                ? t(`s3.validationStatus.${method.validation_status}`)
                : null
            }
            regulatoryStatuses={contexts.map((context, index) => {
              const jurisdiction = jurisdictionLabel(
                context.jurisdiction,
                lang,
                t,
              )
              const status = context.regulation_status
                ? t(`s3.regulatoryStatus.${context.regulation_status}`)
                : null
              const keyBase =
                typeof context.jurisdiction === 'object'
                  ? context.jurisdiction['en-us']
                  : context.jurisdiction
              return {
                key: `${keyBase}-${index}`,
                label: status ? `${jurisdiction}: ${status}` : jurisdiction,
                citation: context.regulatory_citation?.trim() || null,
                url: context.regulatory_url || null,
              }
            })}
            purpose={primaryContext?.regulation_purpose || null}
            purposeLabel={t('s3.purposeLabel')}
            validationStatusLabel={t('s3.validationStatusLabel')}
            approvedJurisdictionsLabel={t('s3.approvedJurisdictionsLabel')}
            description={methodDescription(method, lang)}
            protocolCitation={protocolCitation}
            noCitationLabel={t('s3.noProtocolCitation')}
            noRegulatoryCitationLabel={t('s3.noRegulatoryCitation')}
            primaryUrl={method.source_url || null}
            sourcesLabel={t('s3.sourceLink')}
            referenceLabel={t('s3.referenceLabel')}
            regulatoryLinkLabel={t('s3.regulatoryLink')}
            closeLabel={t('s3.close')}
            highlightQuery={highlightQuery}
          />
        )
      }}
    />
  )
}

function DocumentsPanel({ categories, emptyKey, t, lang }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchDocumentsCatalogue(categories)
      .then((result) => {
        if (!cancelled) setItems(result.documents ?? [])
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || t('s4.loadError'))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [categories, t])

  if (loading) {
    return (
      <p className="font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('s4.loading')}
      </p>
    )
  }
  if (error) {
    return (
      <p className="font-body-base text-body-base text-error" role="alert">
        {error}
      </p>
    )
  }

  return (
    <ExpandableList
      items={items}
      getKey={(item) => item.slug}
      getLabel={(item) => pickLocalized(item.doc_citation, lang)}
      emptyLabel={t(emptyKey)}
      noMatchesLabel={t('s4.noMatches')}
      filterPlaceholder={t('s4.filterPlaceholder')}
      expandLabel={t('s4.expand')}
      collapseLabel={t('s4.collapse')}
      feedbackLabel={t('s4.reportFeedback')}
      renderCard={(item, highlightQuery) => (
        <DocumentCard
          document={item}
          t={t}
          lang={lang}
          highlightQuery={highlightQuery}
          hideTitle
          className="rounded-none border-0 bg-transparent"
        />
      )}
    />
  )
}

export default function ExplorePage() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const { section } = useParams()
  const lang = (i18n.resolvedLanguage ?? i18n.language ?? 'en').split('-')[0]
  const activeTab = TABS.includes(section) ? section : 'methods'

  function selectTab(nextTab) {
    navigate(`/explore/${nextTab}`)
  }

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <header className="mb-section-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('s4.title')}
        </h1>

        <div
          className="mt-card-gap flex flex-wrap gap-2 border-b border-border-subtle"
          role="tablist"
          aria-label={t('s4.tabsLabel')}
        >
          {TABS.map((tab) => {
            const isActive = tab === activeTab
            return (
              <button
                key={tab}
                id={`explore-tab-${tab}`}
                type="button"
                role="tab"
                aria-selected={isActive}
                aria-controls={`explore-panel-${tab}`}
                onClick={() => selectTab(tab)}
                className={tabClass(isActive)}
              >
                {t(`s4.${tab}.label`)}
              </button>
            )
          })}
        </div>
      </header>

      <div
        id={`explore-panel-${activeTab}`}
        role="tabpanel"
        aria-labelledby={`explore-tab-${activeTab}`}
      >
        {activeTab === 'methods' ? (
          <MethodsPanel lang={lang} t={t} />
        ) : (
          <DocumentsPanel
            categories={DOCUMENT_CATEGORIES[activeTab]}
            emptyKey={`s4.${activeTab}.empty`}
            t={t}
            lang={lang}
          />
        )}
      </div>
    </main>
  )
}
