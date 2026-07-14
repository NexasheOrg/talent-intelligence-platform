"""M0 loader: generate synthetic seed data, then load it into the gold schema in Postgres.

This is the thin end-to-end proof of the data platform: seed -> gold tables in Postgres.
Later milestones replace this with real bronze/silver/gold transforms (see docs/ROADMAP.md).

Env:
    DATABASE_URL   postgres connection string (e.g. postgresql://tip:tip@db:5432/tip)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
SEED_SCRIPT = ROOT / "data" / "seed" / "generate_seed.py"
SEED_OUT = ROOT / "data" / "seed" / "out"
SCHEMA_SQL = ROOT / "data-platform" / "models" / "gold_schema.sql"

TABLES = [
    "dim_consultant", "dim_client", "dim_job",
    "fact_pipeline", "fact_placements", "fact_bench", "fact_timesheets",
]


def connect_with_retry(url, attempts=20, delay=1.5):
    """Postgres may still be starting when this container runs; retry a few times."""
    for i in range(1, attempts + 1):
        try:
            return psycopg2.connect(url)
        except psycopg2.OperationalError:
            print(f"  db not ready (attempt {i}/{attempts}), retrying...")
            time.sleep(delay)
    raise SystemExit("Could not connect to the database.")


def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set.")

    print("1/3 generating synthetic seed data...")
    subprocess.run([sys.executable, str(SEED_SCRIPT)], check=True)

    print("2/3 creating gold schema...")
    conn = connect_with_retry(url)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute(SCHEMA_SQL.read_text())

    print("3/3 loading tables...")
    for table in TABLES:
        csv_path = SEED_OUT / f"{table}.csv"
        with open(csv_path, "r") as f:
            cur.copy_expert(
                f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')", f
            )
        cur.execute(f"SELECT count(*) FROM {table}")
        print(f"    {table:18} {cur.fetchone()[0]:6d} rows")

    conn.commit()
    cur.close()
    conn.close()
    print("done: gold schema loaded.")


if __name__ == "__main__":
    main()
