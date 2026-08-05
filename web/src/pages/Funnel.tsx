/**
 * Placement funnel - how candidates move from submitted to placed.
 *
 * The stages are genuinely ordered, so this is one of the few charts allowed a colour ramp; the
 * ramp brightens toward "placed" so the outcome that matters is the most prominent mark.
 * "Rejected" is not a stage of the funnel - it's what falls out of it - so it's rendered in the
 * de-emphasis grey rather than given a place on the ramp.
 */

import { ChartCard } from '../components/ChartCard'
import { DataState } from '../components/DataState'
import { Kpi } from '../components/Card'
import { CategoryBars } from '../components/charts/CategoryBars'
import { DE_EMPHASIS, ORDINAL } from '../components/charts/theme'
import { useApi } from '../lib/api'
import { formatNumber, formatPercent, titleCase } from '../lib/format'
import type { FunnelResponse } from '../lib/types'

const PROGRESSION = ['submitted', 'interview', 'offer', 'placed']

/** Brightest at the end of the funnel, grey for anything outside it. */
function colorForStage(stage: string) {
  const position = PROGRESSION.indexOf(stage)
  if (position === -1) return DE_EMPHASIS
  return [...ORDINAL].reverse()[position] ?? DE_EMPHASIS
}

export function FunnelPage() {
  const { data, error, loading, reload } = useApi<FunnelResponse>('/funnel')

  const rows = (data?.rows ?? []).map((row) => ({ ...row, label: titleCase(row.stage) }))
  const placed = rows.find((row) => row.stage === 'placed')

  return (
    <>
      <div className="page-head">
        <h1>Placement Funnel</h1>
        <p className="sub">Candidates by pipeline stage. Synthetic data.</p>
      </div>

      <DataState loading={loading} error={error} empty={rows.length === 0} onRetry={reload}>
        {data && (
          <>
            <section className="kpis">
              <Kpi label="Candidates in pipeline" value={formatNumber(data.total)} />
              <Kpi label="Placed" value={formatNumber(placed?.count ?? 0)} />
              <Kpi
                label="Placed share"
                value={formatPercent(placed?.pct_of_total ?? 0)}
                hint="of everyone in the pipeline"
              />
            </section>

            <ChartCard
              title="Candidates by stage"
              subtitle="A distribution across current stages, not stage-to-stage conversion - see the note below"
              rows={rows}
              columns={[
                { header: 'Stage', cell: (r) => r.label },
                { header: 'Candidates', cell: (r) => formatNumber(r.count), numeric: true },
                { header: 'Share', cell: (r) => formatPercent(r.pct_of_total), numeric: true },
              ]}
            >
              <CategoryBars
                data={rows}
                categoryKey="label"
                valueKey="count"
                seriesName="Candidates"
                colors={rows.map((row) => colorForStage(row.stage))}
                formatValue={formatNumber}
                height={260}
              />
            </ChartCard>

            <p className="note">
              <strong>Read this before quoting these numbers.</strong> The gold layer stores one
              row per candidate and job with a single <em>current</em> stage, so this is a
              snapshot of where people are, not a conversion rate. True conversion needs the full
              stage history per candidate - that's task <code>DATA-03</code>.
            </p>
          </>
        )}
      </DataState>
    </>
  )
}
