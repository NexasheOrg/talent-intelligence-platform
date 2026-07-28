# api

Backend API that serves the gold layer to the web app, with auth + RBAC. Owns the repo's
CI/CD pipeline.

- `src/` - FastAPI (Python) service, endpoints, RBAC, request/response contracts

**Reads only the gold layer** - never bronze/silver. Roles: recruiter / delivery manager /
exec each see a different slice. Also proxies the ML scoring endpoint to the web app.
Keeping the API in Python means the whole backend (API + ML + AI) is one language and deploys
together. **Stack:** FastAPI, Python, Docker, GitHub Actions.

**M0 (built):** `main.py` serves `/health`, `/api/utilization`, and `/api/bench-by-seniority`
from the gold layer. Runs as part of `docker compose up` (root), on http://localhost:8000.
Next: auth + RBAC, and proxy the ML scoring endpoint.

## Running it locally, with hot reload

`docker compose up` (from the repo root) runs the API for you. Use the steps below instead when
you are editing `main.py` and want it to reload on save.

Python packages go in a **virtual environment**, never system-wide. Installing without one
fails on a Mac with `error: externally-managed-environment` - that is expected. From the repo
root, once:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r api/requirements.txt -r requirements-dev.txt
```

Then start Postgres (with the seed data loaded) and run the API against it:

```bash
docker compose up -d db loader
DATABASE_URL=postgresql://tip:tip@localhost:5433/tip uvicorn main:app --reload --app-dir api --port 8000
```

Port **5433** is deliberate: `docker-compose.yml` maps Postgres to 5433 on the host so it does
not clash with a Postgres you may already run on 5432.

Check it: `curl localhost:8000/health` and `curl localhost:8000/api/utilization`.

New terminals only need `source .venv/bin/activate`; `deactivate` when done. `.venv/` is
git-ignored.
