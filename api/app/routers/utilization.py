"""Utilization & bench endpoints - the numbers behind the first dashboard.

Utilization is the headline metric of a staffing business: of the hours we paid for, how many
did a client pay us for? Everything here is derived from `fact_timesheets` and `fact_bench`.
"""

from fastapi import APIRouter

from ..db import query_all, query_one
from ..models import BenchBySeniority, Utilization, UtilizationTrend

router = APIRouter(prefix="/api", tags=["utilization"])


def _pct(billable, bench):
    total = (billable or 0) + (bench or 0)
    return round(100.0 * billable / total, 1) if total else 0.0


@router.get("/utilization", response_model=Utilization)
def utilization():
    """Overall utilization and bench snapshot, computed from the gold layer."""
    row = query_one(
        """
        SELECT
            (SELECT count(*) FROM dim_consultant) AS total_consultants,
            (SELECT count(*) FROM fact_bench)     AS consultants_on_bench,
            COALESCE(SUM(hours_billable), 0)      AS billable_hours,
            COALESCE(SUM(hours_bench), 0)         AS bench_hours
        FROM fact_timesheets
        """
    )
    return Utilization(
        total_consultants=row["total_consultants"],
        consultants_on_bench=row["consultants_on_bench"],
        billable_hours=int(row["billable_hours"]),
        bench_hours=int(row["bench_hours"]),
        utilization_pct=_pct(row["billable_hours"], row["bench_hours"]),
    )


@router.get("/bench-by-seniority", response_model=BenchBySeniority)
def bench_by_seniority():
    """How many benched consultants sit at each seniority level."""
    rows = query_all(
        """
        SELECT c.seniority AS seniority, count(*) AS on_bench
        FROM fact_bench b
        JOIN dim_consultant c ON c.consultant_id = b.consultant_id
        GROUP BY c.seniority
        ORDER BY on_bench DESC
        """
    )
    return BenchBySeniority(rows=rows)


@router.get("/utilization/trend", response_model=UtilizationTrend)
def utilization_trend():
    """Weekly billable vs bench hours - the series behind the trend chart.

    The seed generates eight weeks of timesheets, so expect eight points. Oldest first, because
    charts read left to right.
    """
    rows = query_all(
        """
        SELECT week_ending,
               COALESCE(SUM(hours_billable), 0) AS billable_hours,
               COALESCE(SUM(hours_bench), 0)    AS bench_hours
        FROM fact_timesheets
        GROUP BY week_ending
        ORDER BY week_ending
        """
    )
    return UtilizationTrend(
        rows=[
            {
                "week_ending": str(r["week_ending"]),
                "billable_hours": int(r["billable_hours"]),
                "bench_hours": int(r["bench_hours"]),
                "utilization_pct": _pct(r["billable_hours"], r["bench_hours"]),
            }
            for r in rows
        ]
    )
