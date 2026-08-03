import { useTranslation } from 'react-i18next'

const MIN_LENGTH = 20
const MAX_LENGTH = 40000

export { MIN_LENGTH, MAX_LENGTH }

export default function ProtocolTextarea({
  value,
  onChange,
  id = 'protocol-text',
}) {
  const { t } = useTranslation()

  return (
    <div className="rounded-lg border border-border-subtle bg-surface-container-lowest p-card-gap">
      <label
        htmlFor={id}
        className="mb-card-gap block font-label-caps text-label-caps uppercase text-on-surface-variant"
      >
        {t('s1.pasteLabel')}
      </label>
      <div className="relative">
        <textarea
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={MAX_LENGTH}
          rows={10}
          placeholder={t('s1.placeholder')}
          className="w-full resize-y rounded-lg border border-border-emphasis bg-surface-container-low p-container-padding font-monospace-data text-monospace-data text-on-surface outline-none transition-colors duration-ethos placeholder:text-text-tertiary focus:border-primary"
        />
        <div
          className="pointer-events-none absolute bottom-4 right-4 font-metadata text-metadata text-text-tertiary"
          aria-live="polite"
        >
          {t('s1.charCount', { count: value.length, max: MAX_LENGTH })}
        </div>
      </div>
    </div>
  )
}
