"""Guardrail tests.

These are the most important tests in the repo. The assistant turns untrusted text into
database queries; if these pass and the rest of the service is broken, the damage is a wrong
answer. If these fail, the damage is a dropped table.

Every new guardrail needs a test that proves it *blocks* something, not just that it lets good
queries through.
"""

import pytest
from assistant.guardrails import MAX_LIMIT, Unsafe, validate


def test_a_plain_select_is_allowed():
    assert validate("SELECT count(*) FROM fact_bench").lower().startswith("select")


def test_a_limit_is_always_applied():
    assert f"LIMIT {MAX_LIMIT}" in validate("SELECT * FROM dim_consultant")


def test_a_small_limit_is_left_alone():
    assert validate("SELECT * FROM dim_consultant LIMIT 5").endswith("LIMIT 5")


def test_an_oversized_limit_is_tightened():
    assert validate("SELECT * FROM dim_consultant LIMIT 99999").endswith(f"LIMIT {MAX_LIMIT}")


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE dim_consultant",
        "DELETE FROM fact_bench",
        "UPDATE dim_consultant SET cost_rate = 0",
        "INSERT INTO dim_client VALUES (1, 'x', 'y', 'z', '2020-01-01')",
        "TRUNCATE fact_timesheets",
        "ALTER TABLE dim_job ADD COLUMN x TEXT",
    ],
)
def test_anything_that_writes_is_refused(sql):
    with pytest.raises(Unsafe):
        validate(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; DROP TABLE dim_consultant",
        "SELECT * FROM dim_consultant; DELETE FROM fact_bench",
    ],
)
def test_a_second_statement_is_refused(sql):
    """The classic injection shape. One statement, always."""
    with pytest.raises(Unsafe):
        validate(sql)


def test_a_write_hidden_behind_a_comment_is_refused():
    with pytest.raises(Unsafe):
        validate("SELECT 1 -- harmless\n; DROP TABLE dim_consultant")


def test_a_table_outside_the_gold_layer_is_refused():
    with pytest.raises(Unsafe, match="not part of the gold layer"):
        validate("SELECT * FROM pg_shadow")


def test_a_system_table_join_is_refused():
    with pytest.raises(Unsafe):
        validate("SELECT * FROM dim_consultant JOIN sqlite_master ON 1=1")


def test_select_into_is_refused():
    """SELECT ... INTO writes a new table on some engines, so it isn't read-only."""
    with pytest.raises(Unsafe):
        validate("SELECT * INTO stolen FROM dim_consultant")


def test_an_empty_query_is_refused():
    with pytest.raises(Unsafe):
        validate("   ")
