import { useEffect, useId, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
import Button from './Button'
import { submitFeedback } from '../lib/feedback'

export default function FeedbackModal({ object, url, onClose }) {
  const { t } = useTranslation()
  const titleId = useId()
  const fieldId = useId()
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape' && !submitting) onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose, submitting])

  async function handleSubmit(event) {
    event.preventDefault()
    const feedbackText = text.trim()
    if (!feedbackText || submitting) return

    setSubmitting(true)
    setError(null)
    try {
      await submitFeedback({
        url: url || window.location.href,
        object,
        feedback_text: feedbackText,
      })
      setSubmitted(true)
    } catch (err) {
      setError(err.message || t('feedback.submitError'))
    } finally {
      setSubmitting(false)
    }
  }

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 px-container-padding py-section-gap"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget && !submitting) onClose()
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-container-lowest p-container-padding shadow-lg"
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <h3
            id={titleId}
            className="font-card-title text-card-title text-primary"
          >
            {t('feedback.title')}
          </h3>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="-mr-1 -mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded text-2xl leading-none text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary disabled:opacity-50"
            aria-label={t('feedback.close')}
          >
            ×
          </button>
        </div>

        {submitted ? (
          <div className="space-y-card-gap">
            <p className="font-body-base text-body-base text-on-secondary-container" role="status">
              {t('feedback.success')}
            </p>
            <div className="flex justify-end">
              <Button type="button" variant="primary" size="sm" onClick={onClose}>
                {t('feedback.close')}
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-card-gap">
            <p className="font-metadata text-metadata text-on-surface-variant">
              {t('feedback.objectLabel')}:{' '}
              <span className="text-on-secondary-container">{object}</span>
            </p>
            <div>
              <label
                htmlFor={fieldId}
                className="mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant"
              >
                {t('feedback.textLabel')}
              </label>
              <textarea
                id={fieldId}
                value={text}
                onChange={(event) => setText(event.target.value)}
                rows={5}
                required
                disabled={submitting}
                placeholder={t('feedback.textPlaceholder')}
                className="w-full rounded-md border border-border-subtle bg-surface-container-lowest px-3 py-2 font-body-base text-body-base text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:outline-none disabled:opacity-50"
              />
            </div>
            {error ? (
              <p className="font-metadata text-metadata text-error" role="alert">
                {error}
              </p>
            ) : null}
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={onClose}
                disabled={submitting}
              >
                {t('feedback.cancel')}
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={submitting || !text.trim()}
              >
                {submitting ? t('feedback.submitting') : t('feedback.submit')}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>,
    document.body,
  )
}
