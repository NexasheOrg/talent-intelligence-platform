/**
 * A placeholder for a dashboard nobody has built yet.
 *
 * This is deliberate, not laziness. An unbuilt page that says *what to build, which endpoint to
 * call, and which existing file to copy* is a better brief than a ticket, because you find it
 * while looking at the product. Delete the route's `<ComingSoon>` when you build the real thing.
 */

import { Link } from 'react-router-dom'

type Props = {
  /** Matches an entry in docs/TASKS.md, e.g. "WEB-03". */
  taskId: string
  title: string
  /** One sentence: what should this page answer? */
  purpose: string
  /** API path it needs. Mark clearly if it doesn't exist yet. */
  endpoint: string
  endpointExists: boolean
  /** An existing file that already does something close enough to copy. */
  copyFrom: string
  steps: string[]
}

export function ComingSoon({
  taskId,
  title,
  purpose,
  endpoint,
  endpointExists,
  copyFrom,
  steps,
}: Props) {
  return (
    <>
      <div className="page-head">
        <h1>{title}</h1>
        <p className="sub">{purpose}</p>
      </div>

      <section className="panel todo">
        <p className="todo-badge">Not built yet · task {taskId}</p>
        <h2>This page is someone's task. Possibly yours.</h2>

        <ol className="todo-steps">
          {steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>

        <dl className="todo-facts">
          <div>
            <dt>Data it needs</dt>
            <dd>
              <code>{endpoint}</code>{' '}
              {endpointExists ? (
                <span className="ok">already exists</span>
              ) : (
                <span className="warn">you'll need to build this too</span>
              )}
            </dd>
          </div>
          <div>
            <dt>Closest thing to copy</dt>
            <dd>
              <code>{copyFrom}</code>
            </dd>
          </div>
          <div>
            <dt>Full brief</dt>
            <dd>
              <code>docs/tasks/{taskId}-*.md</code>
            </dd>
          </div>
        </dl>

        <p className="todo-foot">
          Stuck for more than 15 minutes? Ask in the team chat. That's expected, not a failure.{' '}
          <Link to="/utilization">See a finished page for reference →</Link>
        </p>
      </section>
    </>
  )
}
