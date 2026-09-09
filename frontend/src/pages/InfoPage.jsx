import { useTranslation } from 'react-i18next'
import MarkdownRenderer from '../components/MarkdownRenderer'
import infoEn from '../../../docs/info_en.md?raw'
import infoPt from '../../../docs/info_pt.md?raw'

export default function InfoPage() {
  const { t, i18n } = useTranslation()
  const markdown = i18n.language?.startsWith('pt') ? infoPt : infoEn

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <h1 className="font-headline-lg text-headline-xl text-primary">
        {t('info.title')}
      </h1>
      <MarkdownRenderer className="info-markdown mt-card-gap">{markdown}</MarkdownRenderer>
    </main>
  )
}
