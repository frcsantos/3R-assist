import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import ExperimentTabs, { experimentTabLabel } from '../components/ExperimentTabs'
import ParameterField, {
  EvidenceToggle,
  FieldConfidenceIndicator,
} from '../components/ParameterField'
import ProtocolTextPanel from '../components/ProtocolTextPanel'
import { resolveExperimentStates } from '../lib/experimentState.js'
import { setLanguage } from '../lib/i18n'
import { searchAllExperiments } from '../lib/search'
import {
  ANIMAL_COUNT_FIELDS,
  DISPLAY_FIELDS,
  ENDPOINT_FIELD,
  MATCHING_FIELDS,
  emptyParameterKeys,
} from '../lib/protocol'

const subsectionClass =
  'mt-section-gap border-t border-border-subtle pt-section-gap space-y-card-gap'

export default function ParametersPage() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const analysis = location.state

  const [experimentStates, setExperimentStates] = useState(() =>
    resolveExperimentStates(analysis),
  )
  const [activeExperimentIndex, setActiveExperimentIndex] = useState(
    analysis?.activeExperimentIndex ?? 0,
  )
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState(null)

  useEffect(() => {
    if (analysis?.lang) {
      void setLanguage(analysis.lang)
    }
  }, [analysis?.lang])

  if (!analysis?.params && !analysis?.experimentStates?.length) {
    return <Navigate to="/" replace />
  }

  const activeExperiment =
    experimentStates[activeExperimentIndex] ?? experimentStates[0]
  const params = activeExperiment?.params ?? {}
  const incompleteKeys = new Set(emptyParameterKeys(params))
  const endpointCovered = Boolean(params.endpoint_category?.trim())
  const tabLabels = experimentStates.map((experiment, index) =>
    experimentTabLabel(experiment.studyType, index, t),
  )

  function updateActiveParams(updater) {
    setExperimentStates((current) =>
      current.map((experiment, index) =>
        index === activeExperimentIndex
          ? {
              ...experiment,
              params: updater(experiment.params),
            }
          : experiment,
      ),
    )
  }

  function updateField(key, value) {
    updateActiveParams((current) => ({ ...current, [key]: value }))
  }

  function updateAnimalCount(key, value) {
    updateActiveParams((current) => ({
      ...current,
      animal_counts: {
        ...current.animal_counts,
        [key]: value,
      },
    }))
  }

  async function handleSearch() {
    setSearchError(null)
    setSearching(true)
    try {
      const experimentSearchResults = await searchAllExperiments(
        experimentStates,
        analysis.lang,
      )
      const activeResult =
        experimentSearchResults[activeExperimentIndex] ??
        experimentSearchResults[0]
      navigate('/resultados', {
        state: {
          ...analysis,
          experimentStates,
          activeExperimentIndex,
          experimentSearchResults,
          params: activeResult.params,
          studyType: activeResult.studyType,
          notes: activeResult.notes,
          recommendations: activeResult.recommendations,
          filter_relaxation: activeResult.filter_relaxation,
          searchCompleted: true,
        },
      })
    } catch (error) {
      setSearchError(error.message)
    } finally {
      setSearching(false)
    }
  }

  function renderFields(fields) {
    return (
      <div className="space-y-card-gap">
        {fields.map(
          ({
            key,
            labelKey,
            type,
            options,
            enumPrefix,
            hintKey,
            allowEmpty,
            evidenceKey,
            confidenceKey,
          }) => (
            <ParameterField
              key={key}
              id={`param-${key}-${activeExperimentIndex}`}
              labelKey={labelKey}
              type={type}
              options={options}
              enumPrefix={enumPrefix}
              hintKey={hintKey}
              allowEmpty={allowEmpty}
              value={params[key]}
              onChange={(value) => updateField(key, value)}
              incomplete={incompleteKeys.has(key)}
              evidence={
                evidenceKey
                  ? activeExperiment.evidence?.[evidenceKey] ?? null
                  : null
              }
              fieldConfidence={
                confidenceKey
                  ? activeExperiment.fieldConfidence?.[confidenceKey] ?? null
                  : null
              }
            />
          ),
        )}
      </div>
    )
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-container-padding py-section-gap">
      <div className="mb-section-gap">
        <Link
          to="/"
          state={{
            protocolText: analysis.protocolText,
            lang: analysis.lang,
          }}
          className="font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary"
        >
          ← {t('s2.backToEdit')}
        </Link>
      </div>

      <header className="mb-card-gap">
        <h1 className="font-headline-lg text-headline-lg text-primary">
          {t('s2.title')}
        </h1>
        <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container opacity-65">
          {t('s2.subtitle')}
        </p>
      </header>

      <div className="grid gap-section-gap lg:grid-cols-2 lg:items-start">
        <div className="space-y-section-gap">
          <ExperimentTabs
            tabs={tabLabels}
            activeIndex={activeExperimentIndex}
            onChange={setActiveExperimentIndex}
            count={experimentStates.length}
          />

          <section
            role="tabpanel"
            id={`experiment-panel-${activeExperimentIndex}`}
            aria-labelledby={`experiment-tab-${activeExperimentIndex}`}
            className="space-y-card-gap rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding"
          >
            <h2 className="font-label-caps text-label-caps uppercase text-on-surface-variant">
              {t('s2.identificationSection')}
            </h2>

            <div className="space-y-card-gap">
              <ParameterField
                id={`param-study-type-${activeExperimentIndex}`}
                labelKey="s2.fields.studyType"
                type="text"
                value={activeExperiment.studyType}
                readOnly
              />

              <div className="space-y-1">
                <ParameterField
                  id={`param-${ENDPOINT_FIELD.key}-${activeExperimentIndex}`}
                  labelKey={ENDPOINT_FIELD.labelKey}
                  type={ENDPOINT_FIELD.type}
                  options={ENDPOINT_FIELD.options}
                  enumPrefix={ENDPOINT_FIELD.enumPrefix}
                  allowEmpty={ENDPOINT_FIELD.allowEmpty}
                  value={params.endpoint_category}
                  onChange={(value) => updateField('endpoint_category', value)}
                  incomplete={false}
                />
                {!endpointCovered && (
                  <p className="font-metadata text-metadata text-reduction-text">
                    {t('s2.endpointNotCovered')}
                  </p>
                )}
              </div>
            </div>

            <div className={subsectionClass}>
              <h2 className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('s2.matchingSection')}
              </h2>
              {renderFields(MATCHING_FIELDS)}
            </div>

            <div className={subsectionClass}>
              <h2 className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                {t('s2.displaySection')}
              </h2>

              {renderFields(DISPLAY_FIELDS)}

              <div className="space-y-card-gap pt-fine-gap">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-small-label text-small-label uppercase text-on-surface-variant opacity-65">
                    {t('s2.fields.animalCounts.label')}
                  </p>
                  <FieldConfidenceIndicator
                    level={activeExperiment.fieldConfidence?.animal_counts}
                  />
                </div>
                <div className="grid gap-card-gap sm:grid-cols-2">
                  {ANIMAL_COUNT_FIELDS.map(({ key, labelKey }) => (
                    <ParameterField
                      key={key}
                      id={`param-animal-count-${key}-${activeExperimentIndex}`}
                      labelKey={labelKey}
                      type="number"
                      allowEmpty
                      value={params.animal_counts?.[key] ?? ''}
                      onChange={(value) => updateAnimalCount(key, value)}
                    />
                  ))}
                </div>
                <EvidenceToggle evidence={activeExperiment.evidence?.animal_counts} />
              </div>
            </div>

            {activeExperiment.notes && (
              <div className={subsectionClass}>
                <h2 className="font-label-caps text-label-caps uppercase text-on-surface-variant">
                  {t('s2.notesLabel')}
                </h2>
                <p className="font-body-base text-body-base text-on-secondary-container">
                  {activeExperiment.notes}
                </p>
              </div>
            )}
          </section>

          {incompleteKeys.size > 0 && (
            <p
              className="font-metadata text-metadata text-reduction-text"
              role="status"
            >
              {t('s2.incompleteWarning')}
            </p>
          )}

          {searchError && (
            <p
              className="font-metadata text-metadata text-reduction-text"
              role="alert"
            >
              {searchError}
            </p>
          )}

          <div className="flex justify-end">
            <Button
              type="button"
              onClick={handleSearch}
              disabled={searching || incompleteKeys.size > 0}
            >
              {searching ? t('s2.searching') : t('s2.searchCta')}
              {!searching && <span aria-hidden="true">→</span>}
            </Button>
          </div>
        </div>

        <aside className="lg:sticky lg:top-section-gap">
          <ProtocolTextPanel
            protocolText={analysis.protocolText}
            evidence={activeExperiment.evidence}
          />
        </aside>
      </div>
    </main>
  )
}
