# Architecture

TIP is a **monorepo** with one polyglot pipeline: raw source data → medallion lakehouse →
gold star-schema → API → dashboards, with an ML service and an AI assistant reading the gold
layer. This doc is the contract every layer builds against.

## 1. Data flow (medallion)

| Zone | Meaning | Format | Owner |
|---|---|---|---|
| **bronze** | raw, as-ingested, append-only | Parquet / raw JSON | Praveen + Sujith |
| **silver** | cleaned, typed, deduped, conformed | Parquet / Delta | Praveen |
| **gold** | business-ready star schema, serves API/ML/AI | Postgres / Synapse tables | Praveen |

Transforms are code-reviewed and tested. Nothing skips a zone.

## 2. Gold star schema (the shared contract)

Facts and dimensions everyone downstream can rely on. Keep names stable; changes go through a
PR + a note in this doc.

**Dimensions**
- `dim_consultant` — consultant_id, name, skills, seniority, location, cost_rate, hire_date, status
- `dim_client` — client_id, name, industry, tier, start_date
- `dim_date` — standard calendar dimension
- `dim_job` — job_id, client_id, title, skills_required, open_date, status

**Facts**
- `fact_placements` — placement_id, consultant_id, client_id, job_id, start/end, bill_rate, margin
- `fact_timesheets` — consultant_id, date, hours_billable, hours_bench, project_id
- `fact_pipeline` — job_id, consultant_id, stage (submitted/interview/offer/placed/rejected), stage_date
- `fact_bench` — consultant_id, bench_start, bench_end, days_on_bench

## 3. Serving layer

- **API** (`api/`) reads **only** the gold layer. It owns auth + **RBAC** (recruiter / delivery
  manager / exec see different slices). It never queries bronze/silver directly.
- **ML service** (`ml/`) trains on gold + serves a scoring endpoint (`/score/attrition`).
- **AI assistant** (`ai-assistant/`) does **NL→SQL** against gold (read-only, allow-listed
  tables) and **RAG** over uploaded policy/SOW docs. It never gets write access.

## 4. Product surface (web)

React SPA. Talks to the API for dashboard data, to the ML service for risk scores, and to the
AI assistant for the "ask your data" box. Four dashboards for the MVP: Utilization & Bench,
Placement Funnel, Timesheet/Billing, Client Health.

## 5. Environments

- **local** — Docker Compose brings up Postgres + API + web + services; seed data from
  `data/seed/`. This is where everyone develops. No cloud account needed to contribute.
- **cloud (target)** — Azure: ADLS Gen2 (lake), Synapse/Snowflake (warehouse), AKS (services),
  provisioned via Terraform in `infra/`.

## 6. Non-negotiables

1. **No real/customer data in git.** Only the synthetic generator. PII stays out.
2. **Gold schema is a contract.** Breaking changes = PR + review + update this doc.
3. **Every layer runs locally** from seed data, so no one is blocked on cloud access.
4. **RBAC on every API/AI path.** The AI assistant is read-only and table-allow-listed.
