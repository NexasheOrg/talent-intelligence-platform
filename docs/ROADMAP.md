# Roadmap

We ship a **thin vertical slice end-to-end first**, then widen. Scope discipline is how this
stays achievable for a 5-person team with two juniors.

## Milestone 0 - Foundations
- [x] Repo scaffold, CI green, Docker Compose brings the stack up locally
- [x] Synthetic seed generator produces consultants, clients, jobs, timesheets, placements
- [x] Gold star-schema drafted, documented, and loaded into Postgres (pending team sign-off)
- **Exit (met):** everyone can `docker compose up` and see seed data in the dashboard

## Milestone 1 - Thin slice
- [ ] Ingestion: one source (CSV/seed) → bronze → silver → gold (Praveen + Sujith)
- [ ] API: RBAC + one endpoint serving `fact_bench` / utilization (Amulya)
- [ ] Web: one dashboard - **Utilization & Bench** (Laya)
- [ ] ML: first attrition-risk model trained on seed, `/score` endpoint (Eshwar)
- **Exit:** one dashboard live end-to-end + a risk score visible in the UI

## Milestone 2 - Widen the product
- [ ] Dashboards: Placement Funnel, Timesheet/Billing, Client Health
- [ ] AI assistant: NL→SQL over gold (allow-listed, read-only) - "ask your data" box
- [ ] Data-quality checks + tests across silver/gold
- [ ] Infra: Terraform for the cloud target; CI deploys a container

## Milestone 3 - Production-shaped
- [ ] Swap DuckDB/Postgres MVP for the Azure lakehouse target (ADLS + Synapse/Snowflake)
- [ ] RAG over policy/SOW documents in the assistant
- [ ] MLflow experiment tracking + model monitoring
- [ ] Connect a real source (an HRMS / ATS export) behind a connector

Milestones are guides, not contracts - the lead re-cuts scope every milestone based on what's
actually shipping.
