# api

The serving layer. Reads **only the gold layer** - never bronze/silver - and hands it to the web
app and anything else that asks. Keeping the API in Python means the whole backend (API + ML +
AI) is one language and deploys together. **Stack:** FastAPI, Python, Docker, GitHub Actions.

## What's here

```
app/
  main.py            the FastAPI app; registers the routers
  db.py              database access - read this first
  models.py          response shapes (Pydantic) = the contract with the web app
  risk.py            baseline attrition scorer (a heuristic, not ML - see ML-02)
  routers/
    health.py        /health
    utilization.py   /api/utilization, /api/bench-by-seniority, /api/utilization/trend
    funnel.py        /api/funnel
    consultants.py   /api/consultants (search, filter, paginate), detail, risk
tests/               pytest; runs against a real seeded database, no mocks
```

Live, interactive docs while it's running: <http://localhost:8000/docs>.

## Adding an endpoint

Four steps, in this order:

1. **Add the response model** to `models.py`. Agree the shape with whoever's building the UI
   before writing the query - it's much cheaper to change here than later.
2. **Add the route** to the right router, or a new file in `routers/` registered in `main.py`.
3. **Add a test** in `tests/`. Assert an invariant, not just a 200 - see `test_endpoints.py`.
4. **Mirror the type** in `web/src/lib/types.ts`.

## Two rules specific to this folder

**Portable SQL only.** Every query must run on Postgres *and* SQLite, so teammates who can't
install Docker aren't blocked. Write placeholders as `?`; `db.py` converts them for Postgres. No
Postgres-only functions without raising it in the PR.

**Never build SQL by string concatenation.** User input goes in as a parameter, always.
`routers/consultants.py` shows the pattern for dynamic filters.

## Running it locally, with hot reload

`docker compose up` (from the repo root) runs the API for you. Use the steps below when you're
editing it and want it to reload on save.

Python packages go in a **virtual environment**, never system-wide. Installing without one fails
on a Mac with `error: externally-managed-environment` - that is expected. From the repo root,
once:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r api\requirements.txt -r requirements-dev.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt -r requirements-dev.txt
```

Then start Postgres (with the seed data loaded) and run the API against it:

```powershell
docker compose up -d db loader
$env:DATABASE_URL = "postgresql://tip:tip@localhost:5433/tip"
python -m uvicorn app.main:app --app-dir api --port 8000 --reload
```

```bash
# macOS / Linux
docker compose up -d db loader
DATABASE_URL=postgresql://tip:tip@localhost:5433/tip \
  python -m uvicorn app.main:app --app-dir api --port 8000 --reload
```

Port **5433** is deliberate: `docker-compose.yml` maps Postgres to 5433 on the host so it does
not clash with a Postgres you may already run on 5432.

No Docker? Use `sqlite:///data/local/tip.db` as the `DATABASE_URL` and skip the compose line -
see [`docs/RUN-WITHOUT-DOCKER.md`](../docs/RUN-WITHOUT-DOCKER.md).

Check it: <http://localhost:8000/health> and <http://localhost:8000/docs>.
Tests: `python -m pytest api/tests`.

New terminals only need the activate line; `deactivate` when done. `.venv/` is git-ignored.

## Next

RBAC (recruiter / delivery manager / exec see different slices), client-health and billing
endpoints, and proxying the ML score once a real model exists. Tasks `API-01` … `API-05` in
[`docs/TASKS.md`](../docs/TASKS.md).
