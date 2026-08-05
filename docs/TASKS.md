# Available tasks

Thirty tasks across five tracks. **Nothing here is assigned to anyone** - this is the open
backlog. Pick something that matches what you want to get good at, claim it on the issue, and
say so in the team chat so two people don't start the same thing.

Full brief for each one is in [`docs/tasks/`](tasks): why it matters, what "done" looks like,
which files to touch, how to check your work, and the gotchas.

## How to pick

Every track has a `-01` that is a genuine warm-up: small, depends on nothing, and finishable in
a day. **If you're new, start there** - not because the rest is beyond you, but because getting
one PR merged teaches you the whole loop before you're also fighting an unfamiliar problem.

| Marker | Means |
|---|---|
| **warm-up** | day one. Depends on nothing |
| **core** | the real work. Some depend on another track - marked below |
| **stretch** | take it if you're ahead, or if it's the thing you actually want to learn |

Where a task depends on another, that's a **conversation, not a queue**. Go and agree the shape
of the thing between you first - fifteen minutes of that saves a day of rework, and it's the
part of the job that isn't typing.

---

## Frontend - the dashboards people look at

React, TypeScript, Vite, Recharts. Files in [`web/`](../web).

| ID | Task | Level | Needs |
|---|---|---|---|
| [WEB-01](tasks/WEB-01-sortable-consultants-table.md) | Make the consultants table sortable | warm-up | - |
| [WEB-02](tasks/WEB-02-filters-in-the-url.md) | Keep filters in the URL so views are shareable | core | - |
| [WEB-03](tasks/WEB-03-client-health-page.md) | Build the Client Health dashboard | core | API-03 |
| [WEB-04](tasks/WEB-04-billing-page.md) | Build the Timesheet & Billing dashboard | core | API-04 |
| [WEB-05](tasks/WEB-05-light-theme.md) | Add a light theme, and re-validate the chart colours | stretch | - |

## Backend - the serving layer

Python, FastAPI, SQL. Files in [`api/`](../api).

| ID | Task | Level | Needs |
|---|---|---|---|
| [API-01](tasks/API-01-clients-endpoint.md) | Add a `/api/clients` listing endpoint | warm-up | - |
| [API-02](tasks/API-02-sorting-and-bench-filter.md) | Add sorting and a days-on-bench filter | core | - |
| [API-03](tasks/API-03-client-health-endpoint.md) | Add `/api/clients/health` | core | - |
| [API-04](tasks/API-04-billing-endpoint.md) | Add `/api/billing/summary` | core | - |
| [API-05](tasks/API-05-rbac.md) | Add role-based access control | stretch | API-03 |

## Data - the numbers everyone else trusts

Python, SQL, medallion architecture. Files in [`data-platform/`](../data-platform) and
[`data/seed/`](../data/seed).

| ID | Task | Level | Needs |
|---|---|---|---|
| [DATA-01](tasks/DATA-01-more-quality-checks.md) | Add four more data-quality checks | warm-up | - |
| [DATA-02](tasks/DATA-02-bronze-silver-gold.md) | Split the loader into real bronze → silver → gold | core | - |
| [DATA-03](tasks/DATA-03-pipeline-stage-history.md) | Add stage history so the funnel shows real conversion | core | - |
| [DATA-04](tasks/DATA-04-dim-date.md) | Add the `dim_date` calendar dimension | core | - |
| [DATA-05](tasks/DATA-05-csv-connector.md) | Ingest a messy external CSV into bronze | stretch | DATA-02 |

## AI & ML - risk scores and "ask your data"

Python, scikit-learn, LLM APIs. Files in [`ml/`](../ml) and [`ai-assistant/`](../ai-assistant).

| ID | Task | Level | Needs |
|---|---|---|---|
| [AI-01](tasks/AI-01-more-questions.md) | Teach the assistant four more questions | warm-up | - |
| [AI-02](tasks/AI-02-llm-translator.md) | Swap the matcher for an LLM, behind the same guardrails | core | - |
| [AI-03](tasks/AI-03-question-log.md) | Log what people actually ask | core | - |
| [AI-04](tasks/AI-04-ask-your-data-page.md) | Build the "Ask your data" page | core | AI-01 |
| [AI-05](tasks/AI-05-rag-over-documents.md) | Answer policy questions from documents | stretch | AI-02 |
| [ML-01](tasks/ML-01-attrition-label.md) | Give the seed data a realistic attrition signal | warm-up | - |
| [ML-02](tasks/ML-02-train-attrition-model.md) | Train an attrition model that beats the baseline | core | ML-01 |
| [ML-03](tasks/ML-03-serve-the-model.md) | Save the model and serve it over HTTP | core | ML-02 |
| [ML-04](tasks/ML-04-wire-model-into-api.md) | Replace the heuristic in the API with the model | core | ML-03 |
| [ML-05](tasks/ML-05-experiment-log.md) | Log experiments so runs can be compared | stretch | ML-02 |

> **One rule for this track, and it isn't negotiable: no LLM anywhere in the data layer.**
> Bronze → silver → gold has to be deterministic - same input, same output, every time. A model
> that invents a value inside a transform doesn't crash anything; it writes a wrong number into
> gold, and every dashboard then reports it confidently with no way to tell. The LLM belongs in
> `ai-assistant/`: on top of gold, read-only, allow-listed, and returning the SQL it used so a
> human can check the answer.

## DevOps - making it run, repeatably

Docker, GitHub Actions, Terraform. Files in [`infra/`](../infra), [`scripts/`](../scripts) and
[`.github/workflows/`](../.github/workflows).

| ID | Task | Level | Needs |
|---|---|---|---|
| [OPS-01](tasks/OPS-01-pre-commit-hooks.md) | Catch lint failures before they reach CI | warm-up | - |
| [OPS-02](tasks/OPS-02-stack-smoke-test.md) | Smoke-test the whole stack in CI | core | - |
| [OPS-03](tasks/OPS-03-config-and-secrets.md) | Get credentials out of `docker-compose.yml` | core | - |
| [OPS-04](tasks/OPS-04-publish-images.md) | Build and publish container images from CI | core | OPS-02 |
| [OPS-05](tasks/OPS-05-terraform-skeleton.md) | Terraform skeleton for the cloud target | stretch | OPS-04 |

---

## Filing these as GitHub issues

Each brief has front matter with its title and labels.

```bash
./scripts/create-issues.sh            # preview what it would create
./scripts/create-issues.sh --create   # actually create them
```

```powershell
.\scripts\create-issues.ps1
.\scripts\create-issues.ps1 -Create
```

Needs the [GitHub CLI](https://cli.github.com) and write access. Or skip it - the briefs stand
alone as files.

## Before you start anything

Read [ONBOARDING.md](ONBOARDING.md) §7, "Things that will get your PR sent back". It's short,
and it's the difference between one round of review and three.
