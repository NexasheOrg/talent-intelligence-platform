/**
 * Home. The headline numbers, then where to go next.
 *
 * Deliberately shallow: the job of this page is to answer "is anything on fire?" in two seconds
 * and then get out of the way. Detail belongs on the dashboard pages.
 */

import { Link } from 'react-router-dom'

import { Card, Kpi } from '../components/Card'
import { DataState } from '../components/DataState'
import { useApi } from '../lib/api'
import { formatNumber, formatPercent } from '../lib/format'
import type { Health, Utilization } from '../lib/types'

const DASHBOARDS = [
  { to: '/utilization', name: 'Utilization & Bench', state: 'Built', note: 'Trend, hours split, bench by seniority' },
  { to: '/funnel', name: 'Placement Funnel', state: 'Built', note: 'Candidates by pipeline stage' },
  { to: '/consultants', name: 'Consultants', state: 'Built', note: 'Search, filter, risk scores' },
  { to: '/clients', name: 'Client Health', state: 'WEB-03', note: 'Revenue, margin and risk per client' },
  { to: '/billing', name: 'Timesheet & Billing', state: 'WEB-04', note: 'Missing timesheets, unbilled hours' },
  { to: '/ask', name: 'Ask your data', state: 'AI-04', note: 'Natural-language questions over the gold layer' },
]

export function OverviewPage() {
  const { data, error, loading, reload } = useApi<Utilization>('/utilization')
  const health = useApi<Health>('/health')

  return (
    <>
      <div className="page-head">
        <h1>Overview</h1>
        <p className="sub">
          Talent &amp; delivery at a glance. All figures come from the synthetic seed data - no
          real or customer data ever runs through here.
        </p>
      </div>

      <DataState loading={loading} error={error} onRetry={reload}>
        {data && (
          <section className="kpis">
            <Kpi label="Utilization" value={formatPercent(data.utilization_pct)} />
            <Kpi label="Consultants" value={formatNumber(data.total_consultants)} />
            <Kpi label="On bench" value={formatNumber(data.consultants_on_bench)} />
            <Kpi
              label="Bench hours"
              value={formatNumber(data.bench_hours)}
              hint="hours paid for, not billed"
            />
          </section>
        )}
      </DataState>

      <Card title="Dashboards" subtitle="What exists today, and which task covers the rest">
        <ul className="nav-cards">
          {DASHBOARDS.map((dashboard) => (
            <li key={dashboard.to}>
              <Link to={dashboard.to}>
                <span className="nav-card-name">{dashboard.name}</span>
                <span className="nav-card-note">{dashboard.note}</span>
                <span
                  className={`nav-card-state ${dashboard.state === 'Built' ? 'is-built' : 'is-todo'}`}
                >
                  {dashboard.state}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </Card>

      {health.data && (
        <p className="note">
          Serving from <code>{health.data.database}</code>, API v{health.data.version}. Full API
          reference at <code>http://localhost:8000/docs</code>.
        </p>
      )}
    </>
  )
}
