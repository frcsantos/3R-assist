import {
  buildQueryHighlightSpans,
  splitTextWithHighlights,
} from '../lib/highlightEvidence'

const MARK_CLASS =
  'rounded-sm bg-yellow-200 px-0.5 text-inherit'

export default function HighlightedText({ text, query }) {
  if (text == null) return null
  const value = String(text)
  if (!value) return null
  if (!query?.trim()) return value

  const parts = splitTextWithHighlights(
    value,
    buildQueryHighlightSpans(value, query),
  )

  return parts.map((part, index) =>
    part.highlighted ? (
      <mark key={index} className={MARK_CLASS}>
        {part.text}
      </mark>
    ) : (
      part.text
    ),
  )
}
