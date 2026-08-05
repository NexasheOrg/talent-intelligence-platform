/**
 * TypeScript mirrors of the API's response models.
 *
 * These are hand-kept in sync with `api/app/models.py`. If you change a shape on one side,
 * change it on the other in the same PR - a mismatch here is the single most common cause of
 * "the page renders but every number is undefined".
 *
 * The live contract is always at http://localhost:8000/docs while the API is running.
 */

export type Health = {
  status: string
  database: 'postgres' | 'sqlite'
  version: string
}

export type Utilization = {
  total_consultants: number
  consultants_on_bench: number
  billable_hours: number
  bench_hours: number
  utilization_pct: number
}

export type BenchRow = {
  seniority: string
  on_bench: number
}

export type TrendPoint = {
  week_ending: string
  billable_hours: number
  bench_hours: number
  utilization_pct: number
}

export type FunnelStage = {
  stage: string
  count: number
  pct_of_total: number
}

export type ConsultantSummary = {
  consultant_id: number
  name: string
  skills: string
  seniority: string
  location: string
  status: string
  days_on_bench: number | null
}

export type ConsultantPage = {
  rows: ConsultantSummary[]
  total: number
  page: number
  page_size: number
  pages: number
}

export type RiskFactor = {
  label: string
  contribution: number
}

export type RiskScore = {
  consultant_id: number
  risk_score: number
  band: 'low' | 'medium' | 'high'
  factors: RiskFactor[]
  model: string
}

export type ConsultantDetail = ConsultantSummary & {
  cost_rate: number
  hire_date: string
  risk: RiskScore
}

/** Endpoints that return `{ rows: [...] }` share this wrapper. */
export type Rows<T> = { rows: T[] }

export type FunnelResponse = Rows<FunnelStage> & { total: number }
