/**
 * Shared chart theme. Every chart imports from here - do not hardcode a colour in a chart file.
 *
 * These hexes are not a taste call. They were checked with a colour-vision-deficiency validator
 * against this app's actual panel surface (#17222e):
 *
 *   SERIES_1 + SERIES_2   worst adjacent CVD ΔE 26.8 (target >= 8), normal-vision ΔE 31.8
 *   ORDINAL ramp          monotone lightness, every step >= 2:1 against the surface
 *   DE_EMPHASIS gray      >= 3:1 against the surface
 *
 * If you add a third series, don't invent a hue - take the next slot below, which comes from the
 * same validated set, and re-check. If you change the panel background in styles.css, these need
 * re-validating against the new surface.
 *
 * Rules worth knowing before you build a chart here:
 *   - One series = one colour. Never colour bars darker-because-bigger; that just re-encodes
 *     the bar length and buries the free colour channel.
 *   - An ordered scale (funnel stages, tiers) may use ORDINAL. Nominal categories may not.
 *   - Never put two different y-scales on one chart. Two measures = two charts.
 */

export const SURFACE = '#17222e'
export const INK_MUTED = '#8ea0b0'
export const GRID = '#233240'

/** Categorical slots, in fixed order. Slot 1 is the default for a single-series chart. */
export const SERIES_1 = '#3987e5' // blue
export const SERIES_2 = '#d95926' // orange
export const SERIES_3 = '#199e70' // aqua

/** For the "one series matters, the rest are context" case, and for out-of-scale categories. */
export const DE_EMPHASIS = '#898781'

/** Ordered scales only, light -> dark. Reversed at the call site when brighter should mean later. */
export const ORDINAL = ['#cde2fb', '#9ec5f4', '#5598e7', '#1c5cab']

/** Axis ticks use tabular figures so the digits line up as values change. */
export const TICK = {
  fill: INK_MUTED,
  fontSize: 12,
  style: { fontVariantNumeric: 'tabular-nums' as const },
}

export const AXIS_LINE = { stroke: GRID }

/** Recharts draws the "gap" between stacked segments as a surface-coloured stroke. */
export const SEGMENT_GAP = { stroke: SURFACE, strokeWidth: 2 }

export const CHART_MARGIN = { top: 8, right: 16, bottom: 4, left: 4 }

/**
 * Every chart here passes `isAnimationActive={false}`. Three reasons, in order of how much they
 * will bite you:
 *
 *  1. Recharts animates a line by growing its dash offset and a bar by growing its height. If
 *     requestAnimationFrame doesn't run - a background tab, a headless browser, some remote
 *     desktop setups - the animation never advances and the chart renders with **axes but no
 *     marks**. It looks exactly like a data bug, and people lose an afternoon to it.
 *  2. These charts refetch when a filter changes. Re-animating from zero on every keystroke is
 *     noise, not polish.
 *  3. Tests and screenshots become deterministic.
 */

