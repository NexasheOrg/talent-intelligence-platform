"""Tests for the data-quality checks.

Two things are tested, and the second one matters more than it looks:

  1. the checks pass on good data
  2. the checks **fail** on bad data

Without (2) you can ship a check suite that is green because it never actually looks at
anything, and nobody notices until a broken transform reaches a dashboard.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data-platform"))
sys.path.insert(0, str(ROOT / "data-platform" / "quality"))


@pytest.fixture()
def gold_db(tmp_path, monkeypatch):
    """A freshly seeded SQLite gold layer, wired up as DATABASE_URL."""
    db_path = tmp_path / "gold.db"
    url = f"sqlite:///{db_path}"

    result = subprocess.run(
        [sys.executable, str(ROOT / "data-platform" / "load_seed.py")],
        cwd=ROOT,
        env={**os.environ, "DATABASE_URL": url},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    monkeypatch.setenv("DATABASE_URL", url)
    return db_path


def run_checks():
    import checks

    return checks.run()


def test_seeded_data_passes_every_check(gold_db):
    assert run_checks() == 0


def test_an_orphaned_fact_row_is_caught(gold_db):
    """Point a bench row at a consultant who doesn't exist - integrity must catch it."""
    conn = sqlite3.connect(gold_db)
    conn.execute("UPDATE fact_bench SET consultant_id = 999999 WHERE bench_id = 1")
    conn.commit()
    conn.close()

    assert run_checks() == 1


def test_an_unrecognised_status_is_caught(gold_db):
    conn = sqlite3.connect(gold_db)
    conn.execute("UPDATE dim_consultant SET status = 'on holiday' WHERE consultant_id = 1")
    conn.commit()
    conn.close()

    assert run_checks() == 1


def test_impossible_hours_are_caught(gold_db):
    conn = sqlite3.connect(gold_db)
    conn.execute("UPDATE fact_timesheets SET hours_billable = 500 WHERE timesheet_id = 1")
    conn.commit()
    conn.close()

    assert run_checks() == 1
