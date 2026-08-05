"""Database access for the API.

The API reads **only the gold layer** (see docs/ARCHITECTURE.md). Everything goes through the
two helpers at the bottom of this file: `query_all` and `query_one`.

Two databases are supported on purpose:

    postgresql://tip:tip@db:5432/tip     the Docker stack
    sqlite:///data/local/tip.db          the no-Docker fallback (Python only)

so a teammate who can't install Docker Desktop is never blocked. The cost is that **every
query in this service must be portable SQL**: no Postgres-only functions, and write
placeholders as `?` (this module rewrites them to `%s` for Postgres). If you genuinely need
something Postgres-only, say so in your PR - don't silently break the SQLite path.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

# api/app/db.py -> api/app -> api -> repo root
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = f"sqlite:///{ROOT / 'data' / 'local' / 'tip.db'}"


def database_url():
    return os.environ.get("DATABASE_URL") or DEFAULT_URL


def is_postgres(url=None):
    return (url or database_url()).startswith("postgres")


def backend_name():
    """Which database we're talking to - surfaced on /health so it's easy to tell."""
    return "postgres" if is_postgres() else "sqlite"


def _sqlite_file(url):
    raw = url.split("sqlite:///", 1)[1]
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


@contextmanager
def _cursor():
    """Yield a cursor and always close the connection, even if the query raises."""
    url = database_url()
    if is_postgres(url):
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                yield cur
        finally:
            conn.close()
    else:
        path = _sqlite_file(url)
        if not path.exists():
            raise FileNotFoundError(
                f"No local database at {path}. Run the loader first:\n"
                f"    python data-platform/load_seed.py"
            )
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn.cursor()
        finally:
            conn.close()


def _adapt(sql):
    """Queries are written with `?`; psycopg2 wants `%s`."""
    return sql.replace("?", "%s") if is_postgres() else sql


def _clean(value):
    """Make a value JSON-safe: dates become ISO strings, Decimals become floats."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _row_to_dict(row):
    # `.keys()` is required, not a style slip: iterating a sqlite3.Row directly yields its
    # *values*, not its column names, so the shorter `for key in row` silently builds garbage.
    # Ruff's SIM118 doesn't know that - hence the suppression.
    return {key: _clean(row[key]) for key in row.keys()}  # noqa: SIM118


def query_all(sql, params=()):
    """Run a query and return every row as a list of plain dicts."""
    with _cursor() as cur:
        cur.execute(_adapt(sql), tuple(params))
        return [_row_to_dict(row) for row in cur.fetchall()]


def query_one(sql, params=()):
    """Run a query and return the first row as a dict, or None if there is no row."""
    with _cursor() as cur:
        cur.execute(_adapt(sql), tuple(params))
        row = cur.fetchone()
        return _row_to_dict(row) if row is not None else None


def query_value(sql, params=(), default=0):
    """Run a query that selects exactly one column and return that single value."""
    row = query_one(sql, params)
    if not row:
        return default
    value = next(iter(row.values()))
    return default if value is None else value
