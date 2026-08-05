---
id: ML-04
title: "ml + api: replace the heuristic with the trained model"
module: ml
labels: [ml, api]
difficulty: core
estimate: 1-2 days
depends_on: [ML-03]
---

## Why this matters

`api/app/risk.py` is a hand-written heuristic with weights someone guessed. It was always a
placeholder - the whole endpoint was designed so this swap would be easy. This is the task that
puts a real model in front of users.

## What "done" looks like

- [ ] `/api/consultants/{id}/risk` returns the trained model's score
- [ ] The `model` field changes from `baseline-heuristic-v0` to the real version, so anyone can
      tell which produced a number
- [ ] **The API degrades gracefully if the ML service is down** - falls back to the heuristic and
      says so in `model`, rather than 500-ing the consultants page
- [ ] A timeout on the call, so a slow model can't hang the API
- [ ] The existing risk tests still pass unchanged - they assert properties, not exact numbers
- [ ] `api/app/risk.py` keeps the heuristic as the documented fallback
- [ ] `docs/ARCHITECTURE.md` §3 updated

## Where to work

- `api/app/risk.py`, `api/app/routers/consultants.py`
- `api/app/config.py` - new, for the ML service URL
- `api/tests/`

## How to approach it

1. Read `api/tests/test_risk.py` first. Those tests assert bounds, ordering and explainability -
   they should pass with any scorer. If your change breaks one, ask whether the model is wrong
   before you change the test.
2. Put the call behind one function so there's a single place that knows the ML service exists.
3. **Fall back, don't fail.** An unreachable model should degrade the score's quality, not take
   the page down. Return the heuristic and mark it in `model` so it's visible, not silent.
4. Mock the ML service in tests. API tests must not need it running.

## How to check it

```bash
python -m pytest api/tests
```

Then run both, check a score in `/docs`, stop the ML service, and check the endpoint still
answers with the heuristic and the changed `model` field.

## Gotchas

- Talk to whoever owns the web layer. The number on screen will change, and the risk factors will
  read differently - they should see it coming.
- Don't call the model once per row in a list endpoint. That's 25 HTTP calls per page. Either
  batch it or keep risk on the detail endpoint only, and say which you chose.
