#!/usr/bin/env python3
"""Train and evaluate the planned GuideStride Random Forest baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split

FEATURES = [
    "normalized_offset",
    "smoothed_offset",
    "offset_slope",
    "lane_confidence",
    "ax",
    "ay",
    "az",
    "gx",
    "gy",
    "gz",
]
TARGET = "label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.csv)

    required = FEATURES + [TARGET]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    clean = df[required].dropna().copy()
    X = clean[FEATURES]
    y = clean[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=y,
    )

    base = RandomForestClassifier(random_state=args.seed, class_weight="balanced")
    search = GridSearchCV(
        estimator=base,
        param_grid={
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 8, 16],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", 0.7],
        },
        scoring="f1_macro",
        cv=5,
        n_jobs=-1,
    )
    search.fit(X_train, y_train)

    predictions = search.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "best_cv_f1_macro": search.best_score_,
        "best_params": search.best_params_,
        "classification_report": classification_report(y_test, predictions, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=search.classes_).tolist(),
        "classes": search.classes_.tolist(),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(search.best_estimator_, output_dir / "random_forest.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps({"accuracy": metrics["accuracy"], "best_params": metrics["best_params"]}, indent=2))
    print(f"Saved model and metrics to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
