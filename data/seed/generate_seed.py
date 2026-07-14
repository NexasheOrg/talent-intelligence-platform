"""
Synthetic seed-data generator for TIP.

Produces realistic-but-fake staffing data so every layer can develop locally with NO real or
customer data. Writes CSVs to data/seed/out/ matching the gold star schema in
docs/ARCHITECTURE.md.

Usage:
    python data/seed/generate_seed.py            # default sizes
    python data/seed/generate_seed.py --consultants 500 --clients 40

Only the Python stdlib is required.
"""

import argparse
import csv
import os
import random
from datetime import date, timedelta

OUT = os.path.join(os.path.dirname(__file__), "out")

SKILLS = ["Java", "Python", "React", "PySpark", "Azure", "AWS", "SQL", "Databricks",
          "Spring Boot", "Node.js", "Snowflake", "dbt", "Kubernetes", "Angular"]
SENIORITY = ["Junior", "Mid", "Senior", "Lead"]
INDUSTRIES = ["Finance", "Healthcare", "Retail", "Automotive", "Telecom", "Public Sector"]
TIERS = ["Strategic", "Growth", "Standard"]
STAGES = ["submitted", "interview", "offer", "placed", "rejected"]


def _d(start_days_ago, span=720):
    """A random date within the last `span` days, at least `start_days_ago` ago."""
    return date.today() - timedelta(days=random.randint(start_days_ago, span))


def gen(n_consultants, n_clients, n_jobs, seed):
    random.seed(seed)  # deterministic seed data so everyone builds against the same numbers
    os.makedirs(OUT, exist_ok=True)

    # dim_consultant
    consultants = []
    for i in range(1, n_consultants + 1):
        status = random.choices(["placed", "bench", "onboarding"], [0.6, 0.3, 0.1])[0]
        consultants.append({
            "consultant_id": i,
            "name": f"Consultant {i:04d}",
            "skills": "|".join(random.sample(SKILLS, random.randint(2, 5))),
            "seniority": random.choice(SENIORITY),
            "location": random.choice(["Dallas", "Remote", "Hyderabad", "Bangalore", "NJ"]),
            "cost_rate": random.randint(35, 90),
            "hire_date": _d(30).isoformat(),
            "status": status,
        })

    # dim_client
    clients = [{
        "client_id": i,
        "name": f"Client {i:03d}",
        "industry": random.choice(INDUSTRIES),
        "tier": random.choice(TIERS),
        "start_date": _d(90).isoformat(),
    } for i in range(1, n_clients + 1)]

    # dim_job
    jobs = [{
        "job_id": i,
        "client_id": random.randint(1, n_clients),
        "title": random.choice(["Data Engineer", "Full Stack Dev", "ML Engineer",
                                 "Cloud Engineer", "QA Engineer"]),
        "skills_required": "|".join(random.sample(SKILLS, random.randint(2, 4))),
        "open_date": _d(5, 400).isoformat(),
        "status": random.choice(["open", "filled", "closed"]),
    } for i in range(1, n_jobs + 1)]

    # fact_pipeline
    pipeline, pid = [], 1
    for j in jobs:
        for _ in range(random.randint(1, 6)):
            pipeline.append({
                "pipeline_id": pid,
                "job_id": j["job_id"],
                "consultant_id": random.randint(1, n_consultants),
                "stage": random.choices(STAGES, [0.4, 0.25, 0.1, 0.15, 0.1])[0],
                "stage_date": _d(1, 365).isoformat(),
            })
            pid += 1

    # fact_placements
    placements = []
    for pi, c in enumerate([c for c in consultants if c["status"] == "placed"], start=1):
        bill = c["cost_rate"] + random.randint(20, 60)
        placements.append({
            "placement_id": pi,
            "consultant_id": c["consultant_id"],
            "client_id": random.randint(1, n_clients),
            "job_id": random.randint(1, n_jobs),
            "start_date": _d(15, 500).isoformat(),
            "end_date": "",
            "bill_rate": bill,
            "margin": bill - c["cost_rate"],
        })

    # fact_bench
    bench = []
    for bi, c in enumerate([c for c in consultants if c["status"] == "bench"], start=1):
        start = _d(1, 200)
        bench.append({
            "bench_id": bi,
            "consultant_id": c["consultant_id"],
            "bench_start": start.isoformat(),
            "bench_end": "",
            "days_on_bench": (date.today() - start).days,
        })

    # fact_timesheets (last 8 weeks, placed consultants)
    timesheets, tid = [], 1
    for c in [c for c in consultants if c["status"] == "placed"]:
        for w in range(8):
            day = date.today() - timedelta(weeks=w)
            billable = random.randint(24, 40)
            timesheets.append({
                "timesheet_id": tid,
                "consultant_id": c["consultant_id"],
                "week_ending": day.isoformat(),
                "hours_billable": billable,
                "hours_bench": max(0, 40 - billable),
            })
            tid += 1

    tables = {
        "dim_consultant": consultants, "dim_client": clients, "dim_job": jobs,
        "fact_pipeline": pipeline, "fact_placements": placements,
        "fact_bench": bench, "fact_timesheets": timesheets,
    }
    for name, rows in tables.items():
        path = os.path.join(OUT, f"{name}.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print(f"  {name:18} {len(rows):6d} rows -> {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate synthetic TIP seed data.")
    ap.add_argument("--consultants", type=int, default=300)
    ap.add_argument("--clients", type=int, default=25)
    ap.add_argument("--jobs", type=int, default=120)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    print("Generating synthetic seed data (no real data):")
    gen(a.consultants, a.clients, a.jobs, a.seed)
    print("Done. Output in data/seed/out/ (git-ignored).")
