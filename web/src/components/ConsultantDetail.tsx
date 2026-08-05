/**
 * Detail panel for one consultant, including their attrition-risk score.
 *
 * The risk number is never shown on its own. A score with no explanation is a number nobody
 * trusts and nobody can act on, so the factors that produced it are listed underneath, largest
 * first, along with which model produced it.
 *
 * Today that model is a hand-written heuristic (`api/app/risk.py`). When the trained model lands
 * (task ML-02) the shape doesn't change and this component doesn't either - only the `model`
 * line will read differently.
 */

import { Pill } from './Card'
import { DataState } from './DataState'
import { useApi } from '../lib/api'
import { formatDays, formatNumber, parseSkills } from '../lib/format'
import type { ConsultantDetail as Detail } from '../lib/types'

function riskTone(band: string) {
  if (band === 'high') return 'bad' as const
  if (band === 'medium') return 'warn' as const
  return 'good' as const
}

export function ConsultantDetail({
  consultantId,
  onClose,
}: {
  consultantId: number
  onClose: () => void
}) {
  const { data, error, loading, reload } = useApi<Detail>(`/consultants/${consultantId}`)

  return (
    <section className="panel detail">
      <div className="panel-head">
        <h2>{data?.name ?? 'Consultant'}</h2>
        <button className="btn btn-ghost" onClick={onClose}>
          Close
        </button>
      </div>

      <DataState loading={loading} error={error} onRetry={reload}>
        {data && (
          <div className="detail-grid">
            <dl className="facts">
              <div>
                <dt>Seniority</dt>
                <dd>{data.seniority}</dd>
              </div>
              <div>
                <dt>Location</dt>
                <dd>{data.location}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{data.status}</dd>
              </div>
              <div>
                <dt>Cost rate</dt>
                <dd>${formatNumber(data.cost_rate)}/hr</dd>
              </div>
              <div>
                <dt>Hired</dt>
                <dd>{data.hire_date}</dd>
              </div>
              <div>
                <dt>On bench</dt>
                <dd>{formatDays(data.days_on_bench)}</dd>
              </div>
            </dl>

            <div className="risk">
              <div className="risk-head">
                <span className="risk-score">{(data.risk.risk_score * 100).toFixed(0)}</span>
                <Pill tone={riskTone(data.risk.band)}>{data.risk.band} attrition risk</Pill>
              </div>
              <ul className="risk-factors">
                {data.risk.factors.map((factor) => (
                  <li key={factor.label}>
                    <span>{factor.label}</span>
                    <span className="num">+{(factor.contribution * 100).toFixed(0)}</span>
                  </li>
                ))}
              </ul>
              <p className="risk-model">
                Scored by <code>{data.risk.model}</code>
              </p>
            </div>

            <div className="detail-skills">
              {parseSkills(data.skills).map((skill) => (
                <span className="chip" key={skill}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </DataState>
    </section>
  )
}
