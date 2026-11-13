import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import ContactModal from './ContactModal'
import LangToggle from './LangToggle'
import { currentLanguage, setLanguage } from '../lib/i18n'
import { isAuthEnabled } from '../lib/auth'

const routes = [
  { key: 'analyze', to: '/' },
  { key: 'explore', to: '/explore' },
  { key: 'literature', to: '/literature-search' },
  { key: 'glossary', to: '/glossary' },
  { key: 'about', to: '/about' },
]

function ContactIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" className="h-5 w-5">
      <rect
        x="2.5"
        y="4.5"
        width="15"
        height="11"
        rx="2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M3 6l7 5 7-5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function TopNav() {
  const { t } = useTranslation()
  const [authEnabled, setAuthEnabled] = useState(false)
  const [contactOpen, setContactOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    void isAuthEnabled().then((value) => {
      if (!cancelled) setAuthEnabled(value)
    })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <header className="sticky top-0 z-50 border-b border-border-subtle bg-background">
      <div className="mx-auto flex h-nav max-w-content items-center justify-between px-container-padding">
        <div className="flex items-center gap-8">
          <NavLink
            to="/"
            className="relative font-nav-logo text-[24px] font-medium leading-none text-primary"
          >
            Assist<span className="text-on-surface-variant">3R</span>
            <span className="pointer-events-none absolute -right-7 -top-2 text-[10px] font-medium uppercase leading-none tracking-wider text-on-surface-variant">
              Beta
            </span>
          </NavLink>
          <nav className="hidden items-center gap-6 md:flex" aria-label="Main">
            {routes.map((route) => (
              <NavLink
                key={route.key}
                to={route.to}
                end={route.to === '/'}
                className={({ isActive }) =>
                  isActive
                    ? 'relative font-nav-link text-nav-link font-medium text-primary after:absolute after:inset-x-0 after:-bottom-1 after:h-0.5 after:bg-primary'
                    : 'font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary'
                }
              >
                {t(`nav.${route.key}`)}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            aria-label={t('nav.contact')}
            title={t('nav.contact')}
            onClick={() => setContactOpen(true)}
            className="flex h-9 w-9 items-center justify-center rounded text-on-secondary-container transition-colors hover:bg-surface-container hover:text-primary"
          >
            <ContactIcon />
          </button>
          <LangToggle
            value={currentLanguage()}
            onChange={(nextLang) => {
              void setLanguage(nextLang)
            }}
          />
          {authEnabled && (
            <NavLink
              to="/auth"
              className={({ isActive }) =>
                isActive
                  ? 'rounded-md border border-primary bg-surface-container-low px-4 py-2 font-nav-link text-nav-link font-medium text-primary'
                  : 'rounded-md bg-primary px-4 py-2 font-nav-link text-nav-link text-on-primary transition-opacity hover:opacity-90'
              }
            >
              {t('nav.signIn')}
            </NavLink>
          )}
        </div>
      </div>
      {contactOpen ? <ContactModal onClose={() => setContactOpen(false)} /> : null}
    </header>
  )
}
