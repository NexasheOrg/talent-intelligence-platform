"""Turn a plain-English question into SQL over the gold layer.

Today this is **pattern matching, not a language model** - a list of question shapes, each with
a SQL template. That is on purpose:

  * it runs with no API key, no cost, and no internet, so everyone can work on day one
  * it's deterministic, so it can be tested properly
  * it forces the interesting part - the guardrails, the "show me the SQL" contract, the
    handling of questions we can't answer - to be built and reviewed before a model is involved

Replacing the matcher with an LLM is task AI-02. When you do, keep three things:
  1. every generated query still goes through `guardrails.validate`
  2. the SQL is still returned to the user alongside the answer
  3. an unanswerable question still says so instead of inventing a number

Values from the question are passed as **parameters**, never pasted into the SQL string.
"""

import re

INTENTS = []


def intent(name, patterns, sql, answer, params=None):
    """Register a question shape.

    Args:
        name: identifier, handy in tests and logs.
        patterns: regexes; the first to match wins. Named groups become template values.
        sql: the query to run, with `?` placeholders.
        answer: format string rendered with the query result.
        params: builds the parameter list from the regex match. Default: no parameters.
    """
    INTENTS.append({
        "name": name,
        "patterns": [re.compile(p, re.IGNORECASE) for p in patterns],
        "sql": sql,
        "answer": answer,
        "params": params or (lambda match: []),
    })


intent(
    "bench_count",
    [r"how many.*\b(on the bench|benched|bench)\b", r"\bbench (count|size|headcount)\b"],
    "SELECT count(*) AS value FROM fact_bench",
    "{value} consultants are currently on the bench.",
)

intent(
    "utilization",
    [r"\b(what|how).*\butili[sz]ation\b", r"\butili[sz]ation\b.*\?"],
    """
    SELECT ROUND(
        100.0 * SUM(hours_billable) / (SUM(hours_billable) + SUM(hours_bench)), 1
    ) AS value
    FROM fact_timesheets
    """,
    "Utilization is {value}%.",
)

intent(
    "headcount",
    [r"how many consultants(?!.*\b(bench|skill|know)\b)", r"\b(total )?headcount\b"],
    "SELECT count(*) AS value FROM dim_consultant",
    "There are {value} consultants.",
)

intent(
    "consultants_with_skill",
    # The character class is deliberately narrow - letters, digits and the few punctuation
    # marks real skill names use ("C++", "Node.js"). Anything with a quote or a semicolon
    # fails to match and the question is refused, which is the behaviour we want.
    [r"how many.*\b(know|have|with|skilled in)\b\s+(?P<skill>[A-Za-z0-9+#. ]{2,30})\??$"],
    "SELECT count(*) AS value FROM dim_consultant WHERE LOWER(skills) LIKE ?",
    "{value} consultants list that skill.",
    params=lambda match: [f"%{match.group('skill').strip().lower()}%"],
)

intent(
    "pipeline_stage_count",
    [r"how many.*\b(candidates|people)\b.*\b(at|in)\b\s+"
     r"(?P<stage>submitted|interview|offer|placed|rejected)"],
    "SELECT count(*) AS value FROM fact_pipeline WHERE stage = ?",
    "{value} candidates are at that stage.",
    params=lambda match: [match.group("stage").lower()],
)

intent(
    "top_clients_by_placements",
    [r"\b(which|what|top).*clients?\b.*\b(most|top)\b.*\bplacements?\b",
     r"\btop clients?\b"],
    """
    SELECT c.name AS client, count(*) AS placements
    FROM fact_placements p
    JOIN dim_client c ON c.client_id = p.client_id
    GROUP BY c.name
    ORDER BY placements DESC
    LIMIT 5
    """,
    "Top clients by placements.",
)

intent(
    "longest_bench",
    # Both word orders: "longest on the bench" and "on the bench longest".
    [r"\blongest\b.*\bbench\b",
     r"\bbench\b.*\b(longest|the most days)\b"],
    """
    SELECT c.name AS consultant, b.days_on_bench AS days
    FROM fact_bench b
    JOIN dim_consultant c ON c.consultant_id = b.consultant_id
    ORDER BY b.days_on_bench DESC
    LIMIT 10
    """,
    "The consultants who have been on the bench longest.",
)

intent(
    "average_margin",
    [r"\b(average|avg|mean)\b.*\bmargin\b"],
    "SELECT ROUND(AVG(margin), 2) AS value FROM fact_placements",
    "The average margin per placement is ${value} per hour.",
)


class CannotAnswer(Exception):
    """No intent matched. The message tells the user what *can* be asked."""


def examples():
    return [
        "How many consultants are on the bench?",
        "What is our utilization?",
        "How many consultants know Python?",
        "How many candidates are at interview?",
        "Which clients have the most placements?",
        "Who has been on the bench longest?",
        "What is the average margin?",
    ]


def translate(question):
    """Return (sql, params, answer_template, intent_name), or raise CannotAnswer."""
    text = (question or "").strip()
    if not text:
        raise CannotAnswer("Ask a question first.")

    for entry in INTENTS:
        for pattern in entry["patterns"]:
            match = pattern.search(text)
            if match:
                return (
                    " ".join(entry["sql"].split()),
                    entry["params"](match),
                    entry["answer"],
                    entry["name"],
                )

    raise CannotAnswer(
        "I don't know how to answer that yet. Things I can answer:\n  - "
        + "\n  - ".join(examples())
    )
