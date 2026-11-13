import { useEffect, useId, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
import Button from './Button'
import { submitFeedback } from '../lib/feedback'

const inputClass =
  'w-full rounded-md border border-border-subtle bg-surface-container-lowest px-3 py-2 font-body-base text-body-base text-on-surface placeholder:text-on-surface-variant/60 focus:border-primary focus:outline-none disabled:opacity-50'
const labelClass =
  'mb-1 block font-label-caps text-label-caps uppercase text-on-surface-variant'

export default function ContactModal({ onClose }) {
  const { t } = useTranslation()
  const titleId = useId()
  const emailId = useId()
  const messageId = useId()
  const subjectId = useId()
  const [subject, setSubject] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
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
    const body = message.trim()
    if (!body || submitting) return

    const replyTo = email.trim()
    const subjectText = subject.trim()
    const header = [subjectText && `Subject: ${subjectText}`, replyTo && `From: ${replyTo}`]
      .filter(Boolean)
      .join('\n')
    setSubmitting(true)
    setError(null)
    try {
      await submitFeedback({
        url: window.location.href,
        object: 'contact',
        feedback_text: header ? `${header}\n\n${body}` : body,
        subject: subjectText || null,
      })
      setSubmitted(true)
    } catch (err) {
      setError(err.message || t('contact.submitError'))
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
          <h3 id={titleId} className="font-card-title text-card-title text-primary">
            {t('contact.title')}
          </h3>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="-mr-1 -mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded text-2xl leading-none text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary disabled:opacity-50"
            aria-label={t('contact.close')}
          >
            ×
          </button>
        </div>

        {submitted ? (
          <div className="space-y-card-gap">
            <p className="font-body-base text-body-base text-on-secondary-container" role="status">
              {t('contact.success')}
            </p>
            <div className="flex justify-end">
              <Button type="button" variant="primary" size="sm" onClick={onClose}>
                {t('contact.close')}
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-card-gap">
            <p className="font-body-base text-body-base text-on-surface-variant">
              {t('contact.intro')}
            </p>
            <div>
              <label htmlFor={emailId} className={labelClass}>
                {t('contact.emailLabel')}
              </label>
              <input
                id={emailId}
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={submitting}
                placeholder={t('contact.emailPlaceholder')}
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor={subjectId} className={labelClass}>
                {t('contact.subjectLabel')}
              </label>
              <input
                id={subjectId}
                type="text"
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                maxLength={200}
                disabled={submitting}
                placeholder={t('contact.subjectPlaceholder')}
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor={messageId} className={labelClass}>
                {t('contact.messageLabel')}
              </label>
              <textarea
                id={messageId}
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                rows={5}
                required
                disabled={submitting}
                placeholder={t('contact.messagePlaceholder')}
                className={inputClass}
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
                {t('contact.cancel')}
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={submitting || !message.trim()}
              >
                {submitting ? t('contact.submitting') : t('contact.submit')}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>,
    document.body,
  )
}
