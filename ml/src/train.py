"""Train a bench-duration model and compare it against a baseline.

    pip install -r ml/requirements.txt
    python ml/src/train.py

What it does, and why in this order:

  1. Splits the data before doing anything else, so nothing about the test set can leak in.
  2. Scores a **baseline that isn't machine learning at all** - "predict the majority class".
     Any model that can't beat this has learned nothing, and reporting a model's accuracy
     without that comparison is how people ship useless models with confident numbers.
  3. Trains two models and reports precision / recall / F1, not just accuracy. On imbalanced
     data accuracy is a trap: if 80% of people come off the bench quickly, "always predict
     quickly" is 80% accurate and completely worthless.
  4. Saves the better one.

Your job when you extend this (task ML-02) is to keep step 2 honest. If the new model doesn't
beat the baseline, that's a finding worth reporting, not a failure to hide.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from features import FEATURE_NAMES, LONG_BENCH_DAYS, load_training_rows  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
RANDOM_STATE = 42  # fixed so two people training on the same data get the same numbers


def require_sklearn():
    try:
        import sklearn  # noqa: F401
    except ImportError:
        sys.exit(
            "scikit-learn isn't installed.\n"
            "From the repo root, with your virtual environment active:\n"
            "    pip install -r ml/requirements.txt"
        )


def evaluate(name, y_true, y_pred):
    from sklearn.metrics import precision_recall_fscore_support

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    accuracy = sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(y_true)
    print(
        f"  {name:<28} accuracy {accuracy:.2f}   precision {precision:.2f}   "
        f"recall {recall:.2f}   F1 {f1:.2f}"
    )
    return {"name": name, "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def main():
    require_sklearn()

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    X, y, _ = load_training_rows()
    if len(X) < 40:
        sys.exit(
            f"Only {len(X)} rows available - too few to train on.\n"
            "Generate a bigger seed:\n"
            "    python data/seed/generate_seed.py --consultants 2000\n"
            "    python data-platform/load_seed.py"
        )

    print(f"Predicting: still on the bench after {LONG_BENCH_DAYS} days")
    print(f"Rows: {len(X)}   positives: {sum(y)} ({100 * sum(y) / len(y):.0f}%)")
    print(f"Features: {', '.join(FEATURE_NAMES)}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y if len(set(y)) > 1 else None
    )

    print("Results on the held-out test set:")

    # The bar every model has to clear.
    majority = max(set(y_train), key=y_train.count)
    results = [evaluate("baseline (majority class)", y_test, [majority] * len(y_test))]

    scaler = StandardScaler().fit(X_train)
    logistic = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    logistic.fit(scaler.transform(X_train), y_train)
    results.append(
        evaluate("logistic regression", y_test, logistic.predict(scaler.transform(X_test)))
    )

    forest = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
    forest.fit(X_train, y_train)
    results.append(evaluate("random forest", y_test, forest.predict(X_test)))

    print("\nWhat the forest thinks matters:")
    for name, importance in sorted(
        zip(FEATURE_NAMES, forest.feature_importances_), key=lambda pair: -pair[1]
    ):
        print(f"  {name:<16} {importance:.3f}")

    best = max(results[1:], key=lambda r: r["f1"])
    baseline = results[0]

    print()
    if best["f1"] <= baseline["f1"]:
        print(
            f"No model beat the baseline (best F1 {best['f1']:.2f} vs {baseline['f1']:.2f}).\n"
            "That is a real result - report it rather than tuning until the number looks nice.\n"
            "The usual causes: not enough signal in these features, or too few rows."
        )
    else:
        print(f"Best model: {best['name']} (F1 {best['f1']:.2f} vs baseline {baseline['f1']:.2f})")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "metrics.json").write_text(json.dumps(results, indent=2))
    print(f"\nMetrics written to {MODEL_DIR / 'metrics.json'}")
    print("Saving the model itself and serving it is task ML-03.")


if __name__ == "__main__":
    main()
