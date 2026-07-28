# ExamplePipeline Table Schemas

## Customer Device Map (src_customer_device_map.csv)
- Stage: Raw source
- Source path: `data/raw/src_customer_device_map.csv`
- Summary: Source customer-to-device mapping table for the HFC network. It connects each customer to a modem and router identifier.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier assigned to the subscriber record. |
| modem_mac | string | Identifier | Modem MAC address used to identify the cable modem. |
| router_mac | string | Identifier | Router MAC address used to identify the customer gateway or router. |

### Data Summary
- Numeric profile: none

- Binary column counts: none

## Modem Signal Telemetry (src_modem_signal.csv)
- Stage: Raw source
- Source path: `data/raw/src_modem_signal.csv`
- Summary: Raw modem signal telemetry captured from the HFC access network.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| modem_mac | string | Identifier | Modem MAC address that ties the telemetry back to a specific modem. |
| modem_rx | float | Telemetry | Modem receive signal level or power reading. |
| modem_tx | float | Telemetry | Modem transmit signal level or power reading. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| modem_rx | -16.0225 | -3.4908 | 0.1255 | 3.5335 | 16.5582 | 6 |
| modem_tx | 23.9382 | 38.4952 | 42.7287 | 46.6691 | 59.7044 | 6 |

- Binary column counts: none

## CMTS Signal Telemetry (src_cmts_signal.csv)
- Stage: Raw source
- Source path: `data/raw/src_cmts_signal.csv`
- Summary: Raw CMTS-side signal telemetry for the cable access path.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| modem_mac | string | Identifier | Modem MAC address used to align the cable modem to its CMTS readings. |
| cmts_rx | float | Telemetry | CMTS receive signal level for the modem path. |
| cmts_tx | float | Telemetry | CMTS transmit signal level for the modem path. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cmts_rx | -2.0972 | -1.0224 | 0.0392 | 1.1043 | 2.0972 | 0 |
| cmts_tx | 39.6935 | 51.5660 | 55.0074 | 58.2977 | 70.5373 | 9 |

- Binary column counts: none

## Router Signal Telemetry (src_router_signal.csv)
- Stage: Raw source
- Source path: `data/raw/src_router_signal.csv`
- Summary: Raw router-side signal telemetry associated with the customer gateway.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| router_mac | string | Identifier | Router MAC address that identifies the gateway device. |
| router_snr | float | Telemetry | Router signal-to-noise ratio measurement. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| router_snr | -14.9961 | -7.6493 | -0.3977 | 7.8109 | 14.9761 | 0 |

- Binary column counts: none

## Modem Main Tap Ratio Telemetry (src_modem_mtr.csv)
- Stage: Raw source
- Source path: `data/raw/src_modem_mtr.csv`
- Summary: Raw Main Tap Ratio (MTR) telemetry table. In cable pre-equalization context, higher MTR indicates a cleaner primary path; this dataset is mostly 25-26 with a small low band at 17-18.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| modem_mac | string | Identifier | Modem MAC address used to connect the reading to a specific modem. |
| mtr | float | Telemetry | Main Tap Ratio: relative dominance of the main equalizer tap versus non-main taps/reflections; higher values indicate cleaner upstream channel conditions. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mtr | 17.1410 | 25.2353 | 25.5052 | 25.7680 | 25.9991 | 10 |

- Binary column counts: none

## Transformed CMTS Signal (trn_cmts_signal.csv)
- Stage: Interim ETL
- Source path: `data/interim/trn_cmts_signal.csv`
- Summary: Join-ready CMTS telemetry enriched with customer and router identifiers.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier added during ETL join standardization. |
| modem_mac | string | Identifier | Modem MAC address carried through the standardized join. |
| router_mac | string | Identifier | Router MAC address carried through the standardized join. |
| cmts_rx | float | Telemetry | CMTS receive signal level. |
| cmts_tx | float | Telemetry | CMTS transmit signal level. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cmts_rx | -2.0972 | -1.0224 | 0.0392 | 1.1043 | 2.0972 | 0 |
| cmts_tx | 39.6935 | 51.5660 | 55.0074 | 58.2977 | 70.5373 | 9 |

- Binary column counts: none

## Transformed Modem Signal (trn_modem_signal.csv)
- Stage: Interim ETL
- Source path: `data/interim/trn_modem_signal.csv`
- Summary: Join-ready modem signal telemetry enriched with customer and router identifiers.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier added during ETL join standardization. |
| modem_mac | string | Identifier | Modem MAC address carried through the standardized join. |
| router_mac | string | Identifier | Router MAC address carried through the standardized join. |
| modem_rx | float | Telemetry | Modem receive signal level or power reading. |
| modem_tx | float | Telemetry | Modem transmit signal level or power reading. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| modem_rx | -16.0225 | -3.4908 | 0.1255 | 3.5335 | 16.5582 | 6 |
| modem_tx | 23.9382 | 38.4952 | 42.7287 | 46.6691 | 59.7044 | 6 |

- Binary column counts: none

## Transformed Router Signal (trn_router_signal.csv)
- Stage: Interim ETL
- Source path: `data/interim/trn_router_signal.csv`
- Summary: Join-ready router signal telemetry enriched with customer and modem identifiers.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier added during ETL join standardization. |
| modem_mac | string | Identifier | Modem MAC address carried through the standardized join. |
| router_mac | string | Identifier | Router MAC address carried through the standardized join. |
| router_snr | float | Telemetry | Router signal-to-noise ratio measurement. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| router_snr | -14.9961 | -7.6493 | -0.3977 | 7.8109 | 14.9761 | 0 |

- Binary column counts: none

## Transformed Modem MTR (trn_modem_mtr.csv)
- Stage: Interim ETL
- Source path: `data/interim/trn_modem_mtr.csv`
- Summary: Join-ready modem telemetry reading enriched with customer and router identifiers.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier added during ETL join standardization. |
| modem_mac | string | Identifier | Modem MAC address carried through the standardized join. |
| router_mac | string | Identifier | Router MAC address carried through the standardized join. |
| mtr | float | Telemetry | Main Tap Ratio carried into the join-ready table; lower values indicate stronger non-main tap energy and likely echo/reflection impairment. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mtr | 17.1410 | 25.2353 | 25.5052 | 25.7680 | 25.9991 | 10 |

- Binary column counts: none

## Unified Network Features (features_unified.csv)
- Stage: Feature assembly
- Source path: `data/features/features_unified.csv`
- Summary: Unified modeling feature table formed by joining the four interim ETL outputs.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier for the unified feature row. |
| modem_mac | string | Identifier | Modem MAC address for the customer-side cable modem endpoint. |
| router_mac | string | Identifier | Router MAC address for the customer gateway endpoint. |
| modem_rx | float | Telemetry | Modem receive power-level telemetry from the access path. |
| modem_tx | float | Telemetry | Modem transmit power-level telemetry from the access path. |
| cmts_rx | float | Telemetry | CMTS-side receive level telemetry for the same modem path. |
| cmts_tx | float | Telemetry | CMTS-side transmit level telemetry for the same modem path. |
| router_snr | float | Telemetry | Router-side signal-to-noise ratio telemetry from gateway measurements. |
| mtr | float | Telemetry | Main Tap Ratio feature where lower values indicate stronger reflected/non-main tap energy. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| modem_rx | -16.0225 | -3.4908 | 0.1255 | 3.5335 | 16.5582 | 6 |
| modem_tx | 23.9382 | 38.4952 | 42.7287 | 46.6691 | 59.7044 | 6 |
| cmts_rx | -2.0972 | -1.0224 | 0.0392 | 1.1043 | 2.0972 | 0 |
| cmts_tx | 39.6935 | 51.5660 | 55.0074 | 58.2977 | 70.5373 | 9 |
| router_snr | -14.9961 | -7.6493 | -0.3977 | 7.8109 | 14.9761 | 0 |
| mtr | 17.1410 | 25.2353 | 25.5052 | 25.7680 | 25.9991 | 10 |

- Binary column counts: none

## Bad Service Target Labels (target_bad_service.csv)
- Stage: Target engineering
- Source path: `data/targets/target_bad_service.csv`
- Summary: Synthetic binary target table indicating whether a customer is labeled for bad service.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier used to align the target with the feature table. |
| bad_service | integer | Label | Binary label indicating whether the customer is flagged for bad service. |

### Data Summary
- Numeric profile: none

- Binary column counts:
  - `bad_service`: 0=845, 1=155

## Good to Model Dataset (Version 1) (gtm_v1.csv)
- Stage: Modeling dataset
- Source path: `data/gtm/gtm_v1.csv`
- Summary: Good-to-model training table that combines the unified features with the synthetic target.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier for the modeling row. |
| modem_mac | string | Identifier | Modem MAC address for the modeling row. |
| router_mac | string | Identifier | Router MAC address for the modeling row. |
| modem_rx | float | Telemetry | Modem receive signal level or power reading. |
| modem_tx | float | Telemetry | Modem transmit signal level or power reading. |
| cmts_rx | float | Telemetry | CMTS receive signal level. |
| cmts_tx | float | Telemetry | CMTS transmit signal level. |
| router_snr | float | Telemetry | Router signal-to-noise ratio measurement. |
| mtr | float | Telemetry | Main Tap Ratio used in model training; low values align with degradation scenarios in this dataset. |
| bad_service | integer | Label | Binary target label used for model training and evaluation. |

### Data Summary
- Numeric profile:

| Column | Min | Q1 | Median | Q3 | Max | Outliers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| modem_rx | -16.0225 | -3.4908 | 0.1255 | 3.5335 | 16.5582 | 6 |
| modem_tx | 23.9382 | 38.4952 | 42.7287 | 46.6691 | 59.7044 | 6 |
| cmts_rx | -2.0972 | -1.0224 | 0.0392 | 1.1043 | 2.0972 | 0 |
| cmts_tx | 39.6935 | 51.5660 | 55.0074 | 58.2977 | 70.5373 | 9 |
| router_snr | -14.9961 | -7.6493 | -0.3977 | 7.8109 | 14.9761 | 0 |
| mtr | 17.1410 | 25.2353 | 25.5052 | 25.7680 | 25.9991 | 10 |

- Binary column counts:
  - `bad_service`: 0=845, 1=155

## Bad Service Predictions (Version 1) (predictions_v1.csv)
- Stage: Scoring output
- Source path: `data/scored/predictions_v1.csv`
- Summary: Inference output table containing the model predictions for bad service.
- Row count: 1000

| Column | Type | Role | Description |
| --- | --- | --- | --- |
| customer | string | Identifier | Customer identifier for the scored record. |
| modem_mac | string | Identifier | Modem MAC address for the scored record. |
| router_mac | string | Identifier | Router MAC address for the scored record. |
| predicted_bad_service | integer | Label | Model prediction for the bad service flag. |

### Data Summary
- Numeric profile: none

- Binary column counts:
  - `predicted_bad_service`: 0=854, 1=146
