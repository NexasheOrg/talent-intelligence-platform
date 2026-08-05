---
id: AI-03
title: "ai-assistant: log what people actually ask"
module: ai-assistant
labels: [ai-assistant]
difficulty: core
estimate: 1 day
depends_on: []
---

## Why this matters

We're guessing at which questions matter. A log of what people actually typed - and which ones
we failed to answer - turns that guess into a list. The unanswered questions are the roadmap for
this service.

## What "done" looks like

- [ ] Every request records: the question, the matched intent (or none), the SQL, whether it
      succeeded, and how long it took
- [ ] `GET /api/assistant/unanswered` returns the questions we couldn't answer, most frequent first
- [ ] Logging failing **never** breaks the answer - a broken log is not a broken product
- [ ] Tests: a successful question is logged, a refused one is logged as unanswered, and a
      failing logger doesn't take down the endpoint
- [ ] Documented in the README

## Where to work

- `ai-assistant/assistant/log.py` - new
- `ai-assistant/assistant/service.py`
- `ai-assistant/tests/test_log.py` - new

## How to approach it

1. Decide where it goes. A table in the database is the obvious answer - but note that the
   assistant's connection is deliberately **read-only**, so writing needs a second connection
   with a clearly separate purpose. A JSONL file is a perfectly reasonable first version; say
   which you chose and why.
2. Wrap the logging call so an exception can't escape. `try/except` around it, and carry on.
3. For `/unanswered`, group by the question text, normalised (lowercased, trimmed).

## How to check it

```bash
python -m pytest ai-assistant/tests
```

Ask five questions, two of them nonsense, then check `/api/assistant/unanswered` lists the two.

## Gotchas

- **Don't log anything sensitive.** Questions are user input and could contain names. Since this
  runs on synthetic data it's low risk today, but write it as though it weren't - if this ever
  points at real data, this log becomes a liability nobody remembered to check.
- Don't let the log become a write path into the gold layer. Keep it separate from the data the
  assistant reads.
