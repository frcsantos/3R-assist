import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import LangToggle from './LangToggle'
import { currentLanguage, setLanguage } from '../lib/i18n'

const routes = [
  { key: 'analyze', to: '/' },
  { key: 'explore', to: '/explore' },
  { key: 'literature', to: '/literature-search' },
  { key: 'glossary', to: '/glossary' },
  { key: 'info', to: '/info' },
]

export default function TopNav() {
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-50 border-b border-border-subtle bg-background">
      <div className="mx-auto flex h-nav max-w-content items-center justify-between px-container-padding">
        <div className="flex items-center gap-8">
          <NavLink
            to="/"
            className="font-nav-logo text-nav-logo font-medium text-primary"
          >
            3R Assist
          </NavLink>
          <nav className="hidden items-center gap-6 md:flex" aria-label="Main">
            {routes.map((route) => (
              <NavLink
                key={route.key}
                to={route.to}
                end={route.to === '/'}
                className={({ isActive }) =>
                  isActive
                    ? 'border-b-2 border-primary pb-1 font-nav-link text-nav-link font-medium text-primary'
                    : 'font-nav-link text-nav-link text-on-secondary-container transition-colors hover:text-primary'
                }
              >
                {t(`nav.${route.key}`)}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <LangToggle
            value={currentLanguage()}
            onChange={(nextLang) => {
              void setLanguage(nextLang)
            }}
          />
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              isActive
                ? 'rounded-md border border-primary bg-surface-container-low px-4 py-2 font-nav-link text-nav-link font-medium text-primary'
                : 'rounded-md border border-border-emphasis bg-surface-container-lowest px-4 py-2 font-nav-link text-nav-link text-on-surface transition-colors hover:bg-surface-container'
            }
          >
            {t('nav.admin')}
          </NavLink>
          <button
            type="button"
            className="rounded-md bg-primary px-4 py-2 font-nav-link text-nav-link text-on-primary transition-opacity hover:opacity-90"
          >
            {t('nav.signIn')}
          </button>
        </div>
      </div>
    </header>
  )
}
