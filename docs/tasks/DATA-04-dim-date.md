---
id: DATA-04
title: "data-platform: add the dim_date calendar dimension"
module: data-platform
labels: [data-platform]
difficulty: core
estimate: 1 day
depends_on: []
---

## Why this matters

Every time-based question - "utilization by quarter", "placements per month", "how did last
fiscal year compare" - currently needs date arithmetic written by hand in each query, in SQL
that has to work on two different databases. A calendar dimension is the standard fix: compute
it once, join to it everywhere.

[ARCHITECTURE.md](../ARCHITECTURE.md) already lists `dim_date` as part of the gold layer. It just
doesn't exist yet.

## What "done" looks like

- [ ] `dim_date` covers every date the facts reference, with margin either side
- [ ] Columns at minimum: `date_key`, `date`, `year`, `quarter`, `month`, `month_name`,
      `week_of_year`, `day_of_week`, `is_weekend`
- [ ] Generated in code, not typed out, and idempotent
- [ ] Added to `gold_schema.sql` and to `docs/ARCHITECTURE.md`
- [ ] Quality checks: no gaps in the range, no duplicate dates, the range covers the facts
- [ ] At least one existing query rewritten to use it, proving it works

## Where to work

- `data-platform/models/gold_schema.sql`
- `data-platform/transforms/` or a `build_dim_date.py`
- `data-platform/load_seed.py` - call it during the load
- `data-platform/quality/checks.py`, `docs/ARCHITECTURE.md`

## How to approach it

1. Decide the key format and stick to it. `YYYYMMDD` as an integer is conventional and sorts
   correctly; a plain date column works too. Whichever you pick, the facts have to join to it
   cleanly.
2. Generate the range from the data (`MIN`/`MAX` across the date columns in the facts) rather
   than hardcoding years, then pad a year either side.
3. Python's `datetime` gives you everything you need. Don't try to generate this in SQL - it
   would need different syntax per database, which is exactly the problem you're solving.
4. Fiscal year is a business definition. If you add one, ask what the company's fiscal year
   actually is rather than assuming January.

## How to check it

```bash
python data-platform/load_seed.py
python data-platform/quality/checks.py
```

Sanity checks: the row count equals the number of days in the range; every distinct
`week_ending` in `fact_timesheets` finds a match in `dim_date`.

## Gotchas

- Don't store dates as text in one place and as dates in another - the join will silently match
  nothing and every result will be empty. Test the join, not just the table.
- Weeks are a trap: ISO weeks and "week starting Sunday" disagree at year boundaries. Pick one,
  name the column so it's obvious which, and document it.
