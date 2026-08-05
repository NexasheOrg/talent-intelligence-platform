/**
 * Utilization & Bench - the first dashboard, and the reference for the others.
 *
 * The shape to copy: fetch with `useApi`, wrap in `<DataState>`, then hand the rows to a chart
 * from `components/charts/`. A page should read as "get the data, describe the layout" - it
 * shouldn't contain fetch logic, colours, or number formatting.
 */

import { Kpi } from '../components/Card'
import { ChartCard } from '../components/ChartCard'
import { DataState } from '../components/DataState'
import { CategoryBars } from '../components/charts/CategoryBars'
import { LineTrend } from '../components/charts/LineTrend'
import { StackedBars } from '../components/charts/StackedBars'
import { useApi } from '../lib/api'
import { formatNumber, formatPercent, formatShortDate } from '../lib/format'
import type { BenchRow, Rows, TrendPoint, Utilization as UtilizationTotals } from '../lib/types'

export function UtilizationPage() {
  const totals = useApi<UtilizationTotals>('/utilization')
  const trend = useApi<Rows<TrendPoint>>('/utilization/trend')
  const bench = useApi<Rows<BenchRow>>('/bench-by-seniority')

  return (
    <>
      <div className="page-head">
        <h1>Utilization &amp; Bench</h1>
        <p className="sub">
          Of the hours we pay for, how many does a client pay us for? Synthetic data.
        </p>
      </div>

      <DataState loading={totals.loading} error={totals.error} onRetry={totals.reload}>
        {totals.data && (
          <section className="kpis">
            <Kpi
              label="Utilization"
              value={formatPercent(totals.data.utilization_pct)}
              hint="billable ÷ total hours"
            />
            <Kpi label="Consultants" value={formatNumber(totals.data.total_consultants)} />
            <Kpi
              label="On bench"
              value={formatNumber(totals.data.consultants_on_bench)}
              hint={formatPercent(
                (100 * totals.data.consultants_on_bench) / totals.data.total_consultants,
                0,
              ) + ' of headcount'}
            />
            <Kpi label="Billable hours" value={formatNumber(totals.data.billable_hours)} />
          </section>
        )}
      </DataState>

      <DataState
        loading={trend.loading}
        error={trend.error}
        empty={trend.data?.rows.length === 0}
        onRetry={trend.reload}
      >
        {trend.data && (
          <>
            <ChartCard
              title="Utilization over time"
              subtitle="Weekly, oldest first"
              rows={trend.data.rows}
              columns={[
                { header: 'Week ending', cell: (r) => r.week_ending },
                { header: 'Utilization', cell: (r) => formatPercent(r.utilization_pct), numeric: true },
              ]}
            >
              <LineTrend
                data={trend.data.rows}
                xKey="week_ending"
                yKey="utilization_pct"
                seriesName="Utilization"
                formatValue={(value) => formatPercent(value)}
                formatX={formatShortDate}
              />
            </ChartCard>

            <ChartCard
              title="Where the hours went"
              subtitle="Billable and bench hours add up to capacity each week"
              rows={trend.data.rows}
              columns={[
                { header: 'Week ending', cell: (r) => r.week_ending },
                { header: 'Billable', cell: (r) => formatNumber(r.billable_hours), numeric: true },
                { header: 'Bench', cell: (r) => formatNumber(r.bench_hours), numeric: true },
              ]}
            >
              <StackedBars
                data={trend.data.rows}
                xKey="week_ending"
                series={[
                  { key: 'billable_hours', name: 'Billable' },
                  { key: 'bench_hours', name: 'Bench' },
                ]}
                formatValue={formatNumber}
                formatX={formatShortDate}
              />
            </ChartCard>
          </>
        )}
      </DataState>

      <DataState
        loading={bench.loading}
        error={bench.error}
        empty={bench.data?.rows.length === 0}
        emptyMessage="Nobody is on the bench. Suspicious, but good."
        onRetry={bench.reload}
      >
        {bench.data && (
          <ChartCard
            title="Bench by seniority"
            subtitle="Head count currently unassigned"
            rows={bench.data.rows}
            columns={[
              { header: 'Seniority', cell: (r) => r.seniority },
              { header: 'On bench', cell: (r) => formatNumber(r.on_bench), numeric: true },
            ]}
          >
            <CategoryBars
              data={bench.data.rows}
              categoryKey="seniority"
              valueKey="on_bench"
              seriesName="On bench"
              formatValue={formatNumber}
            />
          </ChartCard>
        )}
      </DataState>
    </>
  )
}
