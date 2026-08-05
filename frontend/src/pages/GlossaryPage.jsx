import { useTranslation } from 'react-i18next'
import MarkdownRenderer from '../components/MarkdownRenderer'
import glossaryEn from '../../../docs/glossary_en.md?raw'
import glossaryPt from '../../../docs/glossary_pt.md?raw'

export default function GlossaryPage() {
  const { t, i18n } = useTranslation()
  const markdown = i18n.language?.startsWith('pt') ? glossaryPt : glossaryEn

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <h1 className="font-headline-lg text-headline-lg text-primary">
        {t('glossary.title')}
      </h1>
      <MarkdownRenderer className="mt-card-gap">{markdown}</MarkdownRenderer>
    </main>
  )
}
