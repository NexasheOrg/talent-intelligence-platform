# ai-assistant

The "ask your data" service. Answers plain-English questions about the gold layer and **always
shows the SQL it used**. **Stack:** Python, FastAPI (an LLM API and a vector DB come later).

## What's here

```
assistant/
  guardrails.py   what may run against the database. READ THIS FIRST
  nl2sql.py       question -> SQL. Pattern matching today, an LLM later
  service.py      the FastAPI endpoints
tests/            guardrail and matcher tests - the most important tests in the repo
```

## Running it

```bash
python -m uvicorn assistant.service:app --app-dir ai-assistant --port 8100 --reload
```

Docs at <http://localhost:8100/docs>. It also runs as part of `docker compose up`.

```bash
curl -X POST localhost:8100/api/assistant/ask \
     -H 'content-type: application/json' \
     -d '{"question": "how many consultants are on the bench?"}'
```

```json
{"answer": "94 consultants are currently on the bench.",
 "sql": "SELECT count(*) AS value FROM fact_bench LIMIT 200", "ok": true}
```

Tests: `python -m pytest ai-assistant/tests`

## Why it isn't an LLM yet

It's a list of question shapes with SQL templates. That's deliberate: it runs with no API key,
no cost and no internet, so everyone can work on day one - and it's deterministic, so the
guardrails can actually be tested. Swapping in a model is task `AI-02`.

## Guardrails - the part that must not regress

This service turns untrusted text into database queries. That is a dangerous shape, and the
safety does not come from the model being sensible. It comes from `guardrails.py`, which every
query passes through before it reaches the database:

1. **Read-only.** One SELECT. No writes, no DDL, no second statement.
2. **Allow-listed tables.** The gold layer only - never a system table.
3. **Bounded.** Every query gets a LIMIT.

Plus: values from the question are always **parameters**, never pasted into the SQL string.

When you swap the matcher for an LLM, its output goes through exactly these checks. **An LLM is
a source of suggestions, never a source of permissions.** And keep the two behaviours the tests
pin down: the SQL is always returned to the user, and an unanswerable question says so instead
of inventing a number.

RAG over policy/SOW documents answers a different kind of question ("what's our notice-period
policy?") and is a later task - it gets its own guardrails, since documents are not the gold
layer.

## Next

Tasks `AI-01` … `AI-05` in [`../docs/TASKS.md`](../docs/TASKS.md).
