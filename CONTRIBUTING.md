# Contributing

This is how we work so several people can move at once without stepping on each other. If you're
new, read this once fully - it's short.

Never run the app before? Start with [`docs/WINDOWS-SETUP.md`](docs/WINDOWS-SETUP.md), then
[`docs/ONBOARDING.md`](docs/ONBOARDING.md).

## Picking work

- Open tasks are in [`docs/TASKS.md`](docs/TASKS.md), across five tracks: frontend, backend,
  data, AI/ML and devops. **Nothing is pre-assigned** - pick what you want to get good at.
- Every piece of work has an issue. Labels: `data-platform`, `infra`, `api`, `web`, `ml`,
  `ai-assistant`, `devops`, `docs`, plus `good-first-issue`.
- **Assign yourself before you start**, and say so in the team chat. Two people discovering
  they built the same endpoint is a bad afternoon for both of them.
- Comment on the issue when you're blocked. Blocked-and-quiet is the expensive state.

## Branching & PRs

- `main` is always deployable. Never push to it directly.
- Branch per task: `feature/<area>-<short-desc>`, e.g. `feature/api-bench-endpoint`.
- Open a PR early (draft is fine). Small PRs > big PRs - a PR touching 40 files gets a slow,
  shallow review; one touching 3 gets a fast, useful one.
- Every PR needs **one review**. Being asked to change something is the normal outcome of a
  review, not a criticism.
- CI must be green before merge.

## Commits

Present tense, scoped: `api: add RBAC middleware`, `data-platform: build silver timesheets`.

## The golden rules

1. **No real or customer data in git - ever.** Only the synthetic seed generator.
2. **Don't break the gold schema** without a PR that also updates
   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Every other layer builds on those names.
3. **Portable SQL only.** Everything runs on Postgres *and* SQLite, so nobody is blocked on
   Docker. Placeholders are `?`. CI checks both.
4. **Never paste user input into a SQL string.** Parameters, always.
5. **Your slice must run locally** from seed data before you call it done.
6. Write a test for anything with logic. A dashboard change needs a screenshot in the PR.

## Local dev

Windows: double-click `START-HERE.bat`. macOS/Linux: `./scripts/start.sh`. Or by hand:

```bash
docker compose up --build   # db + loader + api + assistant + web
```

Dashboard at <http://localhost:8080>, API docs at <http://localhost:8000/docs>, assistant at
<http://localhost:8100/docs>. Stop with `STOP.bat` or `docker compose down`.

No Docker? [`docs/RUN-WITHOUT-DOCKER.md`](docs/RUN-WITHOUT-DOCKER.md).

Hot reload while you're editing: [`docs/ONBOARDING.md`](docs/ONBOARDING.md) §3.

## Before you open a PR

```bash
ruff check .                              # lint
python -m pytest                          # all Python tests
python data-platform/quality/checks.py    # if you touched data-platform
cd web && npm test && npm run build       # if you touched web
```

CI runs all of this plus a Postgres-compatibility job. Finding out here is faster than finding
out there.

## Definition of done

Runs locally from seed · has a test or a screenshot · reviewed · CI green · issue closed.
