/**
 * Two-series stacked column chart - part-to-whole over time.
 *
 * Used for billable vs bench hours: they add up to capacity, so stacking is honest here. Don't
 * reach for this to compare two unrelated measures; stacking implies the parts belong to a whole.
 *
 * Two series means a legend is required - colour alone must never be the only way to tell the
 * series apart.
 */

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { ChartTooltip } from './Tooltip'
import { AXIS_LINE, CHART_MARGIN, GRID, SEGMENT_GAP, SERIES_1, SERIES_2, TICK } from './theme'

type Series = { key: string; name: string }

type Props<T> = {
  data: T[]
  xKey: keyof T & string
  /** Bottom of the stack first. Max two - a third series needs a different form. */
  series: [Series, Series]
  formatValue?: (value: number) => string
  formatX?: (value: string) => string
  height?: number
}

export function StackedBars<T extends Record<string, unknown>>({
  data,
  xKey,
  series,
  formatValue = String,
  formatX = String,
  height = 260,
}: Props<T>) {
  const colors = [SERIES_1, SERIES_2]

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={CHART_MARGIN}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={TICK}
          tickLine={false}
          axisLine={AXIS_LINE}
          tickFormatter={formatX}
        />
        <YAxis tick={TICK} tickLine={false} axisLine={false} width={48} tickFormatter={formatValue} />
        <Tooltip
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
          content={<ChartTooltip formatter={formatValue} labelFormatter={formatX} />}
        />
        <Legend
          verticalAlign="top"
          align="left"
          height={28}
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ color: '#8ea0b0', fontSize: 12 }}
        />
        {series.map((s, index) => (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.name}
            stackId="hours"
            fill={colors[index]}
            // The stroke is the panel colour, which renders as a 2px gap between segments
            // rather than as an outline around them.
            {...SEGMENT_GAP}
            radius={index === series.length - 1 ? [4, 4, 0, 0] : undefined}
            maxBarSize={40}
            isAnimationActive={false}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
