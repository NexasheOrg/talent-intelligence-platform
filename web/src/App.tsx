import { useEffect, useState } from 'react'

type Utilization = {
  total_consultants: number
  consultants_on_bench: number
  billable_hours: number
  bench_hours: number
  utilization_pct: number
}

type BenchRow = { seniority: string; on_bench: number }

export default function App() {
  const [util, setUtil] = useState<Utilization | null>(null)
  const [bench, setBench] = useState<BenchRow[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetch('/api/utilization').then((r) => r.json()),
      fetch('/api/bench-by-seniority').then((r) => r.json()),
    ])
      .then(([u, b]) => {
        setUtil(u)
        setBench(b.rows)
      })
      .catch((e) => setError(String(e)))
  }, [])

  if (error) return <main className="wrap"><p className="err">Could not reach the API: {error}</p></main>
  if (!util) return <main className="wrap"><p>Loading…</p></main>

  const maxBench = Math.max(...bench.map((r) => r.on_bench), 1)

  return (
    <main className="wrap">
      <header>
        <h1>Talent &amp; Delivery Intelligence</h1>
        <p className="sub">Utilization &amp; Bench - from the gold layer (synthetic data)</p>
      </header>

      <section className="kpis">
        <Kpi label="Utilization" value={`${util.utilization_pct}%`} />
        <Kpi label="Consultants" value={util.total_consultants} />
        <Kpi label="On bench" value={util.consultants_on_bench} />
        <Kpi label="Billable hrs" value={util.billable_hours} />
      </section>

      <section className="panel">
        <h2>Bench by seniority</h2>
        {bench.map((r) => (
          <div className="bar-row" key={r.seniority}>
            <span className="bar-label">{r.seniority}</span>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(r.on_bench / maxBench) * 100}%` }} />
            </div>
            <span className="bar-value">{r.on_bench}</span>
          </div>
        ))}
      </section>

      <footer>M0 skeleton. Charts, filters, and more dashboards land in later milestones.</footer>
    </main>
  )
}

function Kpi({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="kpi">
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  )
}
