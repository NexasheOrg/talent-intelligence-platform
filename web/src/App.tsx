/**
 * App shell: the nav down the side, the routed page in the middle.
 *
 * To add a dashboard: write the page in `pages/`, add a `<Route>` below, and add it to `NAV`.
 * That's the whole ceremony - three lines and a file.
 */

import { NavLink, Route, Routes } from 'react-router-dom'

import { ComingSoon } from './pages/ComingSoon'
import { ConsultantsPage } from './pages/Consultants'
import { FunnelPage } from './pages/Funnel'
import { OverviewPage } from './pages/Overview'
import { UtilizationPage } from './pages/Utilization'

const NAV = [
  { to: '/', label: 'Overview', end: true },
  { to: '/utilization', label: 'Utilization & Bench' },
  { to: '/funnel', label: 'Placement Funnel' },
  { to: '/consultants', label: 'Consultants' },
  { to: '/clients', label: 'Client Health', todo: true },
  { to: '/billing', label: 'Timesheet & Billing', todo: true },
  { to: '/ask', label: 'Ask your data', todo: true },
]

export default function App() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">TIP</span>
          <span className="brand-sub">Talent &amp; Delivery Intelligence</span>
        </div>
        <nav>
          <ul>
            {NAV.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => (isActive ? 'is-active' : undefined)}
                >
                  {item.label}
                  {item.todo && <span className="nav-todo" title="Not built yet">todo</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <p className="sidebar-foot">Synthetic data only. Never real customer records.</p>
      </aside>

      <main className="content">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/utilization" element={<UtilizationPage />} />
          <Route path="/funnel" element={<FunnelPage />} />
          <Route path="/consultants" element={<ConsultantsPage />} />

          {/* Unbuilt dashboards. Each one is a task; replace the element when you build it. */}
          <Route
            path="/clients"
            element={
              <ComingSoon
                taskId="WEB-03"
                title="Client Health"
                purpose="Which clients are growing, which are shrinking, and which are at risk?"
                endpoint="/api/clients/health"
                endpointExists={false}
                copyFrom="web/src/pages/Utilization.tsx"
                steps={[
                  'Build the API endpoint first (task API-03) so there is data to draw.',
                  'Add a KPI row: active clients, total margin, clients with no placements this quarter.',
                  'Add a table of clients sorted by margin, using the pattern in pages/Consultants.tsx.',
                  'Add a bar chart of margin by client tier with CategoryBars.',
                ]}
              />
            }
          />
          <Route
            path="/billing"
            element={
              <ComingSoon
                taskId="WEB-04"
                title="Timesheet & Billing"
                purpose="Are hours being logged, approved and billed - or leaking?"
                endpoint="/api/billing/summary"
                endpointExists={false}
                copyFrom="web/src/pages/Utilization.tsx"
                steps={[
                  'Agree the response shape with whoever owns API-04 before either of you writes code.',
                  'Show missing timesheets for the most recent week as the headline number.',
                  'Add a trend of billed vs unbilled hours using LineTrend or StackedBars.',
                ]}
              />
            }
          />
          <Route
            path="/ask"
            element={
              <ComingSoon
                taskId="AI-04"
                title="Ask your data"
                purpose="Answer plain-English questions over the gold layer, and show the SQL used."
                endpoint="/api/assistant/ask"
                endpointExists={false}
                copyFrom="ai-assistant/assistant/service.py"
                steps={[
                  'The assistant service already answers a few question templates - run it first and see.',
                  'Build a single input box that posts the question and renders the answer.',
                  'Always show the generated SQL next to the answer. An answer nobody can check is not an answer.',
                ]}
              />
            }
          />

          <Route
            path="*"
            element={
              <div className="page-head">
                <h1>Page not found</h1>
                <p className="sub">That route doesn't exist. Check the nav on the left.</p>
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  )
}
