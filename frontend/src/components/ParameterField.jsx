import { useState } from 'react'
import { useTranslation } from 'react-i18next'

const inputClass = (incomplete) =>
  `w-full rounded-lg border bg-surface-container-lowest px-container-padding py-2 font-body-base text-body-base text-on-surface outline-none transition-colors duration-ethos focus:border-primary ${
    incomplete
      ? 'border-reduction-border bg-reduction-bg/30'
      : 'border-border-emphasis'
  }`

const confidenceStyles = {
  high: 'border-border-emphasis bg-surface-container-low text-on-secondary-container',
  medium: 'border-amber-500/50 bg-amber-500/10 text-amber-900',
  low: 'border-reduction-border bg-reduction-bg text-reduction-text',
}

export function FieldConfidenceIndicator({ level }) {
  const { t } = useTranslation()

  if (!level) return null

  const hintKey = `s2.fieldConfidence.hint.${level}`

  return (
    <span
      className={`inline-flex shrink-0 items-center rounded border px-1.5 py-0.5 text-[0.7rem] leading-snug ${confidenceStyles[level] ?? confidenceStyles.medium}`}
      title={t(hintKey, { defaultValue: '' }) || undefined}
    >
      {t(`s2.fieldConfidence.level.${level}`)}
    </span>
  )
}

export function EvidenceToggle({ evidence }) {
  const { t } = useTranslation()
  const [visible, setVisible] = useState(false)

  if (!evidence) return null

  return (
    <div className="space-y-1">
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="ml-auto font-metadata text-metadata text-primary underline decoration-border-emphasis underline-offset-2 transition-colors hover:decoration-primary"
        >
          {visible ? t('s2.hideEvidence') : t('s2.showEvidence')}
        </button>
      </div>
      {visible && evidence && (
        <p className="rounded-lg border-l-2 border-primary bg-surface-container-low px-card-gap py-2 font-metadata text-metadata text-on-secondary-container">
          <span className="font-semibold">{t('s2.evidenceLabel')}:</span>{' '}
          {evidence}
        </p>
      )}
    </div>
  )
}

export default function ParameterField({
  labelKey,
  value,
  onChange = () => {},
  incomplete = false,
  id,
  type = 'text',
  options = [],
  enumPrefix,
  hintKey,
  allowEmpty = false,
  evidence,
  fieldConfidence,
  readOnly = false,
}) {
  const { t } = useTranslation()
  const displayValue = value ?? ''
  const isMultiSelect = type === 'routes' || type === 'multiselect'
  const labelId = `${id}-label`

  function toggleOption(option) {
    const selected = Array.isArray(value) ? value : []
    if (selected.includes(option)) {
      onChange(selected.filter((item) => item !== option))
      return
    }
    onChange([...selected, option])
  }

  function renderInput() {
    if (readOnly) {
      const readOnlyValue = isMultiSelect
        ? (Array.isArray(value) ? value : [])
            .map((option) => t(`s2.enums.${enumPrefix}.${option}`))
            .join(', ')
        : displayValue

      return (
        <p
          id={id}
          className="rounded-lg border border-border-subtle bg-surface-container-low px-container-padding py-2 font-body-base text-body-base text-on-surface"
        >
          {readOnlyValue || t('s2.emptyOption')}
        </p>
      )
    }

    if (type === 'select') {
      return (
        <select
          id={id}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass(incomplete)}
        >
          {allowEmpty && <option value="">{t('s2.emptyOption')}</option>}
          {options.map((option) => (
            <option key={option} value={option}>
              {t(`s2.enums.${enumPrefix}.${option}`)}
            </option>
          ))}
        </select>
      )
    }

    if (type === 'textarea') {
      return (
        <textarea
          id={id}
          rows={3}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          className={`${inputClass(incomplete)} resize-y`}
        />
      )
    }

    if (type === 'number') {
      return (
        <input
          id={id}
          type="number"
          min="0"
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass(incomplete)}
        />
      )
    }

    if (type === 'boolean') {
      return (
        <select
          id={id}
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass(incomplete)}
        >
          <option value="">{t('s2.emptyOption')}</option>
          <option value="true">{t('s2.boolean.yes')}</option>
          <option value="false">{t('s2.boolean.no')}</option>
        </select>
      )
    }

    if (isMultiSelect) {
      const selected = Array.isArray(value) ? value : []
      return (
        <div
          id={id}
          role="group"
          aria-labelledby={labelId}
          className={`flex flex-wrap gap-x-4 gap-y-2 rounded-lg border px-container-padding py-2 ${
            incomplete
              ? 'border-reduction-border bg-reduction-bg/30'
              : 'border-border-emphasis bg-surface-container-lowest'
          }`}
        >
          {options.map((option) => {
            const checked = selected.includes(option)
            const optionId = `${id}-${option}`
            return (
              <label
                key={option}
                htmlFor={optionId}
                className="inline-flex cursor-pointer items-center gap-2 font-body-base text-body-base text-on-surface"
              >
                <input
                  id={optionId}
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleOption(option)}
                  className="h-4 w-4 rounded border-border-emphasis text-primary accent-primary"
                />
                {t(`s2.enums.${enumPrefix}.${option}`)}
              </label>
            )
          })}
        </div>
      )
    }

    return (
      <input
        id={id}
        type="text"
        value={displayValue}
        onChange={(e) => onChange(e.target.value)}
        className={inputClass(incomplete)}
      />
    )
  }

  return (
    <div className="space-y-1">
      <label
        id={isMultiSelect ? labelId : undefined}
        htmlFor={isMultiSelect ? undefined : id}
        className="flex items-center justify-between gap-2 text-on-surface-variant"
      >
        <span className="font-small-label text-small-label uppercase opacity-65">
          {t(labelKey)}
        </span>
        <FieldConfidenceIndicator level={fieldConfidence} />
      </label>
      {renderInput()}
      {hintKey && !readOnly && (
        <p className="font-metadata text-metadata text-text-tertiary">
          {t(hintKey)}
        </p>
      )}
      <EvidenceToggle evidence={evidence} />
    </div>
  )
}
