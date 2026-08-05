"""TIP API - a FastAPI service over the gold layer.

Start here if you're new to this folder:

    app/db.py         how we talk to the database (Postgres or SQLite)
    app/models.py     the response shapes - the contract with the web app
    app/routers/      one file per topic; each is a small, self-contained APIRouter
    app/risk.py       the baseline attrition scorer
    tests/            pytest; these run in CI on every PR

Adding an endpoint is four steps: add a model, add a route to the right router (or a new
router file, registered below), add a test, then mirror the type in web/src/lib/types.ts.

Interactive docs while it's running: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import consultants, funnel, health, utilization

app = FastAPI(
    title="TIP API",
    version="0.2.0",
    description="Talent & Delivery Intelligence Platform - serving layer over the gold schema.",
)

# Dev-only: let the Vite dev server on :5173 and the nginx build on :8080 both call us.
# Tighten this to known origins before anything is deployed - see task API-05.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(utilization.router)
app.include_router(funnel.router)
app.include_router(consultants.router)
