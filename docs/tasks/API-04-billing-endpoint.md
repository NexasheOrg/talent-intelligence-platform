---
id: API-04
title: "api: add /api/billing/summary"
module: api
labels: [api]
difficulty: core
estimate: 1-2 days
depends_on: []
---

## Why this matters

Hours worked but never logged are hours never invoiced. This endpoint is what makes that
leakage visible - it powers the Timesheet & Billing dashboard (WEB-04).

## What "done" looks like

- [ ] `GET /api/billing/summary` returns, for the most recent week: consultants expected to
      submit, how many did, how many didn't, billable and bench hours
- [ ] `GET /api/billing/missing-timesheets` lists who is missing one, with their name and client
- [ ] "Expected to submit" is defined in the code with a comment - it is not obvious
- [ ] `?weeks=` lets the caller look at more than one week
- [ ] Response models in `models.py`
- [ ] Tests, including the case where nobody is missing
- [ ] Runs on Postgres and SQLite

## Where to work

- `api/app/routers/billing.py` - new
- `api/app/main.py`, `api/app/models.py`, `api/tests/`

## How to approach it

1. Agree the response shape with whoever owns WEB-04 first.
2. Work out **who should have submitted** before you work out who did. In the seed, timesheets
   exist only for consultants with `status = 'placed'`, so that's your denominator. Write that
   down - a "missing timesheets" number with an undefined denominator is worse than no number,
   because people will act on it.
3. "The most recent week" is `MAX(week_ending)` in `fact_timesheets`, not today's date. Using
   today would make the endpoint break every weekend.
4. Missing = a placed consultant with no row for that week. `LEFT JOIN ... WHERE t.id IS NULL`,
   or a `NOT IN` subquery.

## How to check it

```bash
python -m pytest api/tests
```

Cross-check in `/docs`: `submitted + missing` must equal `expected`. If it doesn't, the
denominator is wrong.

## Gotchas

- The seed currently gives every placed consultant a timesheet every week, so **missing will be
  zero**. That's not a bug in your code. Test the logic by deleting a few rows from a local copy
  of the database, and mention it in your PR - making the seed generate realistic gaps is a good
  follow-up issue to file.
- Don't return an empty list and call it success. "Nobody is missing" and "the query is broken"
  look identical from the outside unless the summary numbers are there too.
