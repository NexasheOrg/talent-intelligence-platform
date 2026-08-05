"""Loader: generate synthetic seed data, then load it into the gold schema.

This is the thin end-to-end proof of the data platform: seed CSVs -> gold tables.
Later milestones replace this with real bronze/silver/gold transforms (see docs/ROADMAP.md).

It supports two databases on purpose:

    postgresql://tip:tip@db:5432/tip     the Docker stack (docker compose up)
    sqlite:///data/local/tip.db          the no-Docker fallback, Python only

Both are loaded from the same `models/gold_schema.sql`, so the gold contract stays identical
whichever way you run. Keep it that way - see the header of that file.

Usage:
    python data-platform/load_seed.py                      # SQLite into data/local/tip.db
    DATABASE_URL=postgresql://... python data-platform/load_seed.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_SCRIPT = ROOT / "data" / "seed" / "generate_seed.py"
SEED_OUT = ROOT / "data" / "seed" / "out"
SCHEMA_SQL = ROOT / "data-platform" / "models" / "gold_schema.sql"

DEFAULT_URL = "sqlite:///data/local/tip.db"

# Load order matters: dimensions before the facts that reference them.
TABLES = [
    "dim_consultant", "dim_client", "dim_job",
    "fact_pipeline", "fact_placements", "fact_bench", "fact_timesheets",
]


def is_postgres(url):
    return url.startswith("postgres")


def sqlite_path(url):
    """Turn a sqlite:///relative/path URL into an absolute Path under the repo root."""
    raw = url.split("sqlite:///", 1)[1]
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def connect(url, attempts=20, delay=1.5):
    """Open a connection. Postgres may still be booting, so retry it a few times."""
    if not is_postgres(url):
        import sqlite3

        path = sqlite_path(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path)

    import psycopg2

    for i in range(1, attempts + 1):
        try:
            return psycopg2.connect(url)
        except psycopg2.OperationalError:
            print(f"  database not ready (attempt {i}/{attempts}), retrying...")
            time.sleep(delay)
    raise SystemExit(
        "Could not connect to the database.\n"
        "If you are using Docker, check that Docker Desktop is running."
    )


def run_schema(cur, url):
    """Create the gold tables. SQLite only executes one statement per execute() call."""
    sql = SCHEMA_SQL.read_text()
    if is_postgres(url):
        cur.execute(sql)
        return
    for statement in sql.split(";"):
        if statement.strip():
            cur.execute(statement)


def load_table(cur, url, table, csv_path):
    """Bulk-load one CSV. Postgres has COPY; SQLite gets a plain executemany."""
    if is_postgres(url):
        with open(csv_path, "r") as f:
            cur.copy_expert(
                f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')", f
            )
        return

    import csv

    with open(csv_path, "r", newline="") as f:
        reader = csv.reader(f)
        columns = next(reader)
        # Match Postgres's `NULL ''`: an empty CSV field means NULL, not an empty string.
        rows = [[value if value != "" else None for value in row] for row in reader]
    placeholders = ", ".join("?" for _ in columns)
    cur.executemany(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
    )


def main():
    url = os.environ.get("DATABASE_URL") or DEFAULT_URL
    kind = "Postgres" if is_postgres(url) else f"SQLite ({sqlite_path(url)})"

    print(f"Loading the gold layer into {kind}")
    print("1/3 generating synthetic seed data...")
    subprocess.run([sys.executable, str(SEED_SCRIPT)], check=True)

    print("2/3 creating gold schema...")
    conn = connect(url)
    cur = conn.cursor()
    run_schema(cur, url)

    print("3/3 loading tables...")
    for table in TABLES:
        load_table(cur, url, table, SEED_OUT / f"{table}.csv")
        cur.execute(f"SELECT count(*) FROM {table}")
        print(f"    {table:18} {cur.fetchone()[0]:6d} rows")

    conn.commit()
    cur.close()
    conn.close()
    print("done: gold schema loaded.")


if __name__ == "__main__":
    main()
