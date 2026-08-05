/**
 * Horizontal bars for comparing magnitude across categories.
 *
 * Horizontal, because category names ("Senior", "Data Engineer") read left-to-right and don't
 * need rotating. One series, so **every bar is the same colour** - colouring bars darker because
 * they're bigger just re-encodes the length you can already see.
 *
 * `colors` exists for the ordered case (a funnel, where stage order is real). Pass it only when
 * the categories genuinely have an order.
 */

import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { ChartTooltip } from './Tooltip'
import { CHART_MARGIN, INK_MUTED, SERIES_1, TICK } from './theme'

type Props<T> = {
  data: T[]
  categoryKey: keyof T & string
  valueKey: keyof T & string
  seriesName: string
  /** One colour per row, for ordered categories. Omit for the normal single-colour case. */
  colors?: string[]
  formatValue?: (value: number) => string
  height?: number
}

export function CategoryBars<T extends Record<string, unknown>>({
  data,
  categoryKey,
  valueKey,
  seriesName,
  colors,
  formatValue = String,
  height = 240,
}: Props<T>) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ ...CHART_MARGIN, right: 48 }}>
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey={categoryKey}
          tick={TICK}
          tickLine={false}
          axisLine={false}
          width={96}
        />
        <Tooltip
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
          content={<ChartTooltip formatter={formatValue} />}
        />
        <Bar
          dataKey={valueKey}
          name={seriesName}
          radius={[0, 4, 4, 0]}
          maxBarSize={22}
          isAnimationActive={false}
        >
          {data.map((row, index) => (
            <Cell key={index} fill={colors?.[index] ?? SERIES_1} />
          ))}
          {/* The axis is hidden, so each bar carries its own value at the end. */}
          <LabelList
            dataKey={valueKey}
            position="right"
            formatter={(value: number) => formatValue(value)}
            style={{ fill: INK_MUTED, fontSize: 12, fontVariantNumeric: 'tabular-nums' }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
