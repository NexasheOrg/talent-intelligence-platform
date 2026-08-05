---
id: API-01
title: "api: add a /api/clients listing endpoint"
module: api
labels: [api, good-first-issue]
difficulty: warm-up
estimate: half a day
depends_on: []
---

## Why this matters

We can list consultants but not clients, so nothing in the product can answer "who do we
actually work for?". This is also the smallest possible tour of how an endpoint is built here.

This is your day-one task. Small on purpose: the goal is one merged PR and a feel for the loop.

## What "done" looks like

- [ ] `GET /api/clients` returns a page of clients with their placement count
- [ ] It supports `?q=` (name), `?tier=`, `?page=`, `?page_size=`, like `/api/consultants`
- [ ] Response model added to `models.py`, so `/docs` describes it correctly
- [ ] Tests: pagination doesn't lose or repeat rows, the tier filter filters, search searches
- [ ] The SQL runs on both Postgres and SQLite

## Where to work

- `api/app/routers/clients.py` - new
- `api/app/main.py` - register the router
- `api/app/models.py` - `ClientSummary`, `ClientPage`
- `api/tests/test_endpoints.py` - or a new `test_clients.py`

## How to approach it

1. Open `api/app/routers/consultants.py` and read it. Your endpoint is the same shape: build a
   WHERE clause plus its parameters, use it for both the count query and the page query.
2. Placement counts come from a `LEFT JOIN fact_placements ... GROUP BY`. Use a LEFT JOIN, not an
   inner one, or clients with no placements vanish - which is exactly the group we care about.
3. Add the model first, then the route, then the test.

## How to check it

```bash
python -m pytest api/tests
```

Then <http://localhost:8000/docs> → `/api/clients` → **Try it out**. Check a filter that matches
nothing returns `{"rows": [], "total": 0}` and not an error.

## Gotchas

- `LIMIT ? OFFSET ?` - write placeholders as `?`. `db.py` converts them for Postgres. Never
  build the SQL string with an f-string around user input.
- A client with zero placements should appear with `placements: 0`, not be missing.
