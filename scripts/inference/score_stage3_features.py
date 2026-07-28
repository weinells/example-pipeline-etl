from __future__ import annotations

import json
from pathlib import Path

import mlflow
import mlflow.pyfunc
import pandas as pd


FEATURE_COLUMNS = [
    "modem_rx",
    "modem_tx",
    "cmts_rx",
    "cmts_tx",
    "router_snr",
    "mtr",
]


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]

    features_path = project_root / "data" / "features" / "features_unified.csv"
    model_ref_path = project_root / "repo" / "models" / "best_model_reference.json"
    scored_dir = project_root / "data" / "scored"
    scored_dir.mkdir(parents=True, exist_ok=True)

    features = pd.read_csv(features_path)

    with model_ref_path.open("r", encoding="utf-8") as f:
        model_ref = json.load(f)

    tracking_uri = model_ref["tracking_uri"]
    model_uri = model_ref["best_model_uri"]

    mlflow.set_tracking_uri(tracking_uri)
    model = mlflow.pyfunc.load_model(model_uri)

    X = features[FEATURE_COLUMNS]
    predictions = model.predict(X)

    scored = features[["customer", "modem_mac", "router_mac"]].copy()
    scored["predicted_bad_service"] = pd.Series(predictions).astype(int)

    out_path = scored_dir / "predictions_v1.csv"
    scored.to_csv(out_path, index=False)

    positive_count = int(scored["predicted_bad_service"].sum())
    print(f"Wrote {len(scored)} rows to {out_path}")
    print(f"Predicted positives: {positive_count}")


if __name__ == "__main__":
    main()
