---
id: ML-05
title: "ml: log experiments so runs can be compared"
module: ml
labels: [ml, stretch]
difficulty: stretch
estimate: 1-2 days
depends_on: [ML-02]
---

## Why this matters

Right now every training run overwrites `metrics.json`. Two people trying different features have
no way to compare, and nobody can answer "was last week's model better?". The roadmap wants
MLflow eventually; this is the small honest version of the same idea.

## What "done" looks like

- [ ] Every run appends a record: timestamp, git commit, model type, hyperparameters, feature
      list, and all metrics
- [ ] Runs are never overwritten
- [ ] A small command prints a comparison table of recent runs, best first
- [ ] The baseline is recorded on every run, so improvement is always measurable
- [ ] The log survives being written to by two runs (or the limitation is documented)
- [ ] Tests for reading and writing the log
- [ ] Documented in `ml/README.md`

## Where to work

- `ml/src/experiments.py` - new
- `ml/src/train.py` - record at the end of a run
- `ml/tests/`

## How to approach it

1. JSONL is the right format: append-only, one run per line, readable with any tool, no schema
   migration. Don't reach for a database.
2. **Record the git commit** (`git rev-parse --short HEAD`). Without it, "run 14 was best" is
   unactionable - you can't get back to the code that produced it.
3. Record the *inputs* as carefully as the outputs. A metric with no record of the features and
   parameters that produced it can't be reproduced, which makes it decoration.
4. Compare against the baseline every time, not against the previous best. Baselines move when
   the data changes.

## How to check it

```bash
python ml/src/train.py
python ml/src/train.py
python -m pytest ml/tests
```

Two runs, two lines in the log, and the comparison shows both.

## Gotchas

- If you decide to try MLflow instead of a file, that's a legitimate choice - but check the setup
  cost first. It's a service to run and it complicates the "clone and go" story for everyone
  else. If you add it, it must be optional.
- Don't log anything from the data itself, only metrics and configuration.
