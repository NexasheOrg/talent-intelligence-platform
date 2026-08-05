"""Turn the gold layer into a feature table.

Kept separate from training on purpose. Features are the part you'll iterate on most, they're
the part most likely to leak the answer, and they have to be computed identically at training
time and at scoring time - a separate module makes all three easier.

Only the Python standard library is needed here, so you can inspect the features without
installing scikit-learn.
"""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SENIORITY_RANK = {"Junior": 0, "Mid": 1, "Senior": 2, "Lead": 3}

FEATURE_NAMES = ["seniority_rank", "cost_rate", "tenure_days", "skill_count", "is_remote"]

# What we're predicting: will this benched consultant still be on the bench after 45 days?
# That's a real, useful question - long bench time is the single biggest margin leak in a
# staffing business - and unlike attrition it has a label the seed data actually contains.
LONG_BENCH_DAYS = 45


def _connect():
    """Read the gold layer. Mirrors data-platform/db.py; see the note there about duplication."""
    url = os.environ.get("DATABASE_URL") or f"sqlite:///{ROOT / 'data' / 'local' / 'tip.db'}"
    if url.startswith("postgres"):
        import psycopg2

        return psycopg2.connect(url), True

    raw = url.split("sqlite:///", 1)[1]
    path = Path(raw)
    path = path if path.is_absolute() else ROOT / path
    if not path.exists():
        sys.exit(
            f"No database at {path}.\n"
            f"Build it first:  python data-platform/load_seed.py"
        )
    return sqlite3.connect(path), False


def _days_since(value, today):
    if not value:
        return 0
    try:
        return (today - date.fromisoformat(str(value)[:10])).days
    except ValueError:
        return 0


def load_training_rows(today=None):
    """Return (feature_rows, labels, consultant_ids) for every consultant with a bench record.

    A row is one benched consultant. The label is 1 if they were on the bench longer than
    LONG_BENCH_DAYS.
    """
    today = today or date.today()
    conn, _ = _connect()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.consultant_id, c.seniority, c.cost_rate, c.hire_date, c.skills,
                   c.location, b.days_on_bench
            FROM fact_bench b
            JOIN dim_consultant c ON c.consultant_id = b.consultant_id
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    features, labels, ids = [], [], []
    for consultant_id, seniority, cost_rate, hire_date, skills, location, days_on_bench in rows:
        features.append([
            SENIORITY_RANK.get(seniority, 1),
            float(cost_rate or 0),
            float(_days_since(hire_date, today)),
            float(len((skills or "").split("|"))),
            1.0 if location == "Remote" else 0.0,
        ])
        labels.append(1 if (days_on_bench or 0) > LONG_BENCH_DAYS else 0)
        ids.append(consultant_id)

    return features, labels, ids


if __name__ == "__main__":
    X, y, ids = load_training_rows()
    print(f"{len(X)} rows, {sum(y)} positive ({100 * sum(y) / max(len(y), 1):.0f}%)")
    print(f"features: {', '.join(FEATURE_NAMES)}")
    for row, label, consultant_id in list(zip(X, y, ids))[:5]:
        print(f"  consultant {consultant_id}: {row} -> {label}")
