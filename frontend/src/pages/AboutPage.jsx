import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import ContactModal from '../components/ContactModal'
import MarkdownRenderer from '../components/MarkdownRenderer'
import aboutEn from '../../../docs/about_en.md?raw'
import aboutPt from '../../../docs/about_pt.md?raw'

export default function AboutPage() {
  const { t, i18n } = useTranslation()
  const [contactOpen, setContactOpen] = useState(false)
  const markdown = i18n.language?.startsWith('pt') ? aboutPt : aboutEn

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <h1 className="font-headline-lg text-headline-xl text-primary">
        {t('about.title')}
      </h1>
      <MarkdownRenderer className="about-markdown mt-card-gap">{markdown}</MarkdownRenderer>
      <p className="mt-section-gap font-body-base text-body-base text-on-surface-variant">
        {t('about.contactPrompt')}{' '}
        <button
          type="button"
          onClick={() => setContactOpen(true)}
          className="text-primary underline underline-offset-2 hover:opacity-80"
        >
          {t('about.contactLink')}
        </button>
      </p>
      {contactOpen ? <ContactModal onClose={() => setContactOpen(false)} /> : null}
    </main>
  )
}
