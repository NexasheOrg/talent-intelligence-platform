/**
 * A panel that holds a chart, plus a **table view** of the same numbers.
 *
 * The table isn't decoration. A chart encodes values as position and colour, which excludes
 * anyone using a screen reader and anyone who needs to read an exact figure. Every chart in this
 * app therefore ships with its table twin behind a toggle. Keep it that way.
 */

import { useState, type ReactNode } from 'react'

type Column<T> = {
  header: string
  /** Cell value. Return a string - the table is for reading exact numbers. */
  cell: (row: T) => string
  numeric?: boolean
}

type Props<T> = {
  title: string
  subtitle?: string
  rows: T[]
  columns: Column<T>[]
  children: ReactNode
}

export function ChartCard<T>({ title, subtitle, rows, columns, children }: Props<T>) {
  const [showTable, setShowTable] = useState(false)

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          {subtitle && <p className="panel-sub">{subtitle}</p>}
        </div>
        <button
          className="btn btn-ghost"
          onClick={() => setShowTable((open) => !open)}
          aria-pressed={showTable}
        >
          {showTable ? 'Chart' : 'Table'}
        </button>
      </div>

      {showTable ? (
        <div className="table-scroll">
          <table className="table">
            <caption className="sr-only">{title}</caption>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.header} className={column.numeric ? 'num' : undefined}>
                    {column.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td key={column.header} className={column.numeric ? 'num' : undefined}>
                      {column.cell(row)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        children
      )}
    </section>
  )
}
