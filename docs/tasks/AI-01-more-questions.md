---
id: AI-01
title: "ai-assistant: teach it four more questions"
module: ai-assistant
labels: [ai-assistant, good-first-issue]
difficulty: warm-up
estimate: half a day
depends_on: []
---

## Why this matters

The assistant answers seven questions today. Every extra one it handles is a question somebody
doesn't have to ask an analyst. It's also the quickest way to learn the guardrail pattern before
you go near an LLM.

## What "done" looks like

- [ ] Four new question shapes answered
- [ ] Each has a test asserting the right intent matches
- [ ] Each generated query passes `guardrails.validate` (there's already a test that checks all
      of them at once - it must still pass)
- [ ] `examples()` lists the new questions, so the refusal message stays useful
- [ ] Values from the question are **parameters**, never pasted into the SQL

## Where to work

- `ai-assistant/assistant/nl2sql.py`
- `ai-assistant/tests/test_nl2sql.py`

## Ideas (pick four)

- "How many consultants are in Hyderabad?" (any location)
- "How many open jobs do we have?"
- "Which skills are most common on the bench?"
- "What's our total margin?"
- "How many placements started this month?"
- "Which clients are in healthcare?" (any industry)

## How to approach it

1. Read one existing `intent(...)` block. Yours is the same shape: a name, some regexes, SQL, an
   answer template, and optionally a function that pulls parameters out of the match.
2. **Order matters.** The first pattern that matches wins, so a broad regex placed early will
   swallow later ones. Test the questions you *didn't* intend to match too.
3. Keep any character class for a user-supplied value narrow, like `consultants_with_skill` does.
   A value containing a quote should fail to match and be refused, not reach the database.
4. Portable SQL - Postgres and SQLite.

## How to check it

```bash
python -m pytest ai-assistant/tests
python -m uvicorn assistant.service:app --app-dir ai-assistant --port 8100
```

Then try your questions in `/docs`, and try some near-misses - "how many consultants in
Atlantis?" should return `ok: false`, not a crash and not a made-up number.

## Gotchas

- If a question can't be answered, saying so is the correct behaviour. Never widen a regex until
  it matches something vaguely related - a confident wrong answer is the worst output this
  service can produce.
