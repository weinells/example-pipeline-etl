# ExamplePipeline Table Schemas

## src_customer_device_map.csv
- Stage: Raw source
- Source path: `data/raw/src_customer_device_map.csv`
- Summary: Source customer-to-device mapping table for the HFC network. It connects each customer to a modem and router identifier.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier assigned to the subscriber record. |
| modem_mac | string | Modem MAC address used to identify the cable modem. |
| router_mac | string | Router MAC address used to identify the customer gateway or router. |

## src_modem_signal.csv
- Stage: Raw source
- Source path: `data/raw/src_modem_signal.csv`
- Summary: Raw modem signal telemetry captured from the HFC access network.

| Column | Type | Description |
| --- | --- | --- |
| modem_mac | string | Modem MAC address that ties the telemetry back to a specific modem. |
| modem_rx | float | Modem receive signal level or power reading. |
| modem_tx | float | Modem transmit signal level or power reading. |

## src_cmts_signal.csv
- Stage: Raw source
- Source path: `data/raw/src_cmts_signal.csv`
- Summary: Raw CMTS-side signal telemetry for the cable access path.

| Column | Type | Description |
| --- | --- | --- |
| modem_mac | string | Modem MAC address used to align the cable modem to its CMTS readings. |
| cmts_rx | float | CMTS receive signal level for the modem path. |
| cmts_tx | float | CMTS transmit signal level for the modem path. |

## src_router_signal.csv
- Stage: Raw source
- Source path: `data/raw/src_router_signal.csv`
- Summary: Raw router-side signal telemetry associated with the customer gateway.

| Column | Type | Description |
| --- | --- | --- |
| router_mac | string | Router MAC address that identifies the gateway device. |
| router_snr | float | Router signal-to-noise ratio measurement. |

## src_modem_mtr.csv
- Stage: Raw source
- Source path: `data/raw/src_modem_mtr.csv`
- Summary: Raw Main Tap Ratio (MTR) telemetry table. In cable pre-equalization context, higher MTR indicates a cleaner primary path; this dataset is mostly 25-26 with a small low band at 17-18.

| Column | Type | Description |
| --- | --- | --- |
| modem_mac | string | Modem MAC address used to connect the reading to a specific modem. |
| mtr | float | Main Tap Ratio: relative dominance of the main equalizer tap versus non-main taps/reflections; higher values indicate cleaner upstream channel conditions. |

## trn_cmts_signal.csv
- Stage: Interim ETL
- Source path: `data/interim/trn_cmts_signal.csv`
- Summary: Join-ready CMTS telemetry enriched with customer and router identifiers.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier added during ETL join standardization. |
| modem_mac | string | Modem MAC address carried through the standardized join. |
| router_mac | string | Router MAC address carried through the standardized join. |
| cmts_rx | float | CMTS receive signal level. |
| cmts_tx | float | CMTS transmit signal level. |

## trn_modem_signal.csv
- Stage: Interim ETL
- Source path: `data/interim/trn_modem_signal.csv`
- Summary: Join-ready modem signal telemetry enriched with customer and router identifiers.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier added during ETL join standardization. |
| modem_mac | string | Modem MAC address carried through the standardized join. |
| router_mac | string | Router MAC address carried through the standardized join. |
| modem_rx | float | Modem receive signal level or power reading. |
| modem_tx | float | Modem transmit signal level or power reading. |

## trn_router_signal.csv
- Stage: Interim ETL
- Source path: `data/interim/trn_router_signal.csv`
- Summary: Join-ready router signal telemetry enriched with customer and modem identifiers.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier added during ETL join standardization. |
| modem_mac | string | Modem MAC address carried through the standardized join. |
| router_mac | string | Router MAC address carried through the standardized join. |
| router_snr | float | Router signal-to-noise ratio measurement. |

## trn_modem_mtr.csv
- Stage: Interim ETL
- Source path: `data/interim/trn_modem_mtr.csv`
- Summary: Join-ready modem telemetry reading enriched with customer and router identifiers.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier added during ETL join standardization. |
| modem_mac | string | Modem MAC address carried through the standardized join. |
| router_mac | string | Router MAC address carried through the standardized join. |
| mtr | float | Main Tap Ratio carried into the join-ready table; lower values indicate stronger non-main tap energy and likely echo/reflection impairment. |

## features_unified.csv
- Stage: Feature assembly
- Source path: `data/features/features_unified.csv`
- Summary: Unified modeling feature table formed by joining the four interim ETL outputs.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier for the unified feature row. |
| modem_mac | string | Modem MAC address for the unified feature row. |
| router_mac | string | Router MAC address for the unified feature row. |
| modem_rx | float | Modem receive signal level or power reading. |
| modem_tx | float | Modem transmit signal level or power reading. |
| cmts_rx | float | CMTS receive signal level. |
| cmts_tx | float | CMTS transmit signal level. |
| router_snr | float | Router signal-to-noise ratio measurement. |
| mtr | float | Main Tap Ratio feature; lower values correspond to poorer channel quality and increased impairment risk. |

## target_bad_service.csv
- Stage: Target engineering
- Source path: `data/targets/target_bad_service.csv`
- Summary: Synthetic binary target table indicating whether a customer is labeled for bad service.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier used to align the target with the feature table. |
| bad_service | integer | Binary label indicating whether the customer is flagged for bad service. |

## gtm_v1.csv
- Stage: Modeling dataset
- Source path: `data/gtm/gtm_v1.csv`
- Summary: Good-to-model training table that combines the unified features with the synthetic target.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier for the modeling row. |
| modem_mac | string | Modem MAC address for the modeling row. |
| router_mac | string | Router MAC address for the modeling row. |
| modem_rx | float | Modem receive signal level or power reading. |
| modem_tx | float | Modem transmit signal level or power reading. |
| cmts_rx | float | CMTS receive signal level. |
| cmts_tx | float | CMTS transmit signal level. |
| router_snr | float | Router signal-to-noise ratio measurement. |
| mtr | float | Main Tap Ratio used in model training; low values align with degradation scenarios in this dataset. |
| bad_service | integer | Binary target label used for model training and evaluation. |

## predictions_v1.csv
- Stage: Scoring output
- Source path: `data/scored/predictions_v1.csv`
- Summary: Inference output table containing the model predictions for bad service.

| Column | Type | Description |
| --- | --- | --- |
| customer | string | Customer identifier for the scored record. |
| modem_mac | string | Modem MAC address for the scored record. |
| router_mac | string | Router MAC address for the scored record. |
| predicted_bad_service | integer | Model prediction for the bad service flag. |
