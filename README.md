# Talent & Delivery Intelligence Platform (TIP)

> The analytics brain for a staffing / IT-services firm - one place for the numbers that
> actually run the business: consultant utilization & bench time, the
> submission → interview → placement funnel, timesheet & billing health, attrition
> risk, and client health.

TIP ingests data from operational systems (HRMS, ATS, timesheets, CRM), models it in a
lakehouse, and serves it back as **dashboards**, a **predictive ML model**, and an
**"ask your data" AI assistant**. It plugs into the systems a staffing or recruitment
company already runs (HRMS, ATS, timesheets, CRM) so they can run it internally.

> **Status: early-stage, but runnable end to end.** One command (or one double-click on
> Windows) brings up a seeded warehouse, the API, an NL→SQL assistant, and a multi-page React
> dashboard with live numbers. Three dashboards are built; the rest are scoped starter tasks in
> [`docs/TASKS.md`](docs/TASKS.md). See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the plan.

---

## Why this exists

Staffing / IT-services firms make money on people and placements, but the numbers that
decide profit - who's on the bench, how long, which clients are healthy, who's at risk of
leaving - usually live scattered across spreadsheets and separate apps. TIP unifies them and
puts an analytics + AI layer on top.

## What it does (product surface)

- **Dashboards** - utilization & bench, placement funnel, timesheet/billing, client health.
- **Predictive model** - attrition-risk / bench-duration scoring per consultant.
- **Ask your data** - natural-language questions answered over the warehouse (NL→SQL) and
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
| Lake / warehouse | Postgres (SQLite fallback) | ADLS Gen2 + Synapse / Snowflake |
| Infra | Docker Compose, Terraform | Azure (ADLS, ACR, AKS) |
| API | Python + FastAPI + RBAC | same, containerized |
| Web | React + TypeScript + Vite + Recharts/D3 | same |
| ML | Python, scikit-learn | same, MLflow tracking |
| AI assistant | Python + FastAPI, vector DB | same |
| CI/CD | GitHub Actions | GitHub Actions |

**Why this stack:** the entire backend (API, ML, AI) is **one language, Python** so it deploys
as one set of containers with one skillset. The frontend is **React + TypeScript** because the
team already knows it and it's the industry default. React also keeps a clean path to a
**mobile app later** via React Native / Expo (same language, shared logic) - the web app is
built responsive so it already works on a phone browser in the meantime.

## Repository layout

| Folder | What lives here |
|---|---|
| [`data-platform/`](data-platform) | ingestion, medallion transforms, star-schema models, data-quality checks |
| [`infra/`](infra) | Terraform IaC, source connectors, scheduling, storage |
| [`api/`](api) | backend API over the gold layer, auth + RBAC, CI/CD |
| [`web/`](web) | React dashboard app |
| [`ml/`](ml) | attrition-risk / bench-duration model + notebooks |
| [`ai-assistant/`](ai-assistant) | NL→SQL + RAG "ask your data" service |
| [`data/seed/`](data/seed) | synthetic seed-data generator (no real data in git) |
| [`scripts/`](scripts) | the start / stop / check-setup scripts the launchers call |
| [`docs/`](docs) | setup, onboarding, architecture, roadmap, and the task pack |

## Getting started

**On Windows, or new to this kind of project?** Clone the repo with
[GitHub Desktop](https://desktop.github.com), then **double-click `START-HERE.bat`**. It checks
what you have installed, starts everything, waits until it's actually ready, and opens your
browser. Click-by-click guide: [`docs/WINDOWS-SETUP.md`](docs/WINDOWS-SETUP.md).

**On macOS or Linux:** double-click `start.command`, or:

```bash
git clone https://github.com/NexasheOrg/talent-intelligence-platform.git
cd talent-intelligence-platform
./scripts/start.sh          # or: docker compose up --build
```

Then open:
- **Dashboard** — http://localhost:8080
- **API docs** — http://localhost:8000/docs (interactive, try any endpoint)
- **Assistant** — http://localhost:8100/docs

What happens: Postgres starts, the `loader` generates synthetic seed data and loads the gold
schema, the API and assistant serve it, and the React app displays it. Stop with `STOP.bat` or
`docker compose down`.

**Can't install Docker?** (Locked-down laptop, no admin rights, virtualization off in BIOS.)
Nobody has to be blocked on that — the same app runs on Python + SQLite with no containers:
[`docs/RUN-WITHOUT-DOCKER.md`](docs/RUN-WITHOUT-DOCKER.md). Every query in the repo is written
to run on both databases, and CI checks it.

Working on just one layer? Generate the seed data alone with
`python data/seed/generate_seed.py`, and see your layer's README for a hot-reload setup.

**New to the team?** [`docs/ONBOARDING.md`](docs/ONBOARDING.md) → your starter task in
[`docs/TASKS.md`](docs/TASKS.md) → [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Roadmap

Phased milestones in [`docs/ROADMAP.md`](docs/ROADMAP.md). We ship a thin slice end-to-end
first (one source → one dashboard → one model → one AI query), then widen.
