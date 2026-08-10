# ExamplePipeline Human-Readable Ontology

## Purpose

This ontology defines the business and technical meaning of the synthetic cable-internet telemetry data in ExamplePipeline. It provides a shared vocabulary for the pipeline data, transformations, labels, and predictions.

It is a human-readable companion to the planned formal OWL ontology. The current source of truth is the committed CSV data and `ExamplePipeline/docs/pipeline_reference.md`.

## Scope and Boundaries

- All identifiers and measurements in the current pipeline are synthetic.
- `modem_mac` and `router_mac` are synthetic identifiers, not literal MAC addresses.
- Numeric values are rounded to four decimal places.
- Measurement units are unspecified in the source documentation and remain unspecified here.
- The ontology describes the broader intended hardware model as well as the current sample-data shape. The current sample contains one customer-device mapping row per customer, but that row pattern is not a universal business constraint.

## Concept Glossary

| Concept | Meaning |
| --- | --- |
| Customer | A customer entity identified by `customer`. |
| Hardware | An abstract superclass for physical or logical network hardware. |
| CompanyHardware | Hardware operated by the service provider. A CMTS is CompanyHardware. |
| CustomerDevice | A piece of Hardware associated with a customer. In this ontology, modem and router are customer-device roles. |
| Modem | Customer hardware identified by `modem_mac`; it carries modem-side and CMTS-side telemetry associations. |
| Router | Customer hardware identified by `router_mac`; it supplies the router signal-to-noise measurement. |
| CMTS | Company hardware representing the cable modem termination system. The current data has `cmts_rx` and `cmts_tx` measurements but no CMTS identifier or standalone CMTS dataset. |
| TelemetryMeasurement | A synthetic measurement associated with network hardware. |
| FeatureVector | A combined set of telemetry features for a customer, modem, and router mapping. |
| ServiceQualityLabel | A rule-derived binary service-quality target represented by `bad_service`. |
| Prediction | A persisted-model output represented by `predicted_bad_service`. |

## Hardware Hierarchy and Ownership

```text
Hardware
|- CustomerDevice
|  |- Modem
|  `- Router
`- CompanyHardware
   `- CMTS
```

A customer may have multiple modems, but each modem is associated with one customer. A modem may have multiple routers, but each router is associated with one modem.

## Hardware Topology

The ontology uses the directed relationship `isAncestorOf` to describe the requested hardware topology:

- `Router isAncestorOf Modem`.
- `Modem isAncestorOf CMTS`.
- Multiple routers may be ancestors of one modem.
- Multiple modems may be ancestors of one CMTS.

This direction is intentional and must be preserved in the formal ontology. It is distinct from the customer ownership relationship.

## Identifiers and Cardinality

| Identifier | Represents | Current data contract |
| --- | --- | --- |
| `customer` | Customer identifier | One crosswalk row per customer in the current synthetic sample. |
| `modem_mac` | Modem identifier | Unique in the current synthetic sample; one modem belongs to one customer in the ontology. |
| `router_mac` | Router identifier | Unique in the current synthetic sample; one router belongs to one modem in the ontology. |

The current Stage 2 and Stage 3 transformations use `customer`, `modem_mac`, and `router_mac` as a composite join key. Raw telemetry keys are shuffled, so record order is not a valid relationship.

## Telemetry Vocabulary

| Field | Measurement meaning | Associated hardware | Documented distribution or range | Quality condition |
| --- | --- | --- | --- | --- |
| `modem_rx` | Downstream receive signal measurement | Modem | Normal distribution, mean 0 and standard deviation 5 | Below -7 or above 7 |
| `modem_tx` | Upstream transmit signal measurement | Modem | Normal distribution, mean 42.5 and standard deviation 6 | Below 35 or above 50 |
| `cmts_rx` | Receive measurement for the CMTS-side modem relationship | Modem and CMTS relationship | Uniform distribution from -2.1 to 2.1 | Below -2 or above 2 |
| `cmts_tx` | Transmit measurement for the CMTS-side modem relationship | Modem and CMTS relationship | Normal distribution, mean 55 and standard deviation 5 | Below 50 or above 60 |
| `router_snr` | Router signal-to-noise ratio measurement | Router | Uniform distribution from -15 to 15 | Below 20 or above 40 |
| `mtr` | Synthetic modem measurement used as a service-quality feature | Modem | Uniform from 25 to 26, except each 100th generated row is uniform from 17 to 18 | Below 18 |

Every generated `router_snr` value breaches the documented quality condition by design, because the generated range is entirely below 20.

## Feature, Label, and Prediction Semantics

A FeatureVector is represented by one row in `data/features/features_unified.csv`. It contains the three identifiers and the six telemetry features.

A ServiceQualityLabel is represented by `bad_service` in `data/targets/target_bad_service.csv`. It is rule-derived, not an observed customer outcome:

- `bad_service = 1` when at least three of the six telemetry quality conditions are breached.
- Otherwise, `bad_service = 0`.

A Prediction is represented by `predicted_bad_service` in `data/scored/predictions_v1.csv`. It is an integer produced by the persisted Stage 5 model from the Stage 3 FeatureVector. It is semantically distinct from the rule-derived `bad_service` label.

## Dataset-to-Concept Mapping

| Dataset | Pipeline role | Ontology concepts represented |
| --- | --- | --- |
| `data/raw/src_customer_device_map.csv` | Customer-device crosswalk | Customer, CustomerDevice, Modem, Router |
| `data/raw/src_modem_signal.csv` | Raw modem telemetry | Modem, TelemetryMeasurement |
| `data/raw/src_cmts_signal.csv` | Raw CMTS-side telemetry | Modem, CMTS, TelemetryMeasurement |
| `data/raw/src_router_signal.csv` | Raw router telemetry | Router, TelemetryMeasurement |
| `data/raw/src_modem_mtr.csv` | Raw modem MTR measurement | Modem, TelemetryMeasurement |
| `data/interim/trn_modem_signal.csv` | Enriched modem telemetry | Customer, Modem, Router, TelemetryMeasurement |
| `data/interim/trn_cmts_signal.csv` | Enriched CMTS-side telemetry | Customer, Modem, Router, CMTS, TelemetryMeasurement |
| `data/interim/trn_router_signal.csv` | Enriched router telemetry | Customer, Modem, Router, TelemetryMeasurement |
| `data/interim/trn_modem_mtr.csv` | Enriched modem MTR telemetry | Customer, Modem, Router, TelemetryMeasurement |
| `data/features/features_unified.csv` | Unified feature data | Customer, Modem, Router, FeatureVector, TelemetryMeasurement |
| `data/targets/target_bad_service.csv` | Rule-derived target | Customer, ServiceQualityLabel |
| `data/gtm/gtm_v1.csv` | Modeling dataset | Customer, Modem, Router, FeatureVector, ServiceQualityLabel |
| `data/scored/predictions_v1.csv` | Inference output | Customer, Modem, Router, Prediction |

## Pipeline Provenance

1. Stage 1 creates raw synthetic customer-device mappings and telemetry measurements.
2. Stage 2 enriches each telemetry dataset with the customer, modem, and router identifiers.
3. Stage 3 joins the interim datasets into a FeatureVector using the composite identifier key.
4. Stage 4 derives a ServiceQualityLabel from the documented threshold rule.
5. Stage 5 joins FeatureVectors to labels for model training and produces GTM data.
6. Stage 6 applies the persisted model to FeatureVectors and produces Predictions.

## Candidate Databricks Logical-Asset Mapping

This ontology is independent of physical storage. The proposed Unity Catalog table, column, and curated-view mapping is maintained in [logical_asset_mapping.md](../../ontology/logical_asset_mapping.md). That mapping uses placeholder catalog and schema names and does not change the business concepts defined in this document.
