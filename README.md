# Talent & Delivery Intelligence Platform (TIP)

> The analytics brain for a staffing / IT-services firm — one place for the numbers that
> actually run the business: consultant utilization & bench time, the
> submission → interview → placement funnel, timesheet & billing health, attrition
> risk, and client health.

TIP ingests data from operational systems (HRMS, ATS, timesheets, CRM), models it in a
lakehouse, and serves it back as **dashboards**, a **predictive ML model**, and an
**"ask your data" AI assistant**. It is built to plug into an existing HRMS (e.g. SproxHRMS)
so a company like Nexashe or Dhanutek can run it internally.

---

## Why this exists

Staffing / IT-services firms make money on people and placements, but the numbers that
decide profit — who's on the bench, how long, which clients are healthy, who's at risk of
leaving — usually live scattered across spreadsheets and separate apps. TIP unifies them and
puts an analytics + AI layer on top.

## What it does (product surface)

- **Dashboards** — utilization & bench, placement funnel, timesheet/billing, client health.
- **Predictive model** — attrition-risk / bench-duration scoring per consultant.
- **Ask your data** — natural-language questions answered over the warehouse (NL→SQL) and
  policy/SOW documents (RAG).

## Architecture at a glance

```
 Sources                Data Platform (medallion)           Serving              Product
┌──────────┐   ingest  ┌───────┐  ┌───────┐  ┌───────┐   ┌───────────┐      ┌────────────┐
│ HRMS/ATS │──────────▶│bronze │─▶│silver │─▶│ gold  │──▶│  API      │─────▶│  Web app   │
│ Timesheet│           │(raw)  │  │(clean)│  │(star  │   │ (RBAC)    │      │ dashboards │
│ CRM/CSV  │           └───────┘  └───────┘  │schema)│   └───────────┘      └────────────┘
└──────────┘                                 └───┬───┘         │                  ▲
                                                 │             ▼                  │
                                                 │        ┌─────────┐        ┌─────────┐
                                                 └───────▶│ ML svc  │        │ AI      │
                                                          │ (risk)  │        │ assistant│
                                                          └─────────┘        │(NL→SQL/  │
                                                                             │  RAG)    │
                                                                             └─────────┘
```

Full detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Tech stack

| Layer | MVP | Production target |
|---|---|---|
| Ingestion / transforms | Python, PySpark, dbt | Azure Data Factory + Databricks |
| Lake / warehouse | DuckDB / Postgres | ADLS Gen2 + Synapse / Snowflake |
| Infra | Docker Compose, Terraform | Azure (ADLS, ACR, AKS) |
| API | Spring Boot (or Node) + RBAC | same, containerized |
| Web | React + TypeScript + Vite + Recharts/D3 | same |
| ML | Python, scikit-learn | same, MLflow tracking |
| AI assistant | Python + FastAPI, vector DB | same |
| CI/CD | GitHub Actions | GitHub Actions |

## Repository layout

| Folder | Owner | What lives here |
|---|---|---|
| [`data-platform/`](data-platform) | Praveen | ingestion, medallion transforms, star-schema models, data-quality checks |
| [`infra/`](infra) | Sujith | Terraform IaC, source connectors, scheduling, storage |
| [`api/`](api) | Amulya | backend API over the gold layer, auth + RBAC, CI/CD |
| [`web/`](web) | Laya + Eshwar | React dashboard app |
| [`ml/`](ml) | Eshwar | attrition-risk / bench-duration model + notebooks |
| [`ai-assistant/`](ai-assistant) | Eshwar + Laya | NL→SQL + RAG "ask your data" service |
| [`data/seed/`](data/seed) | shared | synthetic seed-data generator (no real data in git) |
| [`docs/`](docs) | Laya | architecture, roles, roadmap |

## Getting started

```bash
git clone https://github.com/NexasheOrg/talent-intelligence-platform.git
cd talent-intelligence-platform
python data/seed/generate_seed.py     # create synthetic data to build against
```

Then read the doc for **your** layer's README, and pick up your starter issue.
New to the team? Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.

## Team & ownership

See [`docs/ROLES.md`](docs/ROLES.md). Lead / architect: **Laya**.

## Roadmap

Phased milestones in [`docs/ROADMAP.md`](docs/ROADMAP.md). We ship a thin slice end-to-end
first (one source → one dashboard → one model → one AI query), then widen.
