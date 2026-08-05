"""Shared test setup for the API.

Every API test runs against a **real database built from the seed generator** - a throwaway
SQLite file, created once per test session. No mocks: if the SQL is wrong, the test fails,
which is the point.

That also means these tests exercise `data-platform/load_seed.py` for free, so a broken loader
turns CI red before anyone notices at 9am on a Monday.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def seeded_database(tmp_path_factory):
    """Build a SQLite gold layer from the seed generator and point the API at it."""
    db_path = tmp_path_factory.mktemp("gold") / "test.db"
    url = f"sqlite:///{db_path}"

    result = subprocess.run(
        [sys.executable, str(ROOT / "data-platform" / "load_seed.py")],
        cwd=ROOT,
        env={**os.environ, "DATABASE_URL": url},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"seed loader failed:\n{result.stdout}\n{result.stderr}"

    os.environ["DATABASE_URL"] = url
    yield url
    os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="session")
def client(seeded_database):
    """A FastAPI test client. Imported late so it picks up DATABASE_URL above."""
    from app.main import app
    from fastapi.testclient import TestClient

    return TestClient(app)
