/**
 * The only place in the web app that calls `fetch`.
 *
 * Why one place: every page then gets the same error handling, the same loading behaviour, and
 * the same base URL. If you find yourself writing `fetch(` in a component, use `useApi` instead.
 *
 * Requests go to a relative `/api/...` path, never to `http://localhost:8000`. In Docker, nginx
 * forwards `/api/` to the API container; in `npm run dev`, Vite's proxy does the same. Hardcoding
 * the port would break one of those two.
 */

import { useCallback, useEffect, useState } from 'react'

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/** Build `/api/consultants?page=2&status=bench`, skipping empty params. */
export function apiUrl(path: string, params?: Record<string, string | number | undefined | null>) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined && value !== null && value !== '') query.set(key, String(value))
  }
  const qs = query.toString()
  return `/api${path}${qs ? `?${qs}` : ''}`
}

export async function getJson<T>(path: string, params?: Parameters<typeof apiUrl>[1]): Promise<T> {
  let response: Response
  try {
    response = await fetch(apiUrl(path, params))
  } catch {
    // fetch only rejects when the request never reached a server at all.
    throw new ApiError('Could not reach the API. Is the stack running?', 0)
  }
  if (!response.ok) {
    throw new ApiError(`The API returned ${response.status} for ${path}`, response.status)
  }
  return (await response.json()) as T
}

export type ApiState<T> = {
  data: T | null
  error: string | null
  loading: boolean
  reload: () => void
}

/**
 * Fetch JSON from the API and track loading/error state.
 *
 *   const { data, error, loading } = useApi<Utilization>('/utilization')
 *
 * `params` is compared by value, so you can pass an object literal without causing a loop.
 * Pair this with `<DataState>` so every page reports problems the same way.
 */
export function useApi<T>(path: string, params?: Parameters<typeof apiUrl>[1]): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [nonce, setNonce] = useState(0)

  const key = JSON.stringify(params ?? {})

  const reload = useCallback(() => setNonce((n) => n + 1), [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    getJson<T>(path, JSON.parse(key))
      .then((result) => {
        if (!cancelled) setData(result)
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : String(cause))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    // Runs if the params change or the component unmounts mid-request, so a slow
    // response can't overwrite a newer one.
    return () => {
      cancelled = true
    }
  }, [path, key, nonce])

  return { data, error, loading, reload }
}
