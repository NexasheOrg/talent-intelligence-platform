"""Database access for the data-platform layer.

Yes, `api/app/db.py` looks similar. That duplication is deliberate: five people work on five
modules in parallel, and a shared library means one person's refactor breaks four other
branches on a Tuesday. Each module owns its own thin helper instead. If that ever stops being
worth it, consolidating is a small, obvious PR - but do it as a decision, not by accident.

Supports Postgres and SQLite, same as everything else here. Keep the SQL portable.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = f"sqlite:///{ROOT / 'data' / 'local' / 'tip.db'}"


def database_url():
    return os.environ.get("DATABASE_URL") or DEFAULT_URL


def is_postgres(url=None):
    return (url or database_url()).startswith("postgres")


def _sqlite_file(url):
    raw = url.split("sqlite:///", 1)[1]
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


@contextmanager
def cursor():
    url = database_url()
    if is_postgres(url):
        import psycopg2

        conn = psycopg2.connect(url)
        try:
            with conn.cursor() as cur:
                yield cur
        finally:
            conn.close()
    else:
        path = _sqlite_file(url)
        if not path.exists():
            raise FileNotFoundError(
                f"No database at {path}. Build it first:\n"
                f"    python data-platform/load_seed.py"
            )
        conn = sqlite3.connect(path)
        try:
            yield conn.cursor()
        finally:
            conn.close()


def query_all(sql, params=()):
    """Return rows as a list of tuples. Write placeholders as `?`."""
    with cursor() as cur:
        cur.execute(sql.replace("?", "%s") if is_postgres() else sql, tuple(params))
        return cur.fetchall()


def query_value(sql, params=(), default=0):
    rows = query_all(sql, params)
    if not rows or rows[0][0] is None:
        return default
    return rows[0][0]
