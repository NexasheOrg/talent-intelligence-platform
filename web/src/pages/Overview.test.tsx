/**
 * Page test: fake the API, render the page, assert the numbers land in the right place.
 *
 * `fetch` is stubbed rather than the API being called for real, so this runs in CI with no
 * database and no containers. The trade-off is that it can't catch a shape mismatch between the
 * API and `lib/types.ts` - that's what the Python tests in `api/tests/` are for.
 *
 * Copy this file when you build a new page.
 */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { OverviewPage } from './Overview'

const UTILIZATION = {
  total_consultants: 300,
  consultants_on_bench: 88,
  billable_hours: 43120,
  bench_hours: 12880,
  utilization_pct: 77.0,
}

const HEALTH = { status: 'ok', database: 'sqlite', version: '0.2.0' }

function mockApi(routes: Record<string, unknown>) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string) => {
      const match = Object.keys(routes).find((path) => url.startsWith(path))
      if (!match) throw new Error(`unexpected request: ${url}`)
      return { ok: true, status: 200, json: async () => routes[match] } as Response
    }),
  )
}

function renderPage() {
  return render(
    <MemoryRouter>
      <OverviewPage />
    </MemoryRouter>,
  )
}

afterEach(() => vi.unstubAllGlobals())

describe('OverviewPage', () => {
  it('shows the headline numbers once they load', async () => {
    mockApi({ '/api/utilization': UTILIZATION, '/api/health': HEALTH })
    renderPage()

    expect(await screen.findByText('77.0%')).toBeInTheDocument()
    expect(screen.getByText('300')).toBeInTheDocument()
    expect(screen.getByText('12,880')).toBeInTheDocument()
  })

  it('links to every dashboard, built or not', async () => {
    mockApi({ '/api/utilization': UTILIZATION, '/api/health': HEALTH })
    renderPage()

    expect(await screen.findByRole('link', { name: /Utilization & Bench/ })).toHaveAttribute(
      'href',
      '/utilization',
    )
    expect(screen.getByRole('link', { name: /Client Health/ })).toHaveAttribute('href', '/clients')
  })

  it('marks the dashboards that are still someone task', async () => {
    mockApi({ '/api/utilization': UTILIZATION, '/api/health': HEALTH })
    renderPage()

    expect(await screen.findByText('WEB-03')).toBeInTheDocument()
  })

  it('tells the user the API is unreachable instead of rendering an empty page', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('failed to fetch') }))
    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not reach the api/i)
  })
})
