# Architecture

TIP is a **monorepo** with one polyglot pipeline: raw source data → medallion lakehouse →
gold star-schema → API → dashboards, with an ML service and an AI assistant reading the gold
layer. This doc is the contract every layer builds against.

## 1. Data flow (medallion)

| Zone | Meaning | Format |
|---|---|---|
| **bronze** | raw, as-ingested, append-only | Parquet / raw JSON |
| **silver** | cleaned, typed, deduped, conformed | Parquet / Delta |
| **gold** | business-ready star schema, serves API/ML/AI | Postgres / Synapse tables |

Transforms are code-reviewed and tested. Nothing skips a zone.

## 2. Gold star schema (the shared contract)

Facts and dimensions everyone downstream can rely on. Keep names stable; changes go through a
PR + a note in this doc.

**Dimensions**
- `dim_consultant` - consultant_id, name, skills, seniority, location, cost_rate, hire_date, status
- `dim_client` - client_id, name, industry, tier, start_date
- `dim_date` - standard calendar dimension
- `dim_job` - job_id, client_id, title, skills_required, open_date, status

**Facts**
- `fact_placements` - placement_id, consultant_id, client_id, job_id, start/end, bill_rate, margin
- `fact_timesheets` - consultant_id, date, hours_billable, hours_bench, project_id
- `fact_pipeline` - job_id, consultant_id, stage (submitted/interview/offer/placed/rejected), stage_date
- `fact_bench` - consultant_id, bench_start, bench_end, days_on_bench

## 3. Serving layer

| Service | Port | State |
|---|---|---|
| **API** (`api/`) | 8000 | built |
| **AI assistant** (`ai-assistant/`) | 8100 | built (pattern-matched NL→SQL; LLM is `AI-02`) |
| **ML service** (`ml/`) | 8200 | not built yet - `ML-03` |
| **Web** (`web/`) | 8080 | built |

- **API** reads **only** the gold layer, never bronze/silver. It will own auth + **RBAC**
  (recruiter / delivery manager / exec see different slices) - not yet built, `API-05`.
  It currently serves the attrition risk score from a baseline heuristic in `app/risk.py`,
  labelled `baseline-heuristic-v0` in every response so it can't be mistaken for a model.
- **ML service** will train on gold and serve `/score/attrition`. Until it exists, the API's
  heuristic stands in and the endpoint contract (`models.RiskScore`) is already fixed, so the
  swap doesn't ripple outward.
- **AI assistant** does **NL→SQL** against gold and will do **RAG** over policy/SOW documents.
  It never gets write access. Its guardrails - read-only, one statement, allow-listed tables,
  enforced LIMIT - live in `assistant/guardrails.py` and apply to *any* translator, including a
  future LLM. A model is a source of suggestions, never a source of permissions.

## 4. Product surface (web)

React SPA (TypeScript, Vite, Recharts). Talks to the API for dashboard data, to the ML service
for risk scores, and to the AI assistant for "ask your data". nginx routes `/api/assistant/` to
the assistant and everything else under `/api/` to the API; the Vite dev server mirrors that, so
the app only ever uses relative paths.

Dashboards: **Utilization & Bench**, **Placement Funnel** and **Consultants** are built.
**Client Health**, **Timesheet/Billing** and **Ask your data** render a brief in the running app
describing what they need - see [TASKS.md](TASKS.md).

## 5. Environments

- **local (Docker)** - Compose brings up Postgres + loader + API + assistant + web; seed data
  from `data/seed/`. No cloud account needed to contribute.
- **local (no Docker)** - the same stack on **SQLite**, needing only Python and Node, for
  machines where Docker Desktop can't be installed. See [RUN-WITHOUT-DOCKER.md](RUN-WITHOUT-DOCKER.md).
- **cloud (target)** - Azure: ADLS Gen2 (lake), Synapse/Snowflake (warehouse), AKS (services),
  provisioned via Terraform in `infra/`. Not built - `OPS-05`.

### The portability rule

Because those first two environments must stay equivalent, **all SQL in this repo runs on both
Postgres and SQLite**: `?` placeholders, no engine-specific functions, one `DROP` per statement.
CI enforces it by loading the gold layer and running the quality checks against a real Postgres
as well as SQLite. Needing something Postgres-only is a legitimate thing to want - raise it in
the PR rather than breaking the fallback silently.

## 6. Non-negotiables

1. **No real/customer data in git.** Only the synthetic generator. PII stays out.
2. **Gold schema is a contract.** Breaking changes = PR + review + update this doc.
3. **Every layer runs locally** from seed data, so no one is blocked on cloud access.
4. **RBAC on every API/AI path.** The AI assistant is read-only and table-allow-listed.
