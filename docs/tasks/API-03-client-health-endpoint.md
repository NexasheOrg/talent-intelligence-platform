---
id: API-03
title: "api: add /api/clients/health"
module: api
labels: [api]
difficulty: core
estimate: 1-2 days
depends_on: []
---

## Why this matters

This is the data behind the Client Health dashboard (WEB-03). Revenue concentrates in a few
clients, and a client going quiet is the earliest signal that a renewal is in trouble.

## What "done" looks like

- [ ] `GET /api/clients/health` returns, per client: name, industry, tier, active placements,
      total margin per hour, days since the most recent placement started
- [ ] A summary block: total clients, total margin, how many count as "at risk"
- [ ] "At risk" is one rule, defined in **one place in the code**, with a comment saying what it
      means and that it's a judgement call
- [ ] Sorted by margin, highest first
- [ ] Response model in `models.py`
- [ ] Tests, including a client with no placements
- [ ] Runs on Postgres and SQLite

## Where to work

- `api/app/routers/clients.py`
- `api/app/models.py`
- `api/tests/`

## How to approach it

1. **Agree the response shape with whoever owns WEB-03 before you write the query.** Write it
   down in the issue. This is the single highest-value fifteen minutes in the task.
2. Start from the SQL. Get it right in one query against `dim_client`, `fact_placements` and
   `dim_job` before wrapping it in an endpoint.
3. `LEFT JOIN`, always - a client with no placements is the most interesting row on the page and
   an inner join silently deletes it.
4. Date arithmetic differs between Postgres and SQLite. Rather than fighting it, select the raw
   date and compute "days since" in Python. Boring, portable, easy to test.

## How to check it

```bash
python -m pytest api/tests
python data-platform/quality/checks.py    # confirm the data underneath is sane first
```

Sanity-check the totals by hand: the sum of per-client placements should equal
`SELECT count(*) FROM fact_placements`. If it doesn't, your join is duplicating rows - the most
common bug in this kind of query.

## Gotchas

- Joining two facts to one dimension in a single query multiplies rows. Aggregate each fact
  separately (subqueries or CTEs) and join the results.
- "At risk" is a definition, not a truth. Whatever you pick, the UI has to be able to explain it
  to a user in one sentence.
