# ExamplePipeline Human-Readable Ontology

## Purpose

This document explains every term declared in [examplepipeline_ontology.owl](../../ontology/examplepipeline_ontology.owl). The OWL file is the formal ontology; this page is its readable reference for the synthetic cable-internet telemetry domain modeled by ExamplePipeline.

The OWL file supplies vocabulary and constraints. The generated [RDF/Turtle instance graph](../../../data/ontology/examplepipeline_instances.ttl) applies that vocabulary to every current non-raw CSV row. The dataset and column mappings below document how the vocabulary relates to the pipeline.

## Scope and Boundaries

- All identifiers and measurements in the current pipeline are synthetic.
- `modem_mac` and `router_mac` are synthetic identifiers, not literal MAC addresses.
- Numeric values are rounded to four decimal places.
- Measurement units are unspecified in the source documentation and remain unspecified in the ontology.
- The current sample has one customer-device mapping row per customer. This is not a universal business constraint.
- The current data has CMTS-side measurements but no CMTS identifier or standalone CMTS dataset.
- The RDF export intentionally excludes `data/raw/`. It exports the four interim tables plus feature, target, GTM, and scored datasets.

## RDF Instance Export

Run the exporter from the ExamplePipeline root:

```bash
.venv/bin/python example-pipeline-etl/scripts/etl/export_ontology_rdf.py
```

It writes `data/ontology/examplepipeline_instances.ttl`. The graph assigns stable IRIs to customers, modems, routers, feature vectors, service-quality labels, predictions, the documented Stage 4 rule, and the persisted Stage 5 model. Each interim record is a `TelemetryMeasurement`; each exported resource records its contributing CSV path with `dcterms:source`.

Feature, label, GTM, and scored rows resolve to canonical resources by customer identifier. Therefore, the GTM representation contributes an additional source record to the same feature-vector and label instances rather than creating duplicate semantic entities.

## Ontology Identity

| Item | Value |
| --- | --- |
| Ontology IRI | `https://examplepipeline.invalid/ontology` |
| Namespace | `https://examplepipeline.invalid/ontology/` |
| Version IRI | `https://examplepipeline.invalid/ontology/1.0.0` |
| Version | `1.0.0` |

## Classes

The OWL file declares the following 13 classes.

| Class | Meaning | OWL relationships and constraints |
| --- | --- | --- |
| `Customer` | Synthetic customer identified by `customer`. | Receives `customerIdentifier`; may have customer devices through `hasCustomerDevice`, including modems and routers. |
| `Hardware` | Abstract superclass for network hardware. | Superclass of `CustomerDevice` and `CompanyHardware`; used by hardware-topology properties. |
| `CustomerDevice` | Hardware associated with a customer. | Subclass of `Hardware`; disjoint with `CompanyHardware`. |
| `CompanyHardware` | Hardware operated by the service provider. | Subclass of `Hardware`; disjoint with `CustomerDevice`. |
| `Modem` | Customer device identified by `modem_mac`. | Subclass of `CustomerDevice`; disjoint with `Router`; has exactly one `belongsToCustomer` value that is a `Customer`. |
| `Router` | Customer device identified by `router_mac`. | Subclass of `CustomerDevice`; disjoint with `Modem`; has exactly one `belongsToCustomer` value that is a `Customer`. |
| `CMTS` | Cable modem termination system operated by the provider. | Subclass of `CompanyHardware`. |
| `TelemetryMeasurement` | Synthetic measurement associated with network hardware. | May be linked from a `FeatureVector` through `hasTelemetryMeasurement`. |
| `FeatureVector` | Combined telemetry features for a customer, modem, and router mapping. | Has six feature-value properties and may link to telemetry measurements. |
| `ServiceQualityLabel` | Rule-derived binary service-quality target. | Disjoint with `Prediction`; has one feature vector, one generating rule, and one `badServiceValue`. |
| `Prediction` | Persisted-model output. | Disjoint with `ServiceQualityLabel`; has one target feature vector, one generating model, and one `predictedBadServiceValue`. |
| `ServiceQualityRule` | Documented rule that derives a service-quality label. | Is the range of `isGeneratedByRule`. |
| `PersistedModel` | Saved model that produces predictions from feature vectors. | Is the range of `isGeneratedByModel`. |

## Class Hierarchy and Disjointness

```text
Hardware
|- CustomerDevice
|  |- Modem
|  `- Router
`- CompanyHardware
   `- CMTS
```

`CustomerDevice` and `CompanyHardware` are disjoint. `Modem` and `Router` are disjoint. `ServiceQualityLabel` and `Prediction` are disjoint. An individual cannot consistently belong to either pair of disjoint classes at the same time.

## Object Properties

The OWL file declares the following 11 object properties. A functional property allows at most one value for an individual; the modem and router class restrictions additionally require exactly one appropriately typed value.

| Property | Domain -> range | Meaning and OWL characteristics |
| --- | --- | --- |
| `belongsToCustomer` | `CustomerDevice` -> `Customer` | Assigns a modem or router to its customer. Functional; inverse of `hasCustomerDevice`. Each `Modem` and `Router` has exactly one `Customer` value. |
| `hasCustomerDevice` | `Customer` -> `CustomerDevice` | Inverse direction of `belongsToCustomer`. A customer can have multiple customer devices. |
| `hasModem` | `Customer` -> `Modem` | Customer-to-modem relationship; a subproperty of `hasCustomerDevice`. A customer can have multiple modems. |
| `hasRouter` | `Customer` -> `Router` | Customer-to-router relationship; a subproperty of `hasCustomerDevice`. A customer can have multiple routers. |
| `isAncestorOf` | `Hardware` -> `Hardware` | Directed topology relationship. Transitive and inverse of `hasDescendant`. Router-to-modem and modem-to-CMTS links imply a router-to-CMTS ancestor relationship. |
| `hasDescendant` | `Hardware` -> `Hardware` | Inverse direction of `isAncestorOf`. |
| `hasTelemetryMeasurement` | `FeatureVector` -> `TelemetryMeasurement` | Connects a feature vector to associated telemetry-measurement instances when those instances are represented. |
| `hasFeatureVector` | `ServiceQualityLabel` -> `FeatureVector` | Connects a label to its input feature vector. Functional. |
| `isGeneratedByRule` | `ServiceQualityLabel` -> `ServiceQualityRule` | Records the rule that generated a label. Functional. |
| `isPredictionFor` | `Prediction` -> `FeatureVector` | Connects a prediction to its input feature vector. Functional. |
| `isGeneratedByModel` | `Prediction` -> `PersistedModel` | Records the persisted model that generated a prediction. Functional. |

## Datatype Properties

The OWL file declares the following 11 datatype properties. The six telemetry values are direct properties of `FeatureVector`; the ontology does not require separate `TelemetryMeasurement` instances for current CSV data.

| Property | Domain | XSD range | CSV mapping and meaning |
| --- | --- | --- | --- |
| `customerIdentifier` | `Customer` | `xsd:string` | Maps to `customer`; functional. |
| `modemIdentifier` | `Modem` | `xsd:string` | Maps to synthetic `modem_mac`; functional. |
| `routerIdentifier` | `Router` | `xsd:string` | Maps to synthetic `router_mac`; functional. |
| `modemRx` | `FeatureVector` | `xsd:decimal` | Maps to `modem_rx`, the modem receive measurement. |
| `modemTx` | `FeatureVector` | `xsd:decimal` | Maps to `modem_tx`, the modem transmit measurement. |
| `cmtsRx` | `FeatureVector` | `xsd:decimal` | Maps to `cmts_rx`, the CMTS receive measurement. |
| `cmtsTx` | `FeatureVector` | `xsd:decimal` | Maps to `cmts_tx`, the CMTS transmit measurement. |
| `routerSnr` | `FeatureVector` | `xsd:decimal` | Maps to `router_snr`, the router signal-to-noise measurement. |
| `mtr` | `FeatureVector` | `xsd:decimal` | Maps to `mtr`, the synthetic modem service-quality feature. |
| `badServiceValue` | `ServiceQualityLabel` | `xsd:boolean` | Maps to `bad_service`; functional and true when at least three documented conditions are breached. |
| `predictedBadServiceValue` | `Prediction` | `xsd:integer` | Maps to `predicted_bad_service`; functional model output. |

## Telemetry and Label Meaning

| Field | Current documented quality condition |
| --- | --- |
| `modem_rx` | Below -7 or above 7 |
| `modem_tx` | Below 35 or above 50 |
| `cmts_rx` | Below -2 or above 2 |
| `cmts_tx` | Below 50 or above 60 |
| `router_snr` | Below 20 or above 40 |
| `mtr` | Below 18 |

`bad_service` is true when at least three of these six conditions are breached; otherwise it is false. `predicted_bad_service` is a model output and is not the same kind of thing as the rule-derived label.

## Dataset-to-Concept Mapping

| Dataset | Pipeline role | Ontology concepts represented |
| --- | --- | --- |
| `data/raw/src_customer_device_map.csv` | Customer-device mapping table | `Customer`, `Modem`, `Router`, `belongsToCustomer`, `hasModem`, `hasRouter` |
| `data/raw/src_modem_signal.csv` | Raw modem telemetry | `Modem`, `TelemetryMeasurement` |
| `data/raw/src_cmts_signal.csv` | Raw CMTS-side telemetry | `Modem`, `CMTS`, `TelemetryMeasurement` |
| `data/raw/src_router_signal.csv` | Raw router telemetry | `Router`, `TelemetryMeasurement` |
| `data/raw/src_modem_mtr.csv` | Raw modem MTR measurement | `Modem`, `TelemetryMeasurement` |
| `data/interim/trn_*.csv` | Enriched telemetry | Customer, modem, router, and telemetry concepts |
| `data/features/features_unified.csv` | Unified feature data | `FeatureVector` and its six telemetry datatype properties |
| `data/targets/target_bad_service.csv` | Rule-derived target | `ServiceQualityLabel`, `badServiceValue`, `ServiceQualityRule` |
| `data/gtm/gtm_v1.csv` | Modeling dataset | Feature-vector and service-quality-label concepts |
| `data/scored/predictions_v1.csv` | Inference output | `Prediction`, `predictedBadServiceValue`, `PersistedModel` |

## Pipeline Provenance

1. Stage 1 creates raw synthetic customer-device mappings and telemetry measurements.
2. Stage 2 enriches telemetry with customer, modem, and router identifiers.
3. Stage 3 joins interim datasets into a `FeatureVector` using the composite identifier key.
4. Stage 4 derives a `ServiceQualityLabel` from the threshold rule.
5. Stage 5 joins feature vectors to labels for model training and produces GTM data.
6. Stage 6 applies a `PersistedModel` to feature vectors and produces `Prediction` values.

## Logical-Asset Mapping

This ontology is independent of physical storage. The proposed Unity Catalog table, column, and curated-view mapping is maintained in [logical_asset_mapping.md](../../ontology/logical_asset_mapping.md). It uses placeholder catalog and schema names and does not change the OWL vocabulary defined here.
