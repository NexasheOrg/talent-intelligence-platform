/**
 * The one place loading, error and empty states are rendered.
 *
 * Every page that fetches wraps its content in this. That's what makes "the API is down" look
 * the same everywhere instead of each page inventing its own spinner - and it means you can't
 * forget the empty case, which is the one reviewers always catch.
 *
 *   <DataState loading={loading} error={error} empty={!rows.length} onRetry={reload}>
 *     <Chart rows={rows} />
 *   </DataState>
 */

import type { ReactNode } from 'react'

type Props = {
  loading: boolean
  error: string | null
  /** True when the request succeeded but there is nothing to show. */
  empty?: boolean
  emptyMessage?: string
  onRetry?: () => void
  children: ReactNode
}

export function DataState({
  loading,
  error,
  empty = false,
  emptyMessage = 'No data for this view yet.',
  onRetry,
  children,
}: Props) {
  if (loading) {
    return (
      <div className="state" role="status" aria-live="polite">
        <span className="spinner" aria-hidden="true" />
        Loading…
      </div>
    )
  }

  if (error) {
    return (
      <div className="state state-error" role="alert">
        <p>{error}</p>
        <p className="state-hint">
          If you just started the stack, give it a few seconds. If it keeps failing, check that
          the API is running at <code>http://localhost:8000/health</code>.
        </p>
        {onRetry && (
          <button className="btn" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    )
  }

  if (empty) {
    return <div className="state state-empty">{emptyMessage}</div>
  }

  return <>{children}</>
}
