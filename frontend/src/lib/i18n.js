import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import pt from '../locales/pt.json'
import en from '../locales/en.json'

const STORAGE_KEY = '3r-assist.language'

function normalizeLang(lang) {
  const value = String(lang ?? '').trim().toLowerCase()
  if (value.startsWith('pt')) return 'pt'
  if (value.startsWith('en')) return 'en'
  return null
}

function langFromUrl() {
  const params = new URLSearchParams(window.location.search)
  return normalizeLang(params.get('lang'))
}

function langFromStorage() {
  try {
    return normalizeLang(window.localStorage.getItem(STORAGE_KEY))
  } catch {
    return null
  }
}

i18n.use(initReactI18next).init({
  resources: {
    pt: { translation: pt },
    en: { translation: en },
  },
  lng: langFromUrl() ?? langFromStorage() ?? 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
  react: {
    useSuspense: false,
  },
})

export function currentLanguage() {
  return (i18n.resolvedLanguage ?? i18n.language ?? 'en').split('-')[0]
}

export function setLanguage(lang) {
  const normalized = normalizeLang(lang) ?? 'en'
  try {
    window.localStorage.setItem(STORAGE_KEY, normalized)
  } catch {
    // Ignore storage errors (private mode, etc.)
  }
  return i18n.changeLanguage(normalized)
}

export default i18n
