import { useEffect, useState } from 'react'

/**
 * Delay a fast-changing value so it doesn't fire a request per keystroke.
 *
 * Typing "python" into a search box is six renders. Without this, that's six API calls and the
 * results flicker as they race each other. With it, one call, 300ms after typing stops.
 */
export function useDebounced<T>(value: T, delayMs = 300) {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])

  return debounced
}
