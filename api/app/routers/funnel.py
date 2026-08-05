"""Placement-funnel endpoint.

The recruiting funnel is: a consultant is **submitted** to a job, gets an **interview**, gets an
**offer**, and is **placed** (or **rejected** somewhere along the way).

Honest caveat, and it matters: `fact_pipeline` currently stores one row per candidate/job with a
single *current* stage, so what we return is a **distribution across stages**, not true
stage-to-stage conversion. Real conversion needs the full stage history per candidate - that is
task DATA-03 in docs/TASKS.md. When that lands, this endpoint gets conversion rates and the
`pct_of_total` field is replaced.
"""

from fastapi import APIRouter

from ..db import query_all
from ..models import Funnel

router = APIRouter(prefix="/api", tags=["funnel"])

# The order a candidate actually moves through, so the chart doesn't sort itself alphabetically.
STAGE_ORDER = ["submitted", "interview", "offer", "placed", "rejected"]


@router.get("/funnel", response_model=Funnel)
def funnel():
    """Candidate counts per pipeline stage."""
    rows = query_all(
        """
        SELECT stage, count(*) AS count
        FROM fact_pipeline
        GROUP BY stage
        """
    )
    counts = {r["stage"]: r["count"] for r in rows}
    total = sum(counts.values())

    ordered = [
        {
            "stage": stage,
            "count": counts.get(stage, 0),
            "pct_of_total": round(100.0 * counts.get(stage, 0) / total, 1) if total else 0.0,
        }
        for stage in STAGE_ORDER
    ]
    # Any stage the seed grows later still shows up, just after the known ones.
    ordered += [
        {
            "stage": stage,
            "count": count,
            "pct_of_total": round(100.0 * count / total, 1) if total else 0.0,
        }
        for stage, count in counts.items()
        if stage not in STAGE_ORDER
    ]
    return Funnel(rows=ordered, total=total)
