from __future__ import annotations

from pathlib import Path

import pandas as pd


def _load_interim_tables(interim_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    modem = pd.read_csv(interim_dir / "trn_modem_signal.csv")
    cmts = pd.read_csv(interim_dir / "trn_cmts_signal.csv")
    router = pd.read_csv(interim_dir / "trn_router_signal.csv")
    mtr = pd.read_csv(interim_dir / "trn_modem_mtr.csv")
    return modem, cmts, router, mtr


def _validate_required_ids(df: pd.DataFrame, table_name: str) -> None:
    required_ids = ["customer", "modem_mac", "router_mac"]
    missing = [col for col in required_ids if col not in df.columns]
    if missing:
        raise ValueError(f"{table_name} is missing required identifiers: {missing}")
    if df[required_ids].isna().any().any():
        raise ValueError(f"{table_name} contains null identifier values")


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    interim_dir = project_root / "data" / "interim"
    features_dir = project_root / "data" / "features"
    validation_dir = project_root / "example-pipeline-etl" / "outputs" / "validation"

    features_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)

    modem, cmts, router, mtr = _load_interim_tables(interim_dir)

    _validate_required_ids(modem, "trn_modem_signal.csv")
    _validate_required_ids(cmts, "trn_cmts_signal.csv")
    _validate_required_ids(router, "trn_router_signal.csv")
    _validate_required_ids(mtr, "trn_modem_mtr.csv")

    keys = ["customer", "modem_mac", "router_mac"]
    features = modem.merge(cmts, on=keys, how="inner")
    features = features.merge(router, on=keys, how="inner")
    features = features.merge(mtr, on=keys, how="inner")

    if len(features) != 1000:
        raise ValueError(f"Expected 1000 rows in unified features table, found {len(features)}")

    if features[keys].duplicated().any():
        raise ValueError("Unified features table has duplicate identifier rows")

    ordered_cols = keys + [
        "modem_rx",
        "modem_tx",
        "cmts_rx",
        "cmts_tx",
        "router_snr",
        "mtr",
    ]
    features = features[ordered_cols]

    out_features = features_dir / "features_unified.csv"
    features.to_csv(out_features, index=False)

    validation = pd.DataFrame(
        [
            {"metric": "rows_unified", "value": len(features)},
            {"metric": "unique_key_rows", "value": features[keys].drop_duplicates().shape[0]},
            {"metric": "nulls_in_keys", "value": int(features[keys].isna().sum().sum())},
        ]
    )
    out_validation = validation_dir / "stage3_join_validation.csv"
    validation.to_csv(out_validation, index=False)

    print(f"Wrote {len(features)} rows to {out_features}")
    print(f"Wrote validation summary to {out_validation}")


if __name__ == "__main__":
    main()
