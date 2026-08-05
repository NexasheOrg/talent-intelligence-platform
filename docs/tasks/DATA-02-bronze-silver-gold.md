---
id: DATA-02
title: "data-platform: split the loader into real bronze -> silver -> gold transforms"
module: data-platform
labels: [data-platform]
difficulty: core
estimate: 2-3 days
depends_on: []
---

## Why this matters

`load_seed.py` currently jumps straight from CSV to the gold tables. That's fine as a proof it
works, but it means there's nowhere to put cleaning logic, no record of what arrived, and no way
to reprocess without regenerating. The medallion layout in
[ARCHITECTURE.md](../ARCHITECTURE.md) exists to fix all three. This task makes the architecture
real instead of aspirational.

## What "done" looks like

- [ ] **bronze**: raw rows land exactly as received, plus an ingestion timestamp and source name.
      Nothing is cleaned, nothing is dropped
- [ ] **silver**: typed, deduplicated, conformed - dates are dates, numbers are numbers, and
      values are normalised (e.g. status casing)
- [ ] **gold**: built from silver, matching `models/gold_schema.sql` exactly
- [ ] Each stage is runnable on its own and is idempotent - running it twice changes nothing
- [ ] A row count per stage is printed, so drops are visible rather than silent
- [ ] Tests for each stage
- [ ] The quality checks still pass at the end
- [ ] `data-platform/README.md` updated to describe the real pipeline

## Where to work

- `data-platform/ingestion/` - CSV → bronze
- `data-platform/transforms/` - bronze → silver → gold
- `data-platform/load_seed.py` - becomes a thin orchestrator that calls the three stages
- `data-platform/tests/`

## How to approach it

1. Do it in three PRs, not one. Bronze first, and get it merged. This task is big enough that a
   single PR would be unreviewable.
2. Keep bronze **dumb**. The temptation is to clean things on the way in; resist it. The value of
   bronze is that it's exactly what arrived, so when a number looks wrong you can prove where it
   came from.
3. Silver is where every judgement lives: dedup rules, casing, what to do with a null. Comment
   each one with *why*, not *what*.
4. **Print row counts between every stage.** 10,000 rows into silver and 9,300 out is a bug you
   want to see immediately, not in three weeks.
5. Idempotency: re-running must not double the data. Truncate-and-reload is a perfectly good
   answer at this size - just be deliberate about it.

## How to check it

```bash
python data-platform/load_seed.py
python data-platform/load_seed.py     # twice - counts must be identical
python data-platform/quality/checks.py
python -m pytest data-platform/tests api/tests
```

The API tests matter here: they read the gold layer, so if you've broken the contract they'll
tell you before four other people find out.

## Gotchas

- **Don't change the gold schema in this task.** Everything downstream depends on it. If you
  believe it needs changing, that's a separate PR with a note in `ARCHITECTURE.md`.
- Portable SQL only - Postgres and SQLite.
- Tell the team before merging. This one touches the foundation everybody stands on.
