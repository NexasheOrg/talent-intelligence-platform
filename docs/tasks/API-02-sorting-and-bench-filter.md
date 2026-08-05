---
id: API-02
title: "api: add sorting and a days-on-bench filter to /api/consultants"
module: api
labels: [api]
difficulty: core
estimate: 1 day
depends_on: []
---

## Why this matters

WEB-01 sorts the twenty rows currently on screen. "Who has been on the bench longest" needs the
whole 300 sorted, which only the database can do. Same for "show me everyone benched over 90
days" - that's a filter, not something to page through looking for.

## What "done" looks like

- [ ] `?sort=` accepts `name`, `seniority`, `days_on_bench`, `status`
- [ ] `?order=asc|desc`, defaulting to `asc`
- [ ] `?min_days_on_bench=` filters to consultants benched at least that long
- [ ] An unknown `sort` value returns **422**, not a 500 and not silently-ignored
- [ ] Nulls sort predictably and are documented (people not on the bench have no bench days)
- [ ] Tests: each sort key works, order reverses, a bad key is rejected, the filter filters
- [ ] Works on Postgres and SQLite

## Where to work

- `api/app/routers/consultants.py`
- `api/tests/test_endpoints.py`

## How to approach it

1. **A sort column cannot be a parameter** - `ORDER BY ?` isn't valid SQL. So it has to go into
   the query as text, which means it must come from a hardcoded allow-list you control:

   ```python
   SORTABLE = {"name": "c.name", "seniority": "c.seniority",
               "days_on_bench": "b.days_on_bench", "status": "c.status"}
   ```

   Look up the user's value in that dict and use the mapped column. Never pass their string
   through. This is the one place in the codebase where user input reaches the SQL text, and the
   allow-list is what makes it safe.
2. `order` is the same problem: map `asc`/`desc` to literals, don't interpolate.
3. Use FastAPI's validation to return 422 - `Literal["asc", "desc"]` on the parameter does it
   for free.
4. Nulls: Postgres puts them last on ASC, SQLite puts them first. If you want them consistent,
   sort by an expression like `CASE WHEN b.days_on_bench IS NULL THEN 1 ELSE 0 END` first, and
   test on both databases.

## How to check it

```bash
python -m pytest api/tests
```

Try `/api/consultants?sort=days_on_bench&order=desc` in `/docs`. The longest-benched consultant
should be first - cross-check against `/api/consultants?min_days_on_bench=150`.

## Gotchas

- Tell whoever owns WEB-01 when this lands, so the UI can switch to server-side sorting.
- Adding a sortable column means adding it to the allow-list. If that feels annoying, that's the
  security working.
