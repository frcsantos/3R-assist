import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Navigate, useSearchParams } from 'react-router-dom'
import { isAuthEnabled, requestMagicLink, verifyMagicLink } from '../lib/auth'

export default function LoginPage() {
  const { t } = useTranslation()
  const [enabled, setEnabled] = useState(null)
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState(null)
  const [devLink, setDevLink] = useState(null)
  const [error, setError] = useState(null)
  const [searchParams] = useSearchParams()

  useEffect(() => {
    let cancelled = false
    void isAuthEnabled().then((value) => {
      if (!cancelled) setEnabled(value)
    })
    return () => {
      cancelled = true
    }
  }, [])

  const magicToken = searchParams.get('token')
  useEffect(() => {
    if (magicToken && enabled) {
      void verifyMagicLink(magicToken)
        .then(() => {
          window.location.replace('/')
        })
        .catch((err) => setError(err.message))
    }
  }, [magicToken, enabled])

  // While the flag is unknown, render nothing; once known and false, the
  // user system must not be reachable.
  if (enabled === null) return null
  if (!enabled) return <Navigate to="/" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setMessage(null)
    setDevLink(null)
    try {
      const result = await requestMagicLink(email)
      setMessage(result.message)
      setDevLink(result.dev_login_link ?? null)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="mx-auto w-full max-w-md flex-1 px-container-padding py-section-gap">
      <h1 className="font-headline-lg text-headline-xl text-primary">
        {t('auth.title')}
      </h1>
      <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('auth.subtitle')}
      </p>
      {devLink ? (
        <a
          href={devLink}
          className="mt-section-gap block rounded-md bg-primary px-4 py-2 text-center font-nav-link text-nav-link text-on-primary transition-opacity hover:opacity-90"
        >
          {t('auth.openDevLink')}
        </a>
      ) : (
        <form onSubmit={handleSubmit} className="mt-section-gap flex flex-col gap-fine-gap">
          <label htmlFor="auth-email" className="font-label text-label text-on-secondary-container">
            {t('auth.emailLabel')}
          </label>
          <input
            id="auth-email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="rounded-md border border-border-emphasis bg-surface-container-lowest px-3 py-2 font-body-base text-body-base text-on-surface"
            placeholder={t('auth.emailPlaceholder')}
          />
          <button
            type="submit"
            className="mt-fine-gap rounded-md bg-primary px-4 py-2 font-nav-link text-nav-link text-on-primary transition-opacity hover:opacity-90"
          >
            {t('auth.sendLink')}
          </button>
        </form>
      )}
      {message && (
        <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container">
          {message}
        </p>
      )}
      {error && (
        <p className="mt-fine-gap font-body-base text-body-base text-error">{error}</p>
      )}
    </main>
  )
}
