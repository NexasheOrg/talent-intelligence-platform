# ml

Predictive modelling on the gold layer. **Stack:** Python, scikit-learn · MLflow for tracking
(roadmap).

## What's here

```
src/features.py   builds the feature table from gold. Stdlib only, so you can inspect the
                  features without installing anything
src/train.py      trains and compares models against a baseline, prints metrics
models/           output: metrics.json (git-ignored)
notebooks/        exploration, feature engineering, model comparison
```

## Running it

```bash
pip install -r ml/requirements.txt      # scikit-learn; not installed by the run scripts
python ml/src/features.py               # look at the features first
python ml/src/train.py
```

It needs a loaded gold layer: `python data-platform/load_seed.py`.

## What it predicts today

**Will this benched consultant still be on the bench after 45 days?** Long bench time is the
biggest margin leak in a staffing business, and unlike attrition it has a label the seed data
actually contains.

Attrition risk - what the roadmap ultimately wants - has **no ground truth in the seed data**.
You cannot train a model to predict something the data never records. So the first real task
here (`ML-01`) is adding a realistic attrition signal to the seed generator; `ML-02` is training
on it and replacing the heuristic that currently backs `api/app/risk.py`.

## The rule that matters here

**Always report against a baseline.** `train.py` scores "predict the majority class" before it
scores anything else, because on imbalanced data a model can look 80% accurate and be worthless.
If your model doesn't beat the baseline, that is a **result to report**, not a number to tune
away. Right now the random forest beats it by a hair (F1 0.88 vs 0.86) - which mostly means
these five features don't carry much signal yet. Better features are the interesting work.

Report precision and recall, not accuracy alone, and say which you optimised for. "Catch every
at-risk consultant" and "don't waste a manager's time on false alarms" are different products.

## Next

Tasks `ML-01` … `ML-05` in [`../docs/TASKS.md`](../docs/TASKS.md).
