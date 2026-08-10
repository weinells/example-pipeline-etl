# ExamplePipeline Logical Asset Mapping

## Purpose

This document maps the ExamplePipeline ontology to logical data assets suitable for a future Databricks Unity Catalog deployment. It is a conceptual mapping, not a physical deployment specification.

The human-readable ontology remains the source of business meaning. This document describes how that meaning could be exposed through Unity Catalog assets without making the ontology dependent on a particular storage location, file format, catalog, or schema.

## Naming Pattern

Use the following placeholders until a Unity Catalog deployment defines actual values:

```text
<catalog>.<schema>.<table>
```

- `<catalog>` is the Unity Catalog catalog selected for the environment.
- `<schema>` is the Unity Catalog schema selected for the data domain.
- `<table>` is the logical table name.

The proposed table names below reflect current pipeline assets. They are recommendations, not mandated physical names.

## Layering Rules

- The ontology defines concepts and relationships such as Customer, Modem, Router, CMTS, FeatureVector, ServiceQualityLabel, and Prediction.
- Unity Catalog tables, views, and columns are logical assets that represent those concepts for data access and governance.
- A table or column location does not redefine the ontology concept it represents.
- The conceptual CMTS remains valid even though the current datasets have CMTS-side measurements but no CMTS identifier or standalone CMTS table.
- The mapping must not imply physical units for measurements whose units are unspecified.

## Dataset-to-Logical-Asset Mapping

| Current dataset | Proposed logical asset | Asset type | Ontology concepts represented |
| --- | --- | --- | --- |
| `data/raw/src_customer_device_map.csv` | `<catalog>.<schema>.src_customer_device_map` | Table | Customer, CustomerDevice, Modem, Router |
| `data/raw/src_modem_signal.csv` | `<catalog>.<schema>.src_modem_signal` | Table | Modem, TelemetryMeasurement |
| `data/raw/src_cmts_signal.csv` | `<catalog>.<schema>.src_cmts_signal` | Table | Modem, CMTS, TelemetryMeasurement |
| `data/raw/src_router_signal.csv` | `<catalog>.<schema>.src_router_signal` | Table | Router, TelemetryMeasurement |
| `data/raw/src_modem_mtr.csv` | `<catalog>.<schema>.src_modem_mtr` | Table | Modem, TelemetryMeasurement |
| `data/interim/trn_modem_signal.csv` | `<catalog>.<schema>.trn_modem_signal` | Table | Customer, Modem, Router, TelemetryMeasurement |
| `data/interim/trn_cmts_signal.csv` | `<catalog>.<schema>.trn_cmts_signal` | Table | Customer, Modem, Router, CMTS, TelemetryMeasurement |
| `data/interim/trn_router_signal.csv` | `<catalog>.<schema>.trn_router_signal` | Table | Customer, Modem, Router, TelemetryMeasurement |
| `data/interim/trn_modem_mtr.csv` | `<catalog>.<schema>.trn_modem_mtr` | Table | Customer, Modem, Router, TelemetryMeasurement |
| `data/features/features_unified.csv` | `<catalog>.<schema>.features_unified` | Table | Customer, Modem, Router, FeatureVector, TelemetryMeasurement |
| `data/targets/target_bad_service.csv` | `<catalog>.<schema>.target_bad_service` | Table | Customer, ServiceQualityLabel |
| `data/gtm/gtm_v1.csv` | `<catalog>.<schema>.gtm_v1` | Table | Customer, Modem, Router, FeatureVector, ServiceQualityLabel |
| `data/scored/predictions_v1.csv` | `<catalog>.<schema>.predictions_v1` | Table | Customer, Modem, Router, Prediction |

## Column-to-Concept Mapping

| Logical column pattern | Ontology concept or property | Notes |
| --- | --- | --- |
| `customer` | Customer identifier | Synthetic customer identifier. |
| `modem_mac` | Modem identifier | Synthetic modem identifier; not a literal MAC address. |
| `router_mac` | Router identifier | Synthetic router identifier; not a literal MAC address. |
| `modem_rx`, `modem_tx` | TelemetryMeasurement associated with Modem | Units remain unspecified. |
| `cmts_rx`, `cmts_tx` | TelemetryMeasurement associated with the Modem-to-CMTS relationship | The current data does not provide a CMTS identifier. |
| `router_snr` | TelemetryMeasurement associated with Router | Units remain unspecified. |
| `mtr` | TelemetryMeasurement associated with Modem | Units remain unspecified. |
| `bad_service` | ServiceQualityLabel | Rule-derived binary target. |
| `predicted_bad_service` | Prediction | Integer output produced by the persisted model. |

## Curated Views

A deployment may add views without changing the ontology. Suggested views are:

| Proposed view | Purpose | Ontology concepts represented |
| --- | --- | --- |
| `<catalog>.<schema>.vw_feature_vectors` | Expose feature vectors with identifier context | Customer, Modem, Router, FeatureVector, TelemetryMeasurement |
| `<catalog>.<schema>.vw_service_quality_labels` | Expose rule-derived labels with identifier context | Customer, ServiceQualityLabel |
| `<catalog>.<schema>.vw_predictions` | Expose model predictions with identifier context | Customer, Modem, Router, Prediction |

## Governance and Evolution

- Assign Unity Catalog descriptions and tags from the human-readable ontology for each table and column.
- Keep this mapping under version control with the ontology.
- Update the mapping when a dataset, schema, ontology concept, or curated view changes.
- Add lineage or ownership metadata only when it is known for the target environment; do not infer it from this synthetic pipeline.
