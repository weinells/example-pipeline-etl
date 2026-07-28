from __future__ import annotations

import json
import shutil
from pathlib import Path

import mlflow
import mlflow.artifacts
import mlflow.pyfunc
import mlflow.sklearn
import mlflow.xgboost
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier


def build_datasets(project_root: Path) -> pd.DataFrame:
    features = pd.read_csv(project_root / "data" / "features" / "features_unified.csv")
    target = pd.read_csv(project_root / "data" / "targets" / "target_bad_service.csv")

    gtm = features.merge(target, on="customer", how="inner")
    if len(gtm) != 1000:
        raise ValueError(f"Expected 1000 rows in GTM data, found {len(gtm)}")

    gtm_out = project_root / "data" / "gtm"
    gtm_out.mkdir(parents=True, exist_ok=True)
    gtm_path = gtm_out / "gtm_v1.csv"
    gtm.to_csv(gtm_path, index=False)
    print(f"Wrote GTM dataset to {gtm_path}")

    return gtm


def get_model_specs() -> dict[str, object]:
    return {
        "svm": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", SVC(kernel="rbf", C=1.0, gamma="scale", probability=False, random_state=42)),
            ]
        ),
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, random_state=42)),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=4,
        ),
    }


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    outputs_root = project_root / "repo" / "outputs"
    metrics_dir = outputs_root / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    mlruns_dir = outputs_root / "mlruns"
    mlruns_dir.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(mlruns_dir.as_uri())
    mlflow.set_experiment("ExamplePipeline-Stage5")

    gtm = build_datasets(project_root)

    feature_cols = [
        "modem_rx",
        "modem_tx",
        "cmts_rx",
        "cmts_tx",
        "router_snr",
        "mtr",
    ]
    X = gtm[feature_cols]
    y = gtm["bad_service"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    models = get_model_specs()

    results: list[dict[str, float | str]] = []

    for name, model in models.items():
        with mlflow.start_run(run_name=f"stage5_{name}") as run:
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="precision")

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            test_precision = precision_score(y_test, y_pred, zero_division=0)
            test_recall = recall_score(y_test, y_pred, zero_division=0)
            test_f1 = f1_score(y_test, y_pred, zero_division=0)
            test_accuracy = accuracy_score(y_test, y_pred)

            mlflow.log_param("model_name", name)
            mlflow.log_param("cv_folds", 4)
            mlflow.log_param("stratified_split", True)
            mlflow.log_metric("cv_precision_mean", float(cv_scores.mean()))
            mlflow.log_metric("cv_precision_std", float(cv_scores.std()))
            mlflow.log_metric("test_precision", float(test_precision))
            mlflow.log_metric("test_recall", float(test_recall))
            mlflow.log_metric("test_f1", float(test_f1))
            mlflow.log_metric("test_accuracy", float(test_accuracy))

            if name == "xgboost":
                mlflow.xgboost.log_model(model, artifact_path="model")
            else:
                mlflow.sklearn.log_model(model, artifact_path="model")

            results.append(
                {
                    "model": name,
                    "cv_precision_mean": float(cv_scores.mean()),
                    "cv_precision_std": float(cv_scores.std()),
                    "test_precision": float(test_precision),
                    "test_recall": float(test_recall),
                    "test_f1": float(test_f1),
                    "test_accuracy": float(test_accuracy),
                    "run_id": run.info.run_id,
                }
            )

    results_df = pd.DataFrame(results).sort_values("test_precision", ascending=False).reset_index(drop=True)
    metrics_path = metrics_dir / "stage5_model_comparison.csv"
    results_df.to_csv(metrics_path, index=False)

    best = results_df.iloc[0].to_dict()
    best_model_name = str(best["model"])
    best_run_id = str(best["run_id"])

    best_uri = f"runs:/{best_run_id}/model"
    model_dir = project_root / "repo" / "models" / "best_model_mlflow"
    if model_dir.exists():
        shutil.rmtree(model_dir)
    model_dir.parent.mkdir(parents=True, exist_ok=True)
    downloaded_path = Path(
        mlflow.artifacts.download_artifacts(artifact_uri=best_uri, dst_path=str(model_dir.parent))
    )
    if downloaded_path.resolve() != model_dir.resolve():
        if model_dir.exists():
            shutil.rmtree(model_dir)
        shutil.move(str(downloaded_path), str(model_dir))

    # Save a portable reference to the best run and model URI for Stage 6 inference ETL.
    best_ref = {
        "best_model_name": best_model_name,
        "selection_metric": "test_precision",
        "best_test_precision": float(best["test_precision"]),
        "best_run_id": best_run_id,
        "best_model_uri": best_uri,
        "tracking_uri": mlruns_dir.as_uri(),
    }
    best_ref_path = project_root / "repo" / "models" / "best_model_reference.json"
    best_ref_path.parent.mkdir(parents=True, exist_ok=True)
    best_ref_path.write_text(json.dumps(best_ref, indent=2), encoding="utf-8")

    print(f"Wrote model comparison metrics to {metrics_path}")
    print(f"Best model by precision: {best_model_name} ({best['test_precision']:.4f})")
    print(f"Best model reference saved to {best_ref_path}")
    print(f"Best model artifacts downloaded under {model_dir.parent}")


if __name__ == "__main__":
    main()
