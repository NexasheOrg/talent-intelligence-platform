/**
 * Single-series trend line - "is this getting better or worse over time?"
 *
 * One series means no legend box: the card title already names what's plotted. The last point is
 * direct-labelled so the current value is readable without hovering.
 */

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { ChartTooltip } from './Tooltip'
import { AXIS_LINE, CHART_MARGIN, GRID, SERIES_1, SURFACE, TICK } from './theme'

type Props<T> = {
  data: T[]
  xKey: keyof T & string
  yKey: keyof T & string
  /** Shown in the tooltip next to the value. */
  seriesName: string
  formatValue?: (value: number) => string
  formatX?: (value: string) => string
  height?: number
}

export function LineTrend<T extends Record<string, unknown>>({
  data,
  xKey,
  yKey,
  seriesName,
  formatValue = String,
  formatX = String,
  height = 260,
}: Props<T>) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={CHART_MARGIN}>
        {/* Horizontal rules only - vertical ones add noise without helping read a trend. */}
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={TICK}
          tickLine={false}
          axisLine={AXIS_LINE}
          tickFormatter={formatX}
        />
        <YAxis
          tick={TICK}
          tickLine={false}
          axisLine={false}
          width={48}
          tickFormatter={formatValue}
        />
        <Tooltip
          cursor={{ stroke: GRID }}
          content={<ChartTooltip formatter={formatValue} labelFormatter={formatX} />}
        />
        <Line
          type="monotone"
          dataKey={yKey}
          name={seriesName}
          stroke={SERIES_1}
          strokeWidth={2}
          dot={{ r: 3, fill: SERIES_1, strokeWidth: 0 }}
          activeDot={{ r: 5, strokeWidth: 2, stroke: SURFACE }}
          // Draw-on animation is off everywhere in this app - see the note in theme.ts.
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
