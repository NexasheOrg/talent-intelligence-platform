---
id: ML-03
title: "ml: save the model and serve it over HTTP"
module: ml
labels: [ml]
difficulty: core
estimate: 2 days
depends_on: [ML-02]
---

## Why this matters

A model that only exists inside a training script isn't a product. This turns it into something
the API can call, which is the step that gets a real score in front of a user.

## What "done" looks like

- [ ] `train.py` saves the fitted model **and its preprocessing** to `ml/models/`
- [ ] A scoring service exposes `POST /score/attrition` taking a consultant id (or their
      features) and returning the same shape as `api/app/models.py: RiskScore`
- [ ] The response includes which model version produced it
- [ ] Feature building at scoring time uses **the same code** as training - `features.py`, not a
      reimplementation
- [ ] `/health` reports whether a model is loaded
- [ ] A missing model file gives a clear error, not a stack trace on every request
- [ ] Tests: a score comes back in range, an unknown consultant 404s, no model gives a clean error
- [ ] A Dockerfile, and the service added to `docker-compose.yml`

## Where to work

- `ml/src/train.py` - save the artefact
- `ml/service.py` - new, FastAPI on port 8200
- `ml/Dockerfile`, `docker-compose.yml`
- `ml/tests/`

## How to approach it

1. Copy the shape of `ai-assistant/` - it's the same idea: small FastAPI service, its own
   Dockerfile, its own tests.
2. **Match `RiskScore` exactly** (`risk_score`, `band`, `factors`, `model`). If the shape matches,
   ML-04 becomes a small change instead of a rewrite, and the web app doesn't change at all.
3. Save the scaler with the model. A model fed unscaled features returns confident nonsense - and
   this is the single most common bug in shipping a first model.
4. `factors` is not optional. A score with no explanation is a number nobody acts on. Feature
   importances or per-feature contributions both work.
5. Load the model **once at startup**, not per request.

## How to check it

```bash
python ml/src/train.py
python -m uvicorn service:app --app-dir ml --port 8200
python -m pytest ml/tests
```

Score a consultant you know is long-benched and one who's placed. If the scores don't differ in
the direction you'd expect, something is wired wrong.

## Gotchas

- Don't commit the model binary - `ml/models/` is git-ignored. CI or a build step regenerates it.
  Note in your PR how a deployment is meant to get one.
- scikit-learn pickles are version-sensitive. Record the version alongside the model, and fail
  loudly on mismatch rather than silently scoring wrong.
