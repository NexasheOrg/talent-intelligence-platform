/**
 * Unit tests for pure functions - the cheapest tests in the codebase and the easiest to write.
 * If you're new to testing, start here: no rendering, no mocking, just input and output.
 */

import { describe, expect, it } from 'vitest'

import { formatDays, formatNumber, formatPercent, formatShortDate, parseSkills } from './format'

describe('formatNumber', () => {
  it('adds thousands separators', () => {
    expect(formatNumber(43120)).toBe('43,120')
  })

  it('shows a dash rather than "null" when there is no value', () => {
    expect(formatNumber(null)).toBe('-')
    expect(formatNumber(undefined)).toBe('-')
  })

  it('does not turn a real zero into a dash', () => {
    expect(formatNumber(0)).toBe('0')
  })
})

describe('formatPercent', () => {
  it('keeps one decimal by default', () => {
    expect(formatPercent(72.44)).toBe('72.4%')
    expect(formatPercent(72.46)).toBe('72.5%')
  })

  it('can drop the decimal', () => {
    expect(formatPercent(72.44, 0)).toBe('72%')
  })

  // Worth knowing before you write an assertion with a .x5 value: 72.35 has no exact binary
  // representation, so toFixed(1) rounds it *down* to 72.3. That's JavaScript, not a bug here.
  // Pick unambiguous numbers in tests rather than trying to pin down the halfway case.
  it('does not promise anything at an exact halfway value', () => {
    expect(formatPercent(72.35)).toBe('72.3%')
  })
})

describe('formatShortDate', () => {
  it('drops the year, which is noise on a narrow axis', () => {
    expect(formatShortDate('2026-05-04')).toBe('4 May')
  })

  it('passes through anything it cannot parse instead of showing "Invalid Date"', () => {
    expect(formatShortDate('not-a-date')).toBe('not-a-date')
  })
})

describe('parseSkills', () => {
  it('splits the pipe-separated skills the gold layer stores', () => {
    expect(parseSkills('Java|Python|SQL')).toEqual(['Java', 'Python', 'SQL'])
  })

  it('returns nothing for an empty string rather than one empty skill', () => {
    expect(parseSkills('')).toEqual([])
  })
})

describe('formatDays', () => {
  it('marks a consultant with no bench record rather than showing 0 days', () => {
    expect(formatDays(null)).toBe('-')
    expect(formatDays(42)).toBe('42d')
  })
})
