"""Endpoint tests.

Pattern to copy when you add an endpoint: assert the **status code**, the **shape**, and one
**invariant that would catch a wrong query** - not just that it returned 200. A test that only
checks for 200 passes happily while the numbers are nonsense.
"""


def test_health_reports_its_backend(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["database"] in {"postgres", "sqlite"}


def test_utilization_numbers_are_internally_consistent(client):
    response = client.get("/api/utilization")
    assert response.status_code == 200
    body = response.json()

    assert body["total_consultants"] > 0
    assert body["consultants_on_bench"] <= body["total_consultants"]
    # The percentage must actually match the hours it claims to be derived from.
    total_hours = body["billable_hours"] + body["bench_hours"]
    expected = round(100.0 * body["billable_hours"] / total_hours, 1)
    assert body["utilization_pct"] == expected


def test_bench_by_seniority_covers_every_benched_consultant(client):
    rows = client.get("/api/bench-by-seniority").json()["rows"]
    total_on_bench = client.get("/api/utilization").json()["consultants_on_bench"]
    assert sum(r["on_bench"] for r in rows) == total_on_bench


def test_utilization_trend_is_ordered_oldest_first(client):
    rows = client.get("/api/utilization/trend").json()["rows"]
    assert len(rows) > 1
    assert rows == sorted(rows, key=lambda r: r["week_ending"])


def test_funnel_counts_add_up_to_the_total(client):
    body = client.get("/api/funnel").json()
    assert sum(r["count"] for r in body["rows"]) == body["total"]
    assert body["rows"][0]["stage"] == "submitted"


def test_consultants_pagination_does_not_lose_or_repeat_rows(client):
    first = client.get("/api/consultants?page=1&page_size=10").json()
    second = client.get("/api/consultants?page=2&page_size=10").json()

    assert first["total"] == second["total"]
    assert len(first["rows"]) == 10
    assert first["pages"] == -(-first["total"] // 10)

    ids_first = {r["consultant_id"] for r in first["rows"]}
    ids_second = {r["consultant_id"] for r in second["rows"]}
    assert not ids_first & ids_second


def test_consultants_status_filter_only_returns_that_status(client):
    body = client.get("/api/consultants?status=bench&page_size=50").json()
    assert body["total"] > 0
    assert all(r["status"] == "bench" for r in body["rows"])


def test_consultants_search_matches_name_or_skills(client):
    body = client.get("/api/consultants?q=python&page_size=50").json()
    assert body["total"] > 0
    assert all("python" in r["skills"].lower() for r in body["rows"])


def test_unknown_consultant_is_a_404_not_a_crash(client):
    assert client.get("/api/consultants/999999").status_code == 404


def test_risk_score_is_bounded_and_explained(client):
    body = client.get("/api/consultants/1/risk").json()
    assert 0.0 <= body["risk_score"] <= 1.0
    assert body["band"] in {"low", "medium", "high"}
    assert body["factors"], "a score with no factors can't be explained to a user"
