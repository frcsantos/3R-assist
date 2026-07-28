import { useEffect, useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useParams } from 'react-router-dom'
import ResultCard from '../components/ResultCard'
import {
  fetchDocumentsCatalogue,
  fetchMethodsCatalogue,
} from '../lib/explore'
import {
  formatOecdReference,
  methodDescription,
  methodDisplayName,
  methodThreeRBadges,
  primaryRegulatoryContext,
  primaryThreeR,
} from '../lib/search'

const TABS = ['methods', 'regulations', 'documents']

const DOCUMENT_CATEGORIES = {
  regulations: ['regulation', 'guideline'],
  documents: ['method_protocol'],
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

function isHttpUrl(value) {
  if (!value?.trim()) return false
  try {
    const parsed = new URL(value.trim())
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function DocumentCard({ document: doc, t }) {
  const categoryLabel = t(`s4.documentCategory.${doc.category}`, {
    defaultValue: doc.category,
  })
  const dateLabel = doc.date
    ? new Date(`${doc.date}T00:00:00`).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : null

  return (
    <article className="rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding">
      <h3 className="font-card-title text-card-title text-primary">{doc.doc_ref}</h3>
      <dl className="mt-3 space-y-2 font-metadata text-metadata text-on-secondary-container">
        <div className="flex flex-wrap gap-x-2">
          <dt className="text-on-surface-variant">{t('s4.fields.category')}</dt>
          <dd>{categoryLabel}</dd>
        </div>
        {dateLabel ? (
          <div className="flex flex-wrap gap-x-2">
            <dt className="text-on-surface-variant">{t('s4.fields.date')}</dt>
            <dd>{dateLabel}</dd>
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
                  {doc.url}
                </a>
              ) : (
                doc.url
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
}) {
  const [openKey, setOpenKey] = useState(null)
  const [filter, setFilter] = useState('')
  const listId = useId()
  const filterId = useId()

  const query = filter.trim().toLocaleLowerCase()
  const filteredItems = query
    ? items.filter((item) =>
        String(getLabel(item) ?? '')
          .toLocaleLowerCase()
          .includes(query),
      )
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
                    {getLabel(item)}
                  </span>
                </button>
                {open ? (
                  <div
                    id={panelId}
                    role="region"
                    aria-labelledby={buttonId}
                    className="border-t border-border-subtle bg-surface-container-low px-container-padding py-card-gap"
                  >
                    {renderCard(item)}
                  </div>
                ) : null}
              </li>
            )
          })}
        </ul>
      )}
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
      renderCard={(item) => {
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
            badges={methodThreeRBadges(method, t)}
            title={methodDisplayName(method, lang)}
            validationStatus={
              primaryContext
                ? t(`s3.validationStatus.${primaryContext.validation_status}`)
                : null
            }
            regulatoryStatuses={contexts.map((context, index) => {
              const jurisdiction = t(`s3.jurisdiction.${context.jurisdiction}`)
              const status = context.regulation_status
                ? t(`s3.regulatoryStatus.${context.regulation_status}`)
                : null
              return {
                key: `${context.jurisdiction}-${index}`,
                label: status ? `${jurisdiction}: ${status}` : jurisdiction,
                citation: context.regulatory_citation?.trim() || null,
                url: context.regulatory_url || null,
              }
            })}
            purpose={primaryContext?.regulation_purpose || null}
            purposeLabel={t('s3.purposeLabel')}
            description={methodDescription(method, lang)}
            protocolCitation={protocolCitation}
            noCitationLabel={t('s3.noProtocolCitation')}
            noRegulatoryCitationLabel={t('s3.noRegulatoryCitation')}
            primaryUrl={method.source_url || null}
            sourcesLabel={t('s3.sourceLink')}
            regulatoryLinkLabel={t('s3.regulatoryLink')}
            closeLabel={t('s3.close')}
          />
        )
      }}
    />
  )
}

function DocumentsPanel({ categories, emptyKey, t }) {
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
      getLabel={(item) => item.doc_ref}
      emptyLabel={t(emptyKey)}
      noMatchesLabel={t('s4.noMatches')}
      filterPlaceholder={t('s4.filterPlaceholder')}
      expandLabel={t('s4.expand')}
      collapseLabel={t('s4.collapse')}
      renderCard={(item) => <DocumentCard document={item} t={t} />}
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
          />
        )}
      </div>
    </main>
  )
}
