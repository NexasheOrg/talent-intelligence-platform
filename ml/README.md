# ml  ·  Owner: Eshwar

Predictive modeling on the gold layer.

- `notebooks/` — exploration, feature engineering, model comparison
- `src/` — training pipeline + a scoring service (`/score/attrition`)

**First model:** attrition-risk / bench-duration scoring per consultant. Compare a few
supervised models (logistic regression, tree ensembles), track metrics (precision/recall/F1),
ship the best behind an endpoint the API/web can call.
**Stack:** Python, scikit-learn, pandas · MLflow for tracking (roadmap).
