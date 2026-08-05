/**
 * One tooltip for every chart, so hovering feels the same everywhere.
 *
 * A tooltip enhances, it never gates: every value here is also reachable from the axis, a direct
 * label, or the chart's table view. Someone using a keyboard or a screen reader must not have to
 * hover to read a number.
 */

import type { TooltipProps } from 'recharts'

type Formatter = (value: number) => string

export function ChartTooltip({
  active,
  payload,
  label,
  formatter,
  labelFormatter,
}: TooltipProps<number, string> & {
  formatter?: Formatter
  labelFormatter?: (label: string) => string
}) {
  if (!active || !payload?.length) return null

  return (
    <div className="tooltip">
      <div className="tooltip-title">
        {labelFormatter ? labelFormatter(String(label)) : String(label)}
      </div>
      {payload.map((entry) => (
        <div className="tooltip-row" key={String(entry.dataKey)}>
          <span className="tooltip-swatch" style={{ background: entry.color }} aria-hidden="true" />
          <span className="tooltip-name">{entry.name}</span>
          <span className="tooltip-value">
            {formatter ? formatter(Number(entry.value)) : entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}
