/**
 * Consultant directory - the reference page for **filters, a table, and pagination**.
 *
 * Three things here are worth copying rather than reinventing:
 *   1. Filters sit in one row above everything they scope, never inside a card.
 *   2. The search box is debounced, so typing doesn't fire a request per keystroke.
 *   3. On refetch the previous rows stay on screen dimmed, instead of collapsing to a spinner
 *      and making the page jump.
 */

import { useEffect, useState } from 'react'

import { DataState } from '../components/DataState'
import { Pill } from '../components/Card'
import { ConsultantDetail } from '../components/ConsultantDetail'
import { useApi } from '../lib/api'
import { formatDays, formatNumber, parseSkills } from '../lib/format'
import { useDebounced } from '../lib/useDebounced'
import type { ConsultantPage as ConsultantPageData } from '../lib/types'

const PAGE_SIZE = 20
const STATUSES = ['placed', 'bench', 'onboarding']
const SENIORITIES = ['Junior', 'Mid', 'Senior', 'Lead']

function statusTone(status: string) {
  if (status === 'placed') return 'good' as const
  if (status === 'bench') return 'warn' as const
  return 'neutral' as const
}

export function ConsultantsPage() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [seniority, setSeniority] = useState('')
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState<number | null>(null)

  const q = useDebounced(search)

  // Page 7 of an unfiltered list is meaningless once a filter cuts the results to 12.
  useEffect(() => setPage(1), [q, status, seniority])

  const { data, error, loading, reload } = useApi<ConsultantPageData>('/consultants', {
    q,
    status,
    seniority,
    page,
    page_size: PAGE_SIZE,
  })

  const firstLoad = loading && !data

  return (
    <>
      <div className="page-head">
        <h1>Consultants</h1>
        <p className="sub">Everyone on the bench, on a project, or onboarding. Synthetic data.</p>
      </div>

      <div className="filters">
        <label className="field">
          <span>Search</span>
          <input
            type="search"
            value={search}
            placeholder="Name or skill, e.g. Python"
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>

        <label className="field">
          <span>Status</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All</option>
            {STATUSES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Seniority</span>
          <select value={seniority} onChange={(event) => setSeniority(event.target.value)}>
            <option value="">All</option>
            {SENIORITIES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        {data && (
          <p className="filter-count">
            {formatNumber(data.total)} {data.total === 1 ? 'consultant' : 'consultants'}
          </p>
        )}
      </div>

      <DataState
        loading={firstLoad}
        error={error}
        empty={data?.rows.length === 0}
        emptyMessage="No consultants match those filters."
        onRetry={reload}
      >
        {data && (
          <div className={loading ? 'is-refetching' : undefined}>
            <div className="table-scroll panel">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Seniority</th>
                    <th>Location</th>
                    <th>Skills</th>
                    <th>Status</th>
                    <th className="num">On bench</th>
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((row) => (
                    <tr
                      key={row.consultant_id}
                      className={selected === row.consultant_id ? 'is-selected' : undefined}
                    >
                      <td>
                        <button
                          className="link"
                          onClick={() =>
                            setSelected(selected === row.consultant_id ? null : row.consultant_id)
                          }
                        >
                          {row.name}
                        </button>
                      </td>
                      <td>{row.seniority}</td>
                      <td>{row.location}</td>
                      <td className="skills">
                        {parseSkills(row.skills).slice(0, 3).map((skill) => (
                          <span className="chip" key={skill}>
                            {skill}
                          </span>
                        ))}
                      </td>
                      <td>
                        <Pill tone={statusTone(row.status)}>{row.status}</Pill>
                      </td>
                      <td className="num">{formatDays(row.days_on_bench)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <nav className="pager" aria-label="Pagination">
              <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Previous
              </button>
              <span className="pager-label">
                Page {data.page} of {Math.max(data.pages, 1)}
              </span>
              <button
                className="btn"
                disabled={page >= data.pages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </nav>
          </div>
        )}
      </DataState>

      {selected !== null && (
        <ConsultantDetail consultantId={selected} onClose={() => setSelected(null)} />
      )}
    </>
  )
}
