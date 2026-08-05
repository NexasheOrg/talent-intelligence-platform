"""Data-quality checks over the gold layer.

Run after loading, or any time you change a transform:

    python data-platform/quality/checks.py

Exits non-zero if any check fails, so CI and the loader can both depend on it.

The point of this file is that **a silent data bug is worse than a loud crash**. A dashboard
showing a confidently wrong utilisation number does more damage than one showing an error, so
we assert the things that must be true and fail loudly when they aren't.

Adding a check is a function with the `@check` decorator that raises `Failed` with a message
explaining what's wrong. Three kinds are worth having:
  * **completeness** - the rows arrived at all
  * **validity** - values are inside their allowed set
  * **integrity** - facts point at dimensions that exist
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db import query_all, query_value  # noqa: E402

CHECKS = []


class Failed(Exception):
    """Raised by a check when the data is wrong."""


def check(description):
    """Register a function as a data-quality check."""

    def decorate(fn):
        CHECKS.append((description, fn))
        return fn

    return decorate


GOLD_TABLES = [
    "dim_consultant", "dim_client", "dim_job",
    "fact_pipeline", "fact_placements", "fact_bench", "fact_timesheets",
]

VALID_STATUS = {"placed", "bench", "onboarding"}
VALID_SENIORITY = {"Junior", "Mid", "Senior", "Lead"}
VALID_STAGES = {"submitted", "interview", "offer", "placed", "rejected"}


# ---------------------------------------------------------------- completeness

@check("every gold table has rows")
def tables_not_empty():
    empty = [t for t in GOLD_TABLES if query_value(f"SELECT count(*) FROM {t}") == 0]
    if empty:
        raise Failed(f"empty tables: {', '.join(empty)} - did the loader finish?")


@check("no consultant is missing an id or a name")
def consultants_have_keys():
    bad = query_value(
        "SELECT count(*) FROM dim_consultant WHERE consultant_id IS NULL OR name IS NULL"
    )
    if bad:
        raise Failed(f"{bad} consultant rows have a null id or name")


# ---------------------------------------------------------------- validity

@check("consultant status is always one we recognise")
def consultant_status_valid():
    found = {row[0] for row in query_all("SELECT DISTINCT status FROM dim_consultant")}
    unexpected = found - VALID_STATUS
    if unexpected:
        raise Failed(f"unexpected status values: {sorted(unexpected)}")


@check("consultant seniority is always one we recognise")
def consultant_seniority_valid():
    found = {row[0] for row in query_all("SELECT DISTINCT seniority FROM dim_consultant")}
    unexpected = found - VALID_SENIORITY
    if unexpected:
        raise Failed(f"unexpected seniority values: {sorted(unexpected)}")


@check("pipeline stage is always one we recognise")
def pipeline_stage_valid():
    found = {row[0] for row in query_all("SELECT DISTINCT stage FROM fact_pipeline")}
    unexpected = found - VALID_STAGES
    if unexpected:
        raise Failed(f"unexpected pipeline stages: {sorted(unexpected)}")


@check("timesheet hours are never negative and never above a plausible week")
def timesheet_hours_sane():
    bad = query_value(
        """
        SELECT count(*) FROM fact_timesheets
        WHERE hours_billable < 0 OR hours_bench < 0 OR hours_billable + hours_bench > 80
        """
    )
    if bad:
        raise Failed(f"{bad} timesheet rows have negative or impossible hours")


@check("a placement never bills below what the consultant costs")
def placements_have_positive_margin():
    bad = query_value("SELECT count(*) FROM fact_placements WHERE margin <= 0")
    if bad:
        raise Failed(f"{bad} placements bill at or below cost - check the seed or the transform")


# ---------------------------------------------------------------- integrity

@check("every bench row points at a consultant that exists")
def bench_references_consultants():
    orphans = query_value(
        """
        SELECT count(*) FROM fact_bench b
        LEFT JOIN dim_consultant c ON c.consultant_id = b.consultant_id
        WHERE c.consultant_id IS NULL
        """
    )
    if orphans:
        raise Failed(f"{orphans} bench rows reference a consultant that isn't in dim_consultant")


@check("every timesheet points at a consultant that exists")
def timesheets_reference_consultants():
    orphans = query_value(
        """
        SELECT count(*) FROM fact_timesheets t
        LEFT JOIN dim_consultant c ON c.consultant_id = t.consultant_id
        WHERE c.consultant_id IS NULL
        """
    )
    if orphans:
        raise Failed(f"{orphans} timesheet rows reference a missing consultant")


@check("every job points at a client that exists")
def jobs_reference_clients():
    orphans = query_value(
        """
        SELECT count(*) FROM dim_job j
        LEFT JOIN dim_client c ON c.client_id = j.client_id
        WHERE c.client_id IS NULL
        """
    )
    if orphans:
        raise Failed(f"{orphans} jobs reference a missing client")


@check("nobody is on the bench twice at the same time")
def bench_has_no_duplicates():
    duplicates = query_all(
        """
        SELECT consultant_id, count(*) AS n FROM fact_bench
        WHERE bench_end IS NULL
        GROUP BY consultant_id
        HAVING count(*) > 1
        """
    )
    if duplicates:
        raise Failed(f"{len(duplicates)} consultants have more than one open bench record")


# ---------------------------------------------------------------- runner

def run():
    failures = []
    print(f"Running {len(CHECKS)} data-quality checks\n")

    for description, fn in CHECKS:
        try:
            fn()
        except Failed as failure:
            failures.append((description, str(failure)))
            print(f"  FAIL  {description}")
            print(f"        {failure}")
        else:
            print(f"  ok    {description}")

    print()
    if failures:
        print(f"{len(failures)} of {len(CHECKS)} checks failed.")
        return 1
    print(f"All {len(CHECKS)} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
