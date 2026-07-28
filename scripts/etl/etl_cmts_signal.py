from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    raw_dir = project_root / "data" / "raw"
    interim_dir = project_root / "data" / "interim"
    interim_dir.mkdir(parents=True, exist_ok=True)

    device_map = pd.read_csv(raw_dir / "src_customer_device_map.csv")
    cmts_signal = pd.read_csv(raw_dir / "src_cmts_signal.csv")

    transformed = cmts_signal.merge(device_map, on="modem_mac", how="inner")
    transformed = transformed[["customer", "modem_mac", "router_mac", "cmts_rx", "cmts_tx"]]

    if len(transformed) != 1000:
        raise ValueError(f"Expected 1000 transformed rows, found {len(transformed)}")

    if transformed[["customer", "modem_mac", "router_mac"]].isna().any().any():
        raise ValueError("Identifier columns contain null values")

    out_path = interim_dir / "trn_cmts_signal.csv"
    transformed.to_csv(out_path, index=False)
    print(f"Wrote {len(transformed)} rows to {out_path}")


if __name__ == "__main__":
    main()
