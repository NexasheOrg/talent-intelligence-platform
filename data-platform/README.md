# data-platform  ·  Owner: Praveen

The backbone. Ingest source data, move it through the medallion zones, and publish the gold
star schema everyone downstream depends on.

- `ingestion/` — land raw source data into **bronze** (append-only, as-received)
- `transforms/` — bronze → **silver** (clean/type/dedup/conform) → **gold** (star schema)
- `models/` — dbt-style model definitions for the gold facts & dimensions
- `quality/` — data-quality checks & tests (row counts, nulls, referential integrity)

**Stack:** Python, PySpark, dbt · MVP target Postgres/DuckDB · cloud target Databricks/Synapse.
**Contract:** the gold schema in [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — change
only by PR. Everything here must run locally against `data/seed/`.
