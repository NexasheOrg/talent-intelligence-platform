"""M0 API: a thin FastAPI service reading the gold layer from Postgres.

Serves one real dashboard endpoint (utilization & bench) plus a health check. RBAC, more
endpoints, and the ML/AI proxies come in later milestones (see docs/ROADMAP.md).
"""

import os

import psycopg2
import psycopg2.extras
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TIP API", version="0.1.0")

# Dev-only: allow the local web app to call the API. Tighten for real deployments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def query_one(sql):
    """Run a single-row query and return it as a dict."""
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchone()
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/utilization")
def utilization():
    """Overall utilization and bench snapshot, computed from the gold layer."""
    row = query_one(
        """
        SELECT
            (SELECT count(*) FROM dim_consultant)                          AS total_consultants,
            (SELECT count(*) FROM fact_bench)                              AS consultants_on_bench,
            COALESCE(SUM(hours_billable), 0)                              AS billable_hours,
            COALESCE(SUM(hours_bench), 0)                                 AS bench_hours
        FROM fact_timesheets
        """
    )
    billable = row["billable_hours"]
    bench = row["bench_hours"]
    total = billable + bench
    row["utilization_pct"] = round(100.0 * billable / total, 1) if total else 0.0
    return row


@app.get("/api/bench-by-seniority")
def bench_by_seniority():
    """How many benched consultants sit at each seniority level."""
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT c.seniority, count(*) AS on_bench
                FROM fact_bench b
                JOIN dim_consultant c ON c.consultant_id = b.consultant_id
                GROUP BY c.seniority
                ORDER BY on_bench DESC
                """
            )
            return {"rows": cur.fetchall()}
    finally:
        conn.close()
