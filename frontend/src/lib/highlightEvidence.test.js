import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import {
  buildHighlightSpans,
  buildQueryHighlightSpans,
  findEvidenceRange,
  mergeHighlightSpans,
  splitTextWithHighlights,
} from './highlightEvidence.js'

describe('findEvidenceRange', () => {
  it('matches evidence case-insensitively', () => {
    const text = 'Male, pathogen-free Sprague–Dawley rats were used.'
    const range = findEvidenceRange(text, 'sprague–dawley rats')
    assert.ok(range)
    assert.equal(text.slice(range.start, range.end).toLowerCase(), 'sprague–dawley rats')
  })

  it('matches a prefix when the quote was truncated with an ellipsis', () => {
    const text =
      'occupational exposure limit of 3.5 mg/m³ CB per 8 hrs work shift (established by OSHA and NIOSH)'
    const range = findEvidenceRange(
      text,
      'occupational exposure limit of … [truncated]',
    )
    assert.ok(range)
    assert.ok(text.slice(range.start, range.end).startsWith('occupational exposure limit'))
  })
})

describe('mergeHighlightSpans', () => {
  it('merges overlapping spans', () => {
    assert.deepEqual(
      mergeHighlightSpans([
        { start: 0, end: 10 },
        { start: 5, end: 15 },
      ]),
      [{ start: 0, end: 15 }],
    )
  })
})

describe('buildHighlightSpans', () => {
  it('highlights multiple evidence fields without overlap gaps', () => {
    const text = 'rats in the nose-only inhalation chamber. Male Sprague–Dawley rats.'
    const spans = buildHighlightSpans(text, {
      route: 'nose-only inhalation chamber',
      species: 'Sprague–Dawley rats',
    })
    assert.equal(spans.length, 2)

    const parts = splitTextWithHighlights(text, spans)
    const highlighted = parts.filter((part) => part.highlighted).map((part) => part.text)
    assert.ok(highlighted.some((value) => value.includes('inhalation chamber')))
    assert.ok(highlighted.some((value) => value.includes('Sprague–Dawley rats')))
  })
})

describe('buildQueryHighlightSpans', () => {
  it('highlights each filter word case-insensitively', () => {
    const text = 'OECD skin irritation guideline'
    const spans = buildQueryHighlightSpans(text, 'Skin OECD')
    const parts = splitTextWithHighlights(text, spans)
    const highlighted = parts
      .filter((part) => part.highlighted)
      .map((part) => part.text.toLowerCase())
    assert.deepEqual(highlighted, ['oecd', 'skin'])
  })
})
