---
id: ML-02
title: "ml: train an attrition model that beats the baseline"
module: ml
labels: [ml]
difficulty: core
estimate: 2-3 days
depends_on: [ML-01]
---

## Why this matters

Once the seed data records who left (ML-01), attrition becomes a real prediction problem. The
API's current "risk score" is a heuristic someone wrote by hand - this is what replaces it, if
and only if it actually does better.

## What "done" looks like

- [ ] Features built from the gold layer, in `features.py`, for the attrition target
- [ ] At least two model types compared, **both against the majority-class baseline**
- [ ] Precision, recall and F1 reported - not accuracy alone
- [ ] A short write-up in the PR: what you tried, what won, and by how much over the baseline
- [ ] Feature importances reported, with a sentence on whether they're plausible
- [ ] Deterministic: fixed random seed, so someone else gets your numbers
- [ ] Tests for the feature builder (shape, no nulls, label balance is sane)

## Where to work

- `ml/src/features.py`, `ml/src/train.py`
- `ml/tests/` - new

## How to approach it

1. Look at the data before modelling. What fraction left? Does the rate rise with bench time?
   Five minutes of counting saves a day of modelling the wrong thing.
2. **Watch for leakage.** If a feature encodes the answer - `status == 'left'`, or anything
   recorded *because* someone left - you'll get a near-perfect score and a useless model. A
   suspiciously high score is a bug report, not a result.
3. Split before you do anything else, including scaling. Fit the scaler on train only.
4. Decide which error costs more and say so. Missing someone about to leave, or wasting a
   manager's time on a false alarm? That choice is precision vs recall, and it's a product
   decision you should state rather than let the default pick for you.

## How to check it

```bash
python data-platform/load_seed.py
python ml/src/train.py
python -m pytest ml/tests
```

Run it twice. Identical numbers, or your seed isn't fixed.

## Gotchas

- **If nothing beats the baseline, report that.** It's a real finding, and the honest version of
  this task. Tuning until the number looks good is how useless models get shipped.
- This is synthetic data built to be learnable. A good score here says the pipeline works, not
  that the model predicts real attrition. Say so explicitly in the PR - overclaiming is the thing
  that will actually get you in trouble later.
