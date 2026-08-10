from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import quote

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD
from rdflib.namespace import DCTERMS, RDFS


ONTOLOGY = Namespace("https://examplepipeline.invalid/ontology/")
INSTANCE = Namespace("https://examplepipeline.invalid/data/")
FEATURE_COLUMNS = ("modem_rx", "modem_tx", "cmts_rx", "cmts_tx", "router_snr", "mtr")
FEATURE_PROPERTIES = {
    "modem_rx": ONTOLOGY.modemRx,
    "modem_tx": ONTOLOGY.modemTx,
    "cmts_rx": ONTOLOGY.cmtsRx,
    "cmts_tx": ONTOLOGY.cmtsTx,
    "router_snr": ONTOLOGY.routerSnr,
    "mtr": ONTOLOGY.mtr,
}
INTERIM_DATASETS = {
    "trn_modem_signal.csv": "modem signal",
    "trn_cmts_signal.csv": "CMTS signal",
    "trn_router_signal.csv": "router signal",
    "trn_modem_mtr.csv": "MTR",
}


def _resource(kind: str, identifier: str) -> URIRef:
    return INSTANCE[f"{kind}/{quote(identifier, safe='')}"]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def _add_customer_devices(graph: Graph, row: dict[str, str]) -> tuple[URIRef, URIRef, URIRef]:
    customer = _resource("customer", row["customer"])
    modem = _resource("modem", row["modem_mac"])
    router = _resource("router", row["router_mac"])

    graph.add((customer, RDF.type, ONTOLOGY.Customer))
    graph.add((customer, ONTOLOGY.customerIdentifier, Literal(row["customer"], datatype=XSD.string)))
    graph.add((modem, RDF.type, ONTOLOGY.Modem))
    graph.add((modem, ONTOLOGY.modemIdentifier, Literal(row["modem_mac"], datatype=XSD.string)))
    graph.add((modem, ONTOLOGY.belongsToCustomer, customer))
    graph.add((customer, ONTOLOGY.hasModem, modem))
    graph.add((router, RDF.type, ONTOLOGY.Router))
    graph.add((router, ONTOLOGY.routerIdentifier, Literal(row["router_mac"], datatype=XSD.string)))
    graph.add((router, ONTOLOGY.belongsToCustomer, customer))
    graph.add((customer, ONTOLOGY.hasRouter, router))
    return customer, modem, router


def _feature_vector(graph: Graph, row: dict[str, str], source: str) -> URIRef:
    customer, _, _ = _add_customer_devices(graph, row)
    feature_vector = _resource("feature-vector", row["customer"])
    graph.add((feature_vector, RDF.type, ONTOLOGY.FeatureVector))
    graph.add((feature_vector, DCTERMS.source, Literal(source)))
    graph.add((feature_vector, RDFS.label, Literal(f"Feature vector for {row['customer']}")))
    for column in FEATURE_COLUMNS:
        graph.add((feature_vector, FEATURE_PROPERTIES[column], Literal(row[column], datatype=XSD.decimal)))
    return feature_vector


def _export_interim_rows(graph: Graph, interim_dir: Path) -> None:
    for filename, measurement_name in INTERIM_DATASETS.items():
        source = f"data/interim/{filename}"
        for row in _read_rows(interim_dir / filename):
            _add_customer_devices(graph, row)
            feature_vector = _resource("feature-vector", row["customer"])
            measurement = _resource(f"telemetry/{filename.removesuffix('.csv')}", row["customer"])
            graph.add((measurement, RDF.type, ONTOLOGY.TelemetryMeasurement))
            graph.add((measurement, DCTERMS.source, Literal(source)))
            graph.add((measurement, RDFS.label, Literal(f"{measurement_name} telemetry for {row['customer']}")))
            graph.add((feature_vector, ONTOLOGY.hasTelemetryMeasurement, measurement))


def _export_feature_rows(graph: Graph, features_path: Path) -> None:
    for row in _read_rows(features_path):
        _feature_vector(graph, row, "data/features/features_unified.csv")


def _export_label_rows(graph: Graph, targets_path: Path, source: str) -> None:
    for row in _read_rows(targets_path):
        customer = _resource("customer", row["customer"])
        feature_vector = _resource("feature-vector", row["customer"])
        label = _resource("service-quality-label", row["customer"])
        rule = _resource("service-quality-rule", "stage4-threshold-rule")
        graph.add((customer, RDF.type, ONTOLOGY.Customer))
        graph.add((customer, ONTOLOGY.customerIdentifier, Literal(row["customer"], datatype=XSD.string)))
        graph.add((label, RDF.type, ONTOLOGY.ServiceQualityLabel))
        graph.add((label, ONTOLOGY.badServiceValue, Literal(row["bad_service"] == "1", datatype=XSD.boolean)))
        graph.add((label, ONTOLOGY.hasFeatureVector, feature_vector))
        graph.add((label, ONTOLOGY.isGeneratedByRule, rule))
        graph.add((label, DCTERMS.source, Literal(source)))
        graph.add((rule, RDF.type, ONTOLOGY.ServiceQualityRule))
        graph.add((rule, RDFS.label, Literal("Stage 4 service-quality threshold rule")))


def _export_gtm_rows(graph: Graph, gtm_path: Path) -> None:
    for row in _read_rows(gtm_path):
        _feature_vector(graph, row, "data/gtm/gtm_v1.csv")
    _export_label_rows(graph, gtm_path, "data/gtm/gtm_v1.csv")


def _export_prediction_rows(graph: Graph, predictions_path: Path) -> None:
    model = _resource("persisted-model", "stage5-best-model")
    graph.add((model, RDF.type, ONTOLOGY.PersistedModel))
    graph.add((model, RDFS.label, Literal("Persisted Stage 5 model")))
    for row in _read_rows(predictions_path):
        _add_customer_devices(graph, row)
        feature_vector = _resource("feature-vector", row["customer"])
        prediction = _resource("prediction", row["customer"])
        graph.add((prediction, RDF.type, ONTOLOGY.Prediction))
        graph.add((prediction, ONTOLOGY.predictedBadServiceValue, Literal(row["predicted_bad_service"], datatype=XSD.integer)))
        graph.add((prediction, ONTOLOGY.isPredictionFor, feature_vector))
        graph.add((prediction, ONTOLOGY.isGeneratedByModel, model))
        graph.add((prediction, DCTERMS.source, Literal("data/scored/predictions_v1.csv")))


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    data_dir = project_root / "data"
    output_path = data_dir / "ontology" / "examplepipeline_instances.ttl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    graph = Graph()
    graph.bind("ep", ONTOLOGY)
    graph.bind("epdata", INSTANCE)
    graph.bind("dcterms", DCTERMS)

    _export_interim_rows(graph, data_dir / "interim")
    _export_feature_rows(graph, data_dir / "features" / "features_unified.csv")
    _export_label_rows(graph, data_dir / "targets" / "target_bad_service.csv", "data/targets/target_bad_service.csv")
    _export_gtm_rows(graph, data_dir / "gtm" / "gtm_v1.csv")
    _export_prediction_rows(graph, data_dir / "scored" / "predictions_v1.csv")

    graph.serialize(destination=output_path, format="turtle", encoding="utf-8")
    print(f"Wrote {len(graph)} triples to {output_path}")


if __name__ == "__main__":
    main()