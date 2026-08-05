# data-platform

The backbone. Ingest source data, move it through the medallion zones, and publish the gold star
schema everyone downstream depends on. If this layer is wrong, every dashboard is confidently
wrong - which is worse than being down.

**Stack:** Python, PySpark, dbt · MVP target Postgres/SQLite · cloud target Databricks/Synapse.

## What's here

```
models/gold_schema.sql   the gold tables. THE contract - change only by PR
load_seed.py             generates seed data and loads it into the gold schema
db.py                    database access for this layer
quality/checks.py        11 data-quality checks; exits non-zero on failure
tests/                   proves the checks pass on good data AND fail on bad data
ingestion/               bronze landing zone (empty - task DATA-02)
transforms/              bronze -> silver -> gold (empty - task DATA-02)
```

**Contract:** the gold schema in [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md). Four other
people build directly on those table and column names. Changing one silently breaks their
branches, so schema changes go through a PR that updates the doc in the same commit.

## Running it

```bash
python data-platform/load_seed.py          # build the gold layer
python data-platform/quality/checks.py     # verify it
python -m pytest data-platform/tests
```

Without `DATABASE_URL` set it builds a local SQLite file at `data/local/tip.db`. Point it at
Postgres with `DATABASE_URL=postgresql://tip:tip@localhost:5433/tip`.

Run the quality checks **every time you change a transform**. They're the difference between
finding a data bug here and finding it in a dashboard three days later.

## Rules specific to this folder

- **Portable SQL only.** `gold_schema.sql` and every query must run on Postgres *and* SQLite -
  one DROP per statement, no CASCADE, no Postgres-only types. The header of that file lists the
  constraints.
- **Never commit data.** Only the generator. `data/seed/out/` and `data/local/` are git-ignored
  for a reason.
- **A new check needs a test that makes it fail.** A check suite that can't fail is worse than
  none, because it looks like coverage. See `tests/test_checks.py`.

## Next

Real bronze → silver → gold transforms, a `dim_date` calendar dimension, and stage history in
the pipeline fact so the funnel can show true conversion instead of a snapshot. Tasks
`DATA-01` … `DATA-05` in [`../docs/TASKS.md`](../docs/TASKS.md).
