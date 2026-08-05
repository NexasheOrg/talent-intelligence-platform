"""Tests for the question matcher.

Two rules a question-answering service must obey, both pinned here:
  - it answers what it can
  - it says so plainly when it can't, instead of guessing

The second is the one that matters. A confident wrong answer is the worst thing this service
could produce, and it's exactly what a language model will do by default when you swap the
matcher out (task AI-02). These tests should still pass afterwards.
"""

import pytest

from assistant.guardrails import validate
from assistant.nl2sql import CannotAnswer, translate


@pytest.mark.parametrize(
    "question,expected_intent",
    [
        ("How many consultants are on the bench?", "bench_count"),
        ("what is our utilization?", "utilization"),
        ("How many consultants are there?", "headcount"),
        ("How many consultants know Python?", "consultants_with_skill"),
        ("How many candidates are at interview?", "pipeline_stage_count"),
        ("Which clients have the most placements?", "top_clients_by_placements"),
        ("Who has been on the bench longest?", "longest_bench"),
        ("What is the average margin?", "average_margin"),
    ],
)
def test_known_questions_match_the_right_intent(question, expected_intent):
    _, _, _, intent = translate(question)
    assert intent == expected_intent


def test_every_generated_query_passes_the_guardrails():
    """If the matcher can produce SQL the guardrails reject, that's a bug in the matcher."""
    questions = [
        "How many consultants are on the bench?",
        "what is our utilization?",
        "How many consultants know Python?",
        "How many candidates are at offer?",
        "Which clients have the most placements?",
        "Who has been on the bench longest?",
        "What is the average margin?",
    ]
    for question in questions:
        sql, _, _, _ = translate(question)
        validate(sql)


def test_a_value_from_the_question_becomes_a_parameter_not_string_concatenation():
    """The skill the user typed must never end up pasted into the SQL text."""
    sql, params, _, _ = translate("How many consultants know Python?")
    assert "python" not in sql.lower()
    assert params == ["%python%"]


def test_an_injection_attempt_in_a_value_is_refused_outright():
    """Defence in depth, layer one.

    The skill pattern only accepts characters real skill names use, so a value carrying a quote
    or a semicolon never matches an intent at all - the question is refused before any SQL is
    generated. The guardrails and the parameter binding are layers two and three.
    """
    with pytest.raises(CannotAnswer):
        translate("How many consultants know x'; DROP TABLE dim_consultant--?")


def test_an_unknown_question_is_refused_not_guessed():
    with pytest.raises(CannotAnswer) as refusal:
        translate("what will our revenue be next quarter?")
    # The refusal has to be useful, so it lists what can be asked.
    assert "How many consultants are on the bench?" in str(refusal.value)


def test_an_empty_question_is_refused():
    with pytest.raises(CannotAnswer):
        translate("   ")
