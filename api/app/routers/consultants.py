"""Consultant list and detail.

This is the reference endpoint for **search + filter + pagination**. If you're adding a listing
endpoint (clients, jobs, placements), copy the shape here rather than inventing a new one:
filters build up a list of conditions and a matching list of params, and the same WHERE clause
feeds both the count query and the page query.

Note how the filters are parameterised. Never build SQL by pasting user input into the string -
that's how you get SQL injection, and it will be caught in review.
"""

from fastapi import APIRouter, HTTPException, Query

from ..db import query_all, query_one, query_value
from ..models import ConsultantDetail, ConsultantPage, RiskScore
from ..risk import score as score_risk

router = APIRouter(prefix="/api/consultants", tags=["consultants"])

MAX_PAGE_SIZE = 200


def _filters(q, status, seniority):
    """Turn the query params into a WHERE clause plus its parameters."""
    conditions, params = [], []
    if q:
        conditions.append("(LOWER(c.name) LIKE ? OR LOWER(c.skills) LIKE ?)")
        needle = f"%{q.lower()}%"
        params += [needle, needle]
    if status:
        conditions.append("c.status = ?")
        params.append(status)
    if seniority:
        conditions.append("c.seniority = ?")
        params.append(seniority)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where, params


@router.get("", response_model=ConsultantPage)
def list_consultants(
    q: str | None = Query(None, description="Free-text match on name or skills"),
    status: str | None = Query(None, description="placed / bench / onboarding"),
    seniority: str | None = Query(None, description="Junior / Mid / Senior / Lead"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=MAX_PAGE_SIZE),
):
    """One page of consultants, filtered and searchable."""
    where, params = _filters(q, status, seniority)

    total = query_value(
        f"SELECT count(*) AS total FROM dim_consultant c {where}", params
    )

    rows = query_all(
        f"""
        SELECT c.consultant_id, c.name, c.skills, c.seniority, c.location, c.status,
               b.days_on_bench
        FROM dim_consultant c
        LEFT JOIN fact_bench b ON b.consultant_id = c.consultant_id
        {where}
        ORDER BY c.consultant_id
        LIMIT ? OFFSET ?
        """,
        params + [page_size, (page - 1) * page_size],
    )

    pages = (total + page_size - 1) // page_size
    return ConsultantPage(rows=rows, total=total, page=page, page_size=page_size, pages=pages)


def _load_consultant(consultant_id):
    row = query_one(
        """
        SELECT c.consultant_id, c.name, c.skills, c.seniority, c.location, c.status,
               c.cost_rate, c.hire_date, b.days_on_bench
        FROM dim_consultant c
        LEFT JOIN fact_bench b ON b.consultant_id = c.consultant_id
        WHERE c.consultant_id = ?
        """,
        [consultant_id],
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"No consultant with id {consultant_id}")
    return row


@router.get("/{consultant_id}", response_model=ConsultantDetail)
def get_consultant(consultant_id: int):
    """One consultant, with their attrition-risk score attached."""
    row = _load_consultant(consultant_id)
    return ConsultantDetail(**row, risk=score_risk(row))


@router.get("/{consultant_id}/risk", response_model=RiskScore)
def get_consultant_risk(consultant_id: int):
    """Attrition risk for one consultant, with the factors that drove the score.

    Served by the baseline heuristic in `app/risk.py` today. Swapping in the trained model is
    task ML-02 - the response shape stays the same, only `model` changes.
    """
    return score_risk(_load_consultant(consultant_id))
