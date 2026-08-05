"""Unit tests for the baseline risk scorer.

No database, no HTTP - just the function. These run in milliseconds, so they're the right place
to pin down edge cases. `today` is injected so the tests don't start failing next month.

If you replace the heuristic with a trained model (task ML-02), these tests should still pass:
they assert *properties* the scorer must have, not the exact numbers a particular model emits.
"""

from datetime import date

from app.risk import score

TODAY = date(2026, 6, 1)
LONG_AGO = "2020-01-01"


def test_a_long_bench_scores_higher_than_a_short_one():
    short = score({"consultant_id": 1, "seniority": "Mid", "status": "bench",
                   "days_on_bench": 5, "hire_date": LONG_AGO}, today=TODAY)
    long = score({"consultant_id": 2, "seniority": "Mid", "status": "bench",
                  "days_on_bench": 200, "hire_date": LONG_AGO}, today=TODAY)
    assert long["risk_score"] > short["risk_score"]


def test_score_never_leaves_the_zero_to_one_range():
    worst = score({"consultant_id": 3, "seniority": "Junior", "status": "bench",
                   "days_on_bench": 5000, "hire_date": TODAY.isoformat()}, today=TODAY)
    assert 0.0 <= worst["risk_score"] <= 1.0


def test_a_placed_consultant_with_no_bench_time_is_low_risk():
    result = score({"consultant_id": 4, "seniority": "Lead", "status": "placed",
                    "days_on_bench": None, "hire_date": LONG_AGO}, today=TODAY)
    assert result["band"] == "low"


def test_factors_are_ordered_by_impact():
    result = score({"consultant_id": 5, "seniority": "Junior", "status": "bench",
                    "days_on_bench": 150, "hire_date": LONG_AGO}, today=TODAY)
    contributions = [f["contribution"] for f in result["factors"]]
    assert contributions == sorted(contributions, reverse=True)


def test_a_missing_hire_date_does_not_blow_up():
    result = score({"consultant_id": 6, "seniority": "Mid", "status": "bench",
                    "days_on_bench": 10, "hire_date": None}, today=TODAY)
    assert result["model"]
