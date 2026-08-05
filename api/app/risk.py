"""Baseline attrition-risk scorer.

This is a **deliberately simple, explainable heuristic**, not machine learning. It exists so the
rest of the stack (endpoint contract, web badge, tests) can be built and reviewed today, and so
there is a baseline for a real model to beat.

Replacing this with a trained model is task ML-02 in docs/TASKS.md. The swap is meant to be
easy: keep `score(consultant)` returning the same shape, change `MODEL_NAME`, and every caller
and test keeps working. Whoever picks that up should report the new model's precision/recall
*against this baseline* - "better than nothing" is not a result.

Weights below are guesses by a human, and they sum to 1.0 by construction. Don't read them as
findings.
"""

from datetime import date

MODEL_NAME = "baseline-heuristic-v0"

BENCH_DAYS_FOR_MAX_RISK = 180
WEIGHT_BENCH = 0.55
WEIGHT_UNPLACED = 0.15
WEIGHT_NEW_HIRE = 0.15
SENIORITY_WEIGHT = {"Junior": 0.15, "Mid": 0.10, "Senior": 0.06, "Lead": 0.04}
NEW_HIRE_DAYS = 180


def _band(score):
    if score < 0.34:
        return "low"
    if score < 0.67:
        return "medium"
    return "high"


def _days_since(iso_date, today):
    if not iso_date:
        return None
    try:
        return (today - date.fromisoformat(str(iso_date)[:10])).days
    except ValueError:
        return None


def score(consultant, today=None):
    """Score one consultant.

    Args:
        consultant: a dict with at least `consultant_id`, `seniority`, `status`, and
            optionally `days_on_bench` and `hire_date`.
        today: injectable for tests, so results don't drift with the calendar.

    Returns:
        A dict matching `models.RiskScore`.
    """
    today = today or date.today()
    factors = []

    days_on_bench = consultant.get("days_on_bench") or 0
    bench_ratio = min(days_on_bench / BENCH_DAYS_FOR_MAX_RISK, 1.0)
    if bench_ratio:
        factors.append(
            {"label": f"{days_on_bench} days on bench", "contribution": round(bench_ratio * WEIGHT_BENCH, 3)}
        )

    if consultant.get("status") != "placed":
        factors.append({"label": "Not currently placed", "contribution": WEIGHT_UNPLACED})

    seniority = consultant.get("seniority") or "Mid"
    factors.append(
        {
            "label": f"{seniority} seniority",
            "contribution": SENIORITY_WEIGHT.get(seniority, 0.10),
        }
    )

    tenure_days = _days_since(consultant.get("hire_date"), today)
    if tenure_days is not None and tenure_days < NEW_HIRE_DAYS:
        factors.append(
            {"label": "Joined in the last 6 months", "contribution": WEIGHT_NEW_HIRE}
        )

    total = min(round(sum(f["contribution"] for f in factors), 3), 1.0)
    factors.sort(key=lambda f: f["contribution"], reverse=True)

    return {
        "consultant_id": consultant["consultant_id"],
        "risk_score": total,
        "band": _band(total),
        "factors": factors,
        "model": MODEL_NAME,
    }
