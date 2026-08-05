# Roadmap

We ship a **thin vertical slice end-to-end first**, then widen. Scope discipline is how this
stays achievable for a small team.

The milestones are direction. The actual open work, task by task, is in [TASKS.md](TASKS.md) -
nothing there is pre-assigned.

## Milestone 0 - Foundations (done)
- [x] Repo scaffold, CI green, Docker Compose brings the stack up locally
- [x] Synthetic seed generator produces consultants, clients, jobs, timesheets, placements
- [x] Gold star schema drafted, documented, and loaded
- **Exit (met):** everyone can start the stack and see seed data in the dashboard

## Milestone 1 - Thin slice (mostly done)
- [x] **Runnable by anyone.** Double-click launchers on Windows, a setup checker, and a
      no-Docker fallback on Python + SQLite so a locked-down laptop isn't a blocker
- [x] **Serving layer.** FastAPI split into routers with typed response models: utilization,
      trend, funnel, and consultants with search / filter / pagination
- [x] **Web.** Multi-page dashboard - routing, shared API client, charts, filters, and a table
      view on every chart. Utilization & Bench, Placement Funnel and Consultants are live
- [x] **Data quality.** 11 checks over the gold layer, with tests proving each one can fail
- [x] **Risk score visible in the UI** - from a baseline heuristic, explicitly labelled as such
- [x] **CI.** Lint, tests, data quality, Postgres compatibility, and the web build
- [ ] A real model behind the risk score (`ML-01` … `ML-04`)
- [ ] Ingestion split into bronze → silver → gold (`DATA-02`)
- **Exit:** a dashboard live end-to-end with a trained risk score in the UI

## Milestone 2 - Widen the product
- [x] AI assistant answering over gold - read-only, allow-listed, returning its SQL
- [ ] Dashboards: Client Health, Timesheet/Billing (`WEB-03`, `WEB-04`, `API-03`, `API-04`)
- [ ] "Ask your data" in the web app, and an LLM behind the guardrails (`AI-02`, `AI-04`)
- [ ] RBAC on the API (`API-05`)
- [ ] Stage history so the funnel shows true conversion (`DATA-03`), and `dim_date` (`DATA-04`)
- [ ] Images published from CI; config and secrets out of compose (`OPS-03`, `OPS-04`)

## Milestone 3 - Production-shaped
- [ ] Terraform for the cloud target, then a deployed environment (`OPS-05`)
- [ ] Swap the Postgres MVP for the Azure lakehouse target (ADLS + Synapse/Snowflake)
- [ ] RAG over policy/SOW documents in the assistant (`AI-05`)
- [ ] Experiment tracking and model monitoring (`ML-05`)
- [ ] Connect a real source (an HRMS / ATS export) behind a connector (`DATA-05`)

## Two rules that have shaped this more than the milestones

**Nobody gets blocked on tooling.** Every query runs on Postgres *and* SQLite, so someone who
can't install Docker Desktop can still do every task here. CI checks both, so the promise stays
true rather than quietly rotting.

**Placeholders say they're placeholders.** The risk score reports `baseline-heuristic-v0`. The
funnel page says it shows a distribution, not conversion. Unbuilt dashboards render a brief
explaining what they need. Anything that isn't yet what it will eventually be says so *in the
product* - which is why the remaining work is discoverable instead of a nasty surprise.

Milestones are guides, not contracts - scope gets re-cut each milestone based on what's actually
shipping.
