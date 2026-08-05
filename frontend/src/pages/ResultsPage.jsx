import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, Navigate, useLocation } from 'react-router-dom'
import ExperimentTabs, { experimentTabLabel } from '../components/ExperimentTabs'
import ResultCard from '../components/ResultCard'
import {
  formatMatchedParams,
  formatOecdReference,
  isLowConfidenceScore,
  jurisdictionLabel,
  jurisdictionMatches,
  methodDescription,
  methodDisplayName,
  methodThreeRBadges,
  methodThreeRClasses,
  primaryThreeR,
  primaryRegulatoryContext,
  scorePercent,
} from '../lib/search'

const THREE_R_FILTERS = ['all', 'replacement', 'reduction', 'refinement']
const JURISDICTION_FILTERS = ['all', 'brazil', 'eu', 'us', 'oecd']

function ParamSummaryRow({ label, value }) {
  if (!value) return null
  return (
    <tr>
      <th className="w-48 bg-surface-container-low px-container-padding py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">
        {label}
      </th>
      <td className="px-container-padding py-3">{value}</td>
    </tr>
  )
}

function resolveExperimentSearchResults(state) {
  if (state.experimentSearchResults?.length) {
    return state.experimentSearchResults
  }
  if (!state.params) return []
  return [
    {
      params: state.params,
      studyType: state.studyType,
      notes: state.notes,
      recommendations: state.recommendations ?? [],
      filter_relaxation: state.filter_relaxation ?? null,
    },
  ]
}

export default function ResultsPage() {
  const { t } = useTranslation()
  const location = useLocation()
  const state = location.state ?? {}
  const { lang = 'en', searchCompleted } = state

  const experimentSearchResults = useMemo(
    () => resolveExperimentSearchResults(state),
    [state],
  )
  const [activeExperimentIndex, setActiveExperimentIndex] = useState(
    state.activeExperimentIndex ?? 0,
  )
  const [threeRFilter, setThreeRFilter] = useState('all')
  const [jurisdictionFilter, setJurisdictionFilter] = useState('all')

  const activeResult =
    experimentSearchResults[activeExperimentIndex] ??
    experimentSearchResults[0]
  const params = activeResult?.params
  const studyType = activeResult?.studyType
  const recommendations = activeResult?.recommendations ?? []
  const filterRelaxation = activeResult?.filter_relaxation

  const tabLabels = experimentSearchResults.map((result, index) =>
    experimentTabLabel(result.studyType, index, t),
  )

  const filteredResults = useMemo(() => {
    return recommendations.filter((item) => {
      const method = item.method
      const contexts = item.regulatory_contexts ?? []
      if (
        threeRFilter !== 'all' &&
        !methodThreeRClasses(method).includes(threeRFilter)
      ) {
        return false
      }
      if (
        jurisdictionFilter !== 'all' &&
        !contexts.some((context) =>
          jurisdictionMatches(context.jurisdiction, jurisdictionFilter),
        )
      ) {
        return false
      }
      return true
    })
  }, [recommendations, threeRFilter, jurisdictionFilter])

  if (!params) {
    return <Navigate to="/" replace />
  }

  if (!searchCompleted) {
    return <Navigate to="/parameters" state={state} replace />
  }

  const routeLabel = Array.isArray(params.route)
    ? params.route.map((route) => t(`s2.enums.route.${route}`)).join(', ')
    : null

  const navigationState = {
    ...state,
    activeExperimentIndex,
    experimentSearchResults,
  }

  return (
    <main className="mx-auto w-full max-w-content flex-1 px-container-padding py-section-gap">
      <div className="mb-card-gap">
        <Link
          to="/parameters"
          state={navigationState}
          className="font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary"
        >
          ← {t('s2.backToParams')}
        </Link>
      </div>

      <header className="mb-section-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('s3.title')}
        </h1>
        <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container">
          {t('s3.subtitle')}
        </p>
      </header>

      <ExperimentTabs
        tabs={tabLabels}
        activeIndex={activeExperimentIndex}
        onChange={setActiveExperimentIndex}
        count={experimentSearchResults.length}
        hintKey="s3.multiExperimentHint"
        tabsLabelKey="s3.experimentTabsLabel"
        idPrefix="results-experiment"
      />

      <section
        role="tabpanel"
        id={`results-experiment-panel-${activeExperimentIndex}`}
        aria-labelledby={`results-experiment-tab-${activeExperimentIndex}`}
        className="mb-section-gap overflow-hidden rounded-lg border border-border-subtle bg-surface-container-lowest"
      >
        <div className="border-b border-border-subtle px-container-padding py-4">
          <h2 className="font-label-caps text-label-caps uppercase text-on-surface-variant">
            {t('s3.protocolSummary')}
          </h2>
        </div>
        <table className="w-full border-collapse text-left">
          <tbody className="divide-y divide-border-subtle font-body-base text-body-base">
            <ParamSummaryRow label={t('s2.fields.studyType')} value={studyType} />
            <ParamSummaryRow
              label={t('s2.fields.endpointCategory')}
              value={
                params.endpoint_category
                  ? t(`s2.enums.endpointCategory.${params.endpoint_category}`)
                  : t('s2.endpointNotCovered')
              }
            />
            <ParamSummaryRow label={t('s2.fields.route')} value={routeLabel} />
            <ParamSummaryRow
              label={t('s2.fields.studyDomain')}
              value={
                params.study_domain
                  ? t(`s2.enums.studyDomain.${params.study_domain}`)
                  : null
              }
            />
            <ParamSummaryRow
              label={t('s2.fields.procedureText')}
              value={params.procedure_text}
            />
          </tbody>
        </table>
        {activeResult.notes && (
          <div className="border-t border-border-subtle px-container-padding py-4">
            <h3 className="mb-fine-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
              {t('s2.notesLabel')}
            </h3>
            <p className="font-body-base text-body-base text-on-secondary-container">
              {activeResult.notes}
            </p>
          </div>
        )}
      </section>

      {filterRelaxation && (
        <p
          className="mb-section-gap rounded-lg border border-border-subtle bg-surface-container-low px-container-padding py-3 font-metadata text-metadata text-on-secondary-container"
          role="status"
        >
          {t(`s3.filterRelaxation.${filterRelaxation}`)}
        </p>
      )}

      <section className="mb-section-gap">
        <div className="mb-card-gap flex flex-wrap gap-card-gap">
          <label className="flex items-center gap-fine-gap font-metadata text-metadata text-on-surface-variant">
            <span>{t('s3.filterThreeR')}</span>
            <select
              value={threeRFilter}
              onChange={(event) => setThreeRFilter(event.target.value)}
              className="rounded border border-border-subtle bg-surface-container-lowest px-2 py-1 text-on-surface"
            >
              {THREE_R_FILTERS.map((value) => (
                <option key={value} value={value}>
                  {value === 'all'
                    ? t('s3.filterAll')
                    : t(`s3.threeR.${value}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-fine-gap font-metadata text-metadata text-on-surface-variant">
            <span>{t('s3.filterJurisdiction')}</span>
            <select
              value={jurisdictionFilter}
              onChange={(event) => setJurisdictionFilter(event.target.value)}
              className="rounded border border-border-subtle bg-surface-container-lowest px-2 py-1 text-on-surface"
            >
              {JURISDICTION_FILTERS.map((value) => (
                <option key={value} value={value}>
                  {value === 'all'
                    ? t('s3.filterAll')
                    : t(`s3.jurisdiction.${value}`)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <h2 className="mb-card-gap font-label-caps text-label-caps uppercase text-on-surface-variant">
          {t('s3.recommendedAlternatives')}
          <span className="ml-2 normal-case text-on-secondary-container">
            ({filteredResults.length})
          </span>
        </h2>

        {filteredResults.length === 0 ? (
          <div className="rounded-lg border border-border-subtle bg-surface-container-low p-container-padding">
            <p className="font-body-base text-body-base text-on-secondary-container">
              {!params.endpoint_category
                ? t('s3.emptyNoEndpoint')
                : recommendations.length === 0
                  ? t('s3.emptyNoMethods')
                  : t('s3.emptyFiltered')}
            </p>
          </div>
        ) : (
          <div className="grid gap-card-gap">
            {filteredResults.map((item) => {
              const method = item.method
              const contexts = item.regulatory_contexts ?? []
              const primaryContext = primaryRegulatoryContext(contexts)
              const percent = scorePercent(item.score)
              const threeR = primaryThreeR(method)
              const protocolCitation =
                method.source_citation?.trim() ||
                formatOecdReference(method.oecd_ref) ||
                null
              return (
                <ResultCard
                  key={method.slug}
                  type={threeR}
                  badges={methodThreeRBadges(method, t)}
                  title={methodDisplayName(method, lang)}
                  score={percent}
                  dimmed={isLowConfidenceScore(item.score)}
                  validationStatus={
                    primaryContext
                      ? t(`s3.validationStatus.${primaryContext.validation_status}`)
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
                  matchedParams={formatMatchedParams(item.matched_params, t)}
                  matchedParamsLabel={t('s3.matchedParams')}
                  description={methodDescription(method, lang)}
                  protocolCitation={protocolCitation}
                  noCitationLabel={t('s3.noProtocolCitation')}
                  noRegulatoryCitationLabel={t('s3.noRegulatoryCitation')}
                  primaryUrl={method.source_url || null}
                  sourcesLabel={t('s3.sourceLink')}
                  regulatoryLinkLabel={t('s3.regulatoryLink')}
                  closeLabel={t('s3.close')}
                  matchLabel={t('s3.matchLabel')}
                />
              )
            })}
          </div>
        )}
      </section>

      <div className="border-t border-border-subtle pt-section-gap">
        <Link
          to="/literature"
          state={{
            protocol_text: state.protocolText,
            params: activeResult?.params,
            lang,
          }}
          className="inline-flex items-center gap-fine-gap rounded-lg border border-primary px-container-padding py-3 font-badge-button text-badge-button text-primary transition-colors hover:bg-primary hover:text-on-primary"
        >
          {t('pubmed.cta.label')} ↗
        </Link>
        <p className="mt-fine-gap font-metadata text-metadata text-on-secondary-container">
          {t('pubmed.cta.description')}
        </p>
      </div>
    </main>
  )
}
