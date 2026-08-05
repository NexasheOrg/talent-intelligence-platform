---
id: DATA-01
title: "data-platform: add four more data-quality checks"
module: data-platform
labels: [data-platform, good-first-issue]
difficulty: warm-up
estimate: half a day
depends_on: []
---

## Why this matters

Eleven checks guard the gold layer today. Every one of them is a data bug that can't reach a
dashboard any more. A wrong number on a dashboard is worse than a broken page, because people
believe it and act on it.

This is your day-one task, and it's the fastest way to learn the shape of the data.

## What "done" looks like

- [ ] Four new checks in `quality/checks.py`
- [ ] Each has a test in `tests/test_checks.py` that **breaks the data and proves the check
      catches it**
- [ ] Every check's failure message says what's wrong and how many rows are affected
- [ ] `python data-platform/quality/checks.py` still passes on freshly loaded seed data

## Where to work

- `data-platform/quality/checks.py`
- `data-platform/tests/test_checks.py`

## Ideas (pick four, or bring your own)

- A placement's `end_date`, when set, is never before its `start_date`
- Nobody has a `hire_date` in the future
- Every consultant marked `bench` has a row in `fact_bench`, and vice versa
- `days_on_bench` matches the gap between `bench_start` and today
- No duplicate consultant names (or: duplicates are expected - find out which, and encode it)
- Every job's `skills_required` uses skills that appear in at least one consultant's `skills`
- Bill rate is always above cost rate on the same placement

## How to approach it

1. Read the existing checks. Each is a small function with `@check("plain english description")`
   that raises `Failed` with a useful message. Copy that shape.
2. **Write the test first.** Corrupt one row in a temporary database, assert `run_checks() == 1`.
   If the test passes before you write the check, the test is wrong.
3. Explore the data with the check runner or plain SQL before deciding what "correct" means -
   some of the ideas above may already be violated by the seed generator, and finding that out
   *is* the useful result.

## How to check it

```bash
python data-platform/load_seed.py
python data-platform/quality/checks.py
python -m pytest data-platform/tests
```

## Gotchas

- If a check fails on the seed data as it stands, don't weaken the check to make it green. Either
  the seed generator is wrong (fix it, or file an issue) or your assumption was wrong (say so).
  A check tuned until it passes is a check that tests nothing.
- Portable SQL only - these run on Postgres and SQLite.
