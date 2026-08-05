/**
 * Component tests: render it, then assert what a user would actually see.
 *
 * Note what's *not* here - no assertions about internal state or prop names. Tests that reach
 * into a component's internals break every time you refactor, without ever catching a real bug.
 */

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { DataState } from './DataState'

describe('DataState', () => {
  it('shows the children when there is data', () => {
    render(
      <DataState loading={false} error={null}>
        <p>the chart</p>
      </DataState>,
    )
    expect(screen.getByText('the chart')).toBeInTheDocument()
  })

  it('hides the children while loading', () => {
    render(
      <DataState loading error={null}>
        <p>the chart</p>
      </DataState>,
    )
    expect(screen.queryByText('the chart')).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Loading')
  })

  it('reports an error as an alert, so screen readers announce it', () => {
    render(
      <DataState loading={false} error="Could not reach the API.">
        <p>the chart</p>
      </DataState>,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('Could not reach the API.')
    expect(screen.queryByText('the chart')).not.toBeInTheDocument()
  })

  it('offers a retry button only when there is something to retry with', () => {
    const onRetry = vi.fn()
    const { rerender } = render(
      <DataState loading={false} error="boom">
        <p>the chart</p>
      </DataState>,
    )
    expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument()

    rerender(
      <DataState loading={false} error="boom" onRetry={onRetry}>
        <p>the chart</p>
      </DataState>,
    )
    screen.getByRole('button', { name: /try again/i }).click()
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('distinguishes "no results" from "still loading"', () => {
    render(
      <DataState loading={false} error={null} empty emptyMessage="No consultants match.">
        <p>the chart</p>
      </DataState>,
    )
    expect(screen.getByText('No consultants match.')).toBeInTheDocument()
  })
})
