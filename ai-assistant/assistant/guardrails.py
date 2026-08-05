"""Guardrails for any SQL this service is about to run.

Read this file before you touch anything else in the folder.

The assistant's whole job is turning untrusted text into database queries. That is a
**dangerous shape**, so the safety rule here is not "the model is careful" - it's that nothing
reaches the database without passing this file first. When the template matcher is replaced
with an LLM (task AI-02), the LLM's output goes through exactly these checks. An LLM is a
source of *suggestions*, never a source of *permissions*.

Three rules, all enforced here:
  1. Read-only. One SELECT, nothing else.
  2. Allow-listed tables. The gold layer only - never a system table, never anything else.
  3. Bounded. Every query gets a LIMIT so one question can't drag the database down.
"""

import re

# Only these tables. Adding one is a deliberate decision, made in a PR, not a config tweak.
ALLOWED_TABLES = {
    "dim_consultant", "dim_client", "dim_job",
    "fact_pipeline", "fact_placements", "fact_bench", "fact_timesheets",
}

MAX_LIMIT = 200

# Anything that writes, changes structure, or runs a second statement.
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|attach|detach|"
    r"copy|pragma|vacuum|replace|merge|call|execute|into)\b",
    re.IGNORECASE,
)

# Table names as they appear after FROM or JOIN.
TABLE_REFERENCE = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)


class Unsafe(Exception):
    """The SQL is not allowed to run. The message is safe to show a user."""


def _strip_comments(sql):
    """Comments can hide a second statement, so they're removed before anything is checked."""
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return sql


def validate(sql):
    """Raise `Unsafe` if this SQL must not run. Returns the cleaned, bounded SQL."""
    cleaned = _strip_comments(sql).strip().rstrip(";").strip()

    if not cleaned:
        raise Unsafe("Empty query.")

    # A second statement is the classic injection route: "SELECT 1; DROP TABLE x".
    if ";" in cleaned:
        raise Unsafe("Only one statement is allowed.")

    if not re.match(r"^\s*(select|with)\b", cleaned, re.IGNORECASE):
        raise Unsafe("Only SELECT queries are allowed - this service is read-only.")

    if FORBIDDEN.search(cleaned):
        raise Unsafe("That query would change data. This service can only read.")

    referenced = {match.lower() for match in TABLE_REFERENCE.findall(cleaned)}
    # Subqueries alias into FROM too; only flag names that aren't allow-listed tables.
    disallowed = referenced - ALLOWED_TABLES
    if disallowed:
        raise Unsafe(
            f"Query touches {', '.join(sorted(disallowed))}, which is not part of the gold layer."
        )

    return enforce_limit(cleaned)


def enforce_limit(sql, limit=MAX_LIMIT):
    """Add a LIMIT, or tighten one that's too generous."""
    existing = re.search(r"\blimit\s+(\d+)\s*$", sql, re.IGNORECASE)
    if existing:
        if int(existing.group(1)) <= limit:
            return sql
        return re.sub(r"\blimit\s+\d+\s*$", f"LIMIT {limit}", sql, flags=re.IGNORECASE)
    return f"{sql} LIMIT {limit}"
