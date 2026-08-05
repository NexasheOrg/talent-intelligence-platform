/**
 * Display formatting.
 *
 * Numbers on a dashboard are read at a glance, so they get thousands separators and a fixed
 * number of decimals. Keep formatting here rather than inline in components - it's the only way
 * "43,120" doesn't end up as "43120" on one page and "43.1k" on another.
 */

const NUMBER = new Intl.NumberFormat('en-US')

export function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) return '-'
  return NUMBER.format(value)
}

export function formatPercent(value: number | null | undefined, decimals = 1) {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(decimals)}%`
}

/** "2026-05-04" -> "4 May". Charts have narrow axes; the year is usually noise. */
export function formatShortDate(iso: string) {
  const parsed = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(parsed.getTime())) return iso
  return parsed.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

export function formatDays(value: number | null | undefined) {
  if (value === null || value === undefined) return '-'
  return `${formatNumber(value)}d`
}

/** "Java|Python|SQL" -> ["Java", "Python", "SQL"]. The gold layer stores skills pipe-separated. */
export function parseSkills(skills: string) {
  return skills.split('|').filter(Boolean)
}

export function titleCase(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1)
}
