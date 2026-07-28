from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: str
    description: str


@dataclass(frozen=True)
class TableSpec:
    slug: str
    title: str
    summary: str
    source_path: str
    stage: str
    columns: tuple[ColumnSpec, ...]


TABLES: tuple[TableSpec, ...] = (
    TableSpec(
        slug="src_customer_device_map",
        title="src_customer_device_map.csv",
        summary="Source customer-to-device mapping table for the HFC network. It connects each customer to a modem and router identifier.",
        source_path="data/raw/src_customer_device_map.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier assigned to the subscriber record."),
            ColumnSpec("modem_mac", "string", "Modem MAC address used to identify the cable modem."),
            ColumnSpec("router_mac", "string", "Router MAC address used to identify the customer gateway or router."),
        ),
    ),
    TableSpec(
        slug="src_modem_signal",
        title="src_modem_signal.csv",
        summary="Raw modem signal telemetry captured from the HFC access network.",
        source_path="data/raw/src_modem_signal.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("modem_mac", "string", "Modem MAC address that ties the telemetry back to a specific modem."),
            ColumnSpec("modem_rx", "float", "Modem receive signal level or power reading."),
            ColumnSpec("modem_tx", "float", "Modem transmit signal level or power reading."),
        ),
    ),
    TableSpec(
        slug="src_cmts_signal",
        title="src_cmts_signal.csv",
        summary="Raw CMTS-side signal telemetry for the cable access path.",
        source_path="data/raw/src_cmts_signal.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("modem_mac", "string", "Modem MAC address used to align the cable modem to its CMTS readings."),
            ColumnSpec("cmts_rx", "float", "CMTS receive signal level for the modem path."),
            ColumnSpec("cmts_tx", "float", "CMTS transmit signal level for the modem path."),
        ),
    ),
    TableSpec(
        slug="src_router_signal",
        title="src_router_signal.csv",
        summary="Raw router-side signal telemetry associated with the customer gateway.",
        source_path="data/raw/src_router_signal.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("router_mac", "string", "Router MAC address that identifies the gateway device."),
            ColumnSpec("router_snr", "float", "Router signal-to-noise ratio measurement."),
        ),
    ),
    TableSpec(
        slug="src_modem_mtr",
        title="src_modem_mtr.csv",
        summary="Raw modem telemetry table that carries the MTR service-health measurement used later in target generation.",
        source_path="data/raw/src_modem_mtr.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("modem_mac", "string", "Modem MAC address used to connect the reading to a specific modem."),
            ColumnSpec("mtr", "float", "Modem telemetry reading (MTR), a service-health signal used in downstream rule logic."),
        ),
    ),
    TableSpec(
        slug="trn_cmts_signal",
        title="trn_cmts_signal.csv",
        summary="Join-ready CMTS telemetry enriched with customer and router identifiers.",
        source_path="data/interim/trn_cmts_signal.csv",
        stage="Interim ETL",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier added during ETL join standardization."),
            ColumnSpec("modem_mac", "string", "Modem MAC address carried through the standardized join."),
            ColumnSpec("router_mac", "string", "Router MAC address carried through the standardized join."),
            ColumnSpec("cmts_rx", "float", "CMTS receive signal level."),
            ColumnSpec("cmts_tx", "float", "CMTS transmit signal level."),
        ),
    ),
    TableSpec(
        slug="trn_modem_signal",
        title="trn_modem_signal.csv",
        summary="Join-ready modem signal telemetry enriched with customer and router identifiers.",
        source_path="data/interim/trn_modem_signal.csv",
        stage="Interim ETL",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier added during ETL join standardization."),
            ColumnSpec("modem_mac", "string", "Modem MAC address carried through the standardized join."),
            ColumnSpec("router_mac", "string", "Router MAC address carried through the standardized join."),
            ColumnSpec("modem_rx", "float", "Modem receive signal level or power reading."),
            ColumnSpec("modem_tx", "float", "Modem transmit signal level or power reading."),
        ),
    ),
    TableSpec(
        slug="trn_router_signal",
        title="trn_router_signal.csv",
        summary="Join-ready router signal telemetry enriched with customer and modem identifiers.",
        source_path="data/interim/trn_router_signal.csv",
        stage="Interim ETL",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier added during ETL join standardization."),
            ColumnSpec("modem_mac", "string", "Modem MAC address carried through the standardized join."),
            ColumnSpec("router_mac", "string", "Router MAC address carried through the standardized join."),
            ColumnSpec("router_snr", "float", "Router signal-to-noise ratio measurement."),
        ),
    ),
    TableSpec(
        slug="trn_modem_mtr",
        title="trn_modem_mtr.csv",
        summary="Join-ready modem telemetry reading enriched with customer and router identifiers.",
        source_path="data/interim/trn_modem_mtr.csv",
        stage="Interim ETL",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier added during ETL join standardization."),
            ColumnSpec("modem_mac", "string", "Modem MAC address carried through the standardized join."),
            ColumnSpec("router_mac", "string", "Router MAC address carried through the standardized join."),
            ColumnSpec("mtr", "float", "Modem telemetry reading (MTR), carried into the join-ready table."),
        ),
    ),
    TableSpec(
        slug="features_unified",
        title="features_unified.csv",
        summary="Unified modeling feature table formed by joining the four interim ETL outputs.",
        source_path="data/features/features_unified.csv",
        stage="Feature assembly",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier for the unified feature row."),
            ColumnSpec("modem_mac", "string", "Modem MAC address for the unified feature row."),
            ColumnSpec("router_mac", "string", "Router MAC address for the unified feature row."),
            ColumnSpec("modem_rx", "float", "Modem receive signal level or power reading."),
            ColumnSpec("modem_tx", "float", "Modem transmit signal level or power reading."),
            ColumnSpec("cmts_rx", "float", "CMTS receive signal level."),
            ColumnSpec("cmts_tx", "float", "CMTS transmit signal level."),
            ColumnSpec("router_snr", "float", "Router signal-to-noise ratio measurement."),
            ColumnSpec("mtr", "float", "Modem telemetry reading (MTR) used as a downstream service-health feature."),
        ),
    ),
    TableSpec(
        slug="target_bad_service",
        title="target_bad_service.csv",
        summary="Synthetic binary target table indicating whether a customer is labeled for bad service.",
        source_path="data/targets/target_bad_service.csv",
        stage="Target engineering",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier used to align the target with the feature table."),
            ColumnSpec("bad_service", "integer", "Binary label indicating whether the customer is flagged for bad service."),
        ),
    ),
    TableSpec(
        slug="gtm_v1",
        title="gtm_v1.csv",
        summary="Good-to-model training table that combines the unified features with the synthetic target.",
        source_path="data/gtm/gtm_v1.csv",
        stage="Modeling dataset",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier for the modeling row."),
            ColumnSpec("modem_mac", "string", "Modem MAC address for the modeling row."),
            ColumnSpec("router_mac", "string", "Router MAC address for the modeling row."),
            ColumnSpec("modem_rx", "float", "Modem receive signal level or power reading."),
            ColumnSpec("modem_tx", "float", "Modem transmit signal level or power reading."),
            ColumnSpec("cmts_rx", "float", "CMTS receive signal level."),
            ColumnSpec("cmts_tx", "float", "CMTS transmit signal level."),
            ColumnSpec("router_snr", "float", "Router signal-to-noise ratio measurement."),
            ColumnSpec("mtr", "float", "Modem telemetry reading (MTR) used in the model training set."),
            ColumnSpec("bad_service", "integer", "Binary target label used for model training and evaluation."),
        ),
    ),
    TableSpec(
        slug="predictions_v1",
        title="predictions_v1.csv",
        summary="Inference output table containing the model predictions for bad service.",
        source_path="data/scored/predictions_v1.csv",
        stage="Scoring output",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier for the scored record."),
            ColumnSpec("modem_mac", "string", "Modem MAC address for the scored record."),
            ColumnSpec("router_mac", "string", "Router MAC address for the scored record."),
            ColumnSpec("predicted_bad_service", "integer", "Model prediction for the bad service flag."),
        ),
    ),
)


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
TABLE_DOCS_DIR = DOCS_DIR / "table-docs"
HTML_DIR = TABLE_DOCS_DIR / "html"
DIAGRAM_DIR = DOCS_DIR / "diagrams"
SCHEMA_MD = TABLE_DOCS_DIR / "table_schemas.md"
INDEX_HTML = TABLE_DOCS_DIR / "index.html"
MERMAID_MD = DIAGRAM_DIR / "etl_job_flow.mmd"


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_schema_markdown() -> str:
    parts = ["# ExamplePipeline Table Schemas", ""]
    for table in TABLES:
        parts.extend(
            [
                f"## {table.title}",
                f"- Stage: {table.stage}",
                f"- Source path: `{table.source_path}`",
                f"- Summary: {table.summary}",
                "",
                "| Column | Type | Description |",
                "| --- | --- | --- |",
            ]
        )
        for column in table.columns:
            parts.append(f"| {column.name} | {column.dtype} | {column.description} |")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def render_table_html(table: TableSpec) -> str:
    rows = []
    for column in table.columns:
        rows.append(
            "<tr>"
            f"<td>{html_escape(column.name)}</td>"
            f"<td>{html_escape(column.dtype)}</td>"
            f"<td>{html_escape(column.description)}</td>"
            "</tr>"
        )

    return dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>{html_escape(table.title)}</title>
          <style>
            body {{ font-family: Arial, sans-serif; margin: 32px; color: #102033; line-height: 1.5; }}
            .crumbs {{ margin-bottom: 16px; }}
            a {{ color: #0b5cad; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            h1 {{ margin-bottom: 8px; }}
            .meta {{ color: #51606f; margin: 0 0 20px 0; }}
            .summary {{ background: #f6f9fc; border: 1px solid #d8e2ee; border-radius: 10px; padding: 16px; margin-bottom: 24px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border-bottom: 1px solid #d8e2ee; padding: 10px 12px; text-align: left; vertical-align: top; }}
            th {{ background: #eef4fb; }}
          </style>
        </head>
        <body>
          <div class="crumbs"><a href="index.html">Table index</a></div>
          <h1>{html_escape(table.title)}</h1>
          <p class="meta">Stage: {html_escape(table.stage)} | Source: {html_escape(table.source_path)}</p>
          <div class="summary">
            <strong>Summary</strong>
            <p>{html_escape(table.summary)}</p>
          </div>
          <table>
            <thead>
              <tr><th>Column</th><th>Type</th><th>Description</th></tr>
            </thead>
            <tbody>
              {''.join(rows)}
            </tbody>
          </table>
        </body>
        </html>
        """
    ).strip() + "\n"


def render_index_html() -> str:
    sections = {
        "Raw source": [],
        "Interim ETL": [],
        "Feature assembly": [],
        "Target engineering": [],
        "Modeling dataset": [],
        "Scoring output": [],
    }
    for table in TABLES:
        sections[table.stage].append(table)

    body_sections = []
    for stage, tables in sections.items():
        items = "".join(
            f'<li><a href="html/{html_escape(table.slug)}.html">{html_escape(table.title)}</a> - {html_escape(table.summary)}</li>'
            for table in tables
        )
        body_sections.append(f"<section><h2>{html_escape(stage)}</h2><ul>{items}</ul></section>")

    return dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>ExamplePipeline Table Documentation</title>
          <style>
            body {{ font-family: Arial, sans-serif; margin: 32px; color: #102033; line-height: 1.55; }}
            h1 {{ margin-bottom: 8px; }}
            .lead {{ color: #51606f; max-width: 900px; }}
            section {{ margin-top: 28px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 10px; }}
            a {{ color: #0b5cad; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
          </style>
        </head>
        <body>
          <h1>ExamplePipeline Table Documentation</h1>
          <p class="lead">Each page summarizes what the table captures and lists the schema below that summary. The pages are organized by pipeline stage so the ETL flow is easy to follow.</p>
          {''.join(body_sections)}
        </body>
        </html>
        """
    ).strip() + "\n"


def render_mermaid() -> str:
    return dedent(
        """\
        flowchart LR
          subgraph Raw[Raw source files]
            src_map[src_customer_device_map.csv]
            src_modem[src_modem_signal.csv]
            src_cmts[src_cmts_signal.csv]
            src_router[src_router_signal.csv]
            src_mtr[src_modem_mtr.csv]
          end

          subgraph Interim[Interim ETL jobs]
            job_modem[etl_modem_signal_from_notebook.py]
            job_cmts[etl_cmts_signal.py]
            job_router[etl_router_signal.py]
            job_mtr[etl_modem_mtr.py]
          end

          subgraph Feature[Feature assembly]
            job_features[etl_unified_features.py]
          end

          subgraph Modeling[Modeling and scoring]
            job_stage5[stage5_train_and_track.py]
            job_score[score_stage3_features.py]
          end

          src_map --> job_modem
          src_modem --> job_modem
          job_modem --> trn_modem[trn_modem_signal.csv]

          src_map --> job_cmts
          src_cmts --> job_cmts
          job_cmts --> trn_cmts[trn_cmts_signal.csv]

          src_map --> job_router
          src_router --> job_router
          job_router --> trn_router[trn_router_signal.csv]

          src_map --> job_mtr
          src_mtr --> job_mtr
          job_mtr --> trn_mtr[trn_modem_mtr.csv]

          trn_modem --> job_features
          trn_cmts --> job_features
          trn_router --> job_features
          trn_mtr --> job_features
          job_features --> features[features_unified.csv]
          job_features --> validation[stage3_join_validation.csv]

          features --> job_stage5
          target[target_bad_service.csv] --> job_stage5
          job_stage5 --> gtm[gtm_v1.csv]
          job_stage5 --> metrics[outputs/metrics/stage5_model_comparison.csv]
          job_stage5 --> modelref[models/best_model_reference.json]
          job_stage5 --> modeldir[models/best_model_mlflow/]
          job_stage5 --> mlruns[outputs/mlruns/]

          features --> job_score
          modelref --> job_score
          job_score --> scored[predictions_v1.csv]
        """
    ).strip() + "\n"


def write_outputs() -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    SCHEMA_MD.write_text(render_schema_markdown(), encoding="utf-8")
    INDEX_HTML.write_text(render_index_html(), encoding="utf-8")
    MERMAID_MD.write_text(render_mermaid(), encoding="utf-8")

    for table in TABLES:
        (HTML_DIR / f"{table.slug}.html").write_text(render_table_html(table), encoding="utf-8")


if __name__ == "__main__":
    write_outputs()