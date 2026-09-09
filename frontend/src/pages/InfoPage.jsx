import { useTranslation } from 'react-i18next'

export default function InfoPage() {
  const { t } = useTranslation()

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-container-padding py-section-gap">
      <h1 className="font-headline-lg text-headline-xl text-primary">
        {t('info.title')}
      </h1>
      <p className="mt-fine-gap font-body-base text-body-base text-on-secondary-container opacity-65">
        {t('info.placeholder')}
      </p>
    </main>
  )
}
