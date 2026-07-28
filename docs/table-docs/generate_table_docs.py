from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Dict, List


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: str
    description: str


@dataclass(frozen=True)
class TableSpec:
    slug: str
    file_name: str
    display_title: str
    summary: str
    source_path: str
    stage: str
    columns: tuple[ColumnSpec, ...]


@dataclass(frozen=True)
class NumericProfile:
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float
    outlier_count: int


@dataclass(frozen=True)
class TableProfile:
    row_count: int
    numeric_profiles: Dict[str, NumericProfile]
    binary_counts: Dict[str, Dict[str, int]]


TABLES: tuple[TableSpec, ...] = (
    TableSpec(
        slug="src_customer_device_map",
        file_name="src_customer_device_map.csv",
        display_title="Customer Device Map",
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
        file_name="src_modem_signal.csv",
        display_title="Modem Signal Telemetry",
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
        file_name="src_cmts_signal.csv",
        display_title="CMTS Signal Telemetry",
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
        file_name="src_router_signal.csv",
        display_title="Router Signal Telemetry",
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
        file_name="src_modem_mtr.csv",
        display_title="Modem Main Tap Ratio Telemetry",
        summary="Raw Main Tap Ratio (MTR) telemetry table. In cable pre-equalization context, higher MTR indicates a cleaner primary path; this dataset is mostly 25-26 with a small low band at 17-18.",
        source_path="data/raw/src_modem_mtr.csv",
        stage="Raw source",
        columns=(
            ColumnSpec("modem_mac", "string", "Modem MAC address used to connect the reading to a specific modem."),
            ColumnSpec("mtr", "float", "Main Tap Ratio: relative dominance of the main equalizer tap versus non-main taps/reflections; higher values indicate cleaner upstream channel conditions."),
        ),
    ),
    TableSpec(
        slug="trn_cmts_signal",
        file_name="trn_cmts_signal.csv",
        display_title="Transformed CMTS Signal",
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
        file_name="trn_modem_signal.csv",
        display_title="Transformed Modem Signal",
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
        file_name="trn_router_signal.csv",
        display_title="Transformed Router Signal",
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
        file_name="trn_modem_mtr.csv",
        display_title="Transformed Modem MTR",
        summary="Join-ready modem telemetry reading enriched with customer and router identifiers.",
        source_path="data/interim/trn_modem_mtr.csv",
        stage="Interim ETL",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier added during ETL join standardization."),
            ColumnSpec("modem_mac", "string", "Modem MAC address carried through the standardized join."),
            ColumnSpec("router_mac", "string", "Router MAC address carried through the standardized join."),
            ColumnSpec("mtr", "float", "Main Tap Ratio carried into the join-ready table; lower values indicate stronger non-main tap energy and likely echo/reflection impairment."),
        ),
    ),
    TableSpec(
        slug="features_unified",
        file_name="features_unified.csv",
        display_title="Unified Network Features",
        summary="Unified modeling feature table formed by joining the four interim ETL outputs.",
        source_path="data/features/features_unified.csv",
        stage="Feature assembly",
        columns=(
            ColumnSpec("customer", "string", "Customer identifier for the unified feature row."),
            ColumnSpec("modem_mac", "string", "Modem MAC address for the customer-side cable modem endpoint."),
            ColumnSpec("router_mac", "string", "Router MAC address for the customer gateway endpoint."),
            ColumnSpec("modem_rx", "float", "Modem receive power-level telemetry from the access path."),
            ColumnSpec("modem_tx", "float", "Modem transmit power-level telemetry from the access path."),
            ColumnSpec("cmts_rx", "float", "CMTS-side receive level telemetry for the same modem path."),
            ColumnSpec("cmts_tx", "float", "CMTS-side transmit level telemetry for the same modem path."),
            ColumnSpec("router_snr", "float", "Router-side signal-to-noise ratio telemetry from gateway measurements."),
            ColumnSpec("mtr", "float", "Main Tap Ratio feature where lower values indicate stronger reflected/non-main tap energy."),
        ),
    ),
    TableSpec(
        slug="target_bad_service",
        file_name="target_bad_service.csv",
        display_title="Bad Service Target Labels",
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
        file_name="gtm_v1.csv",
        display_title="Good to Model Dataset (Version 1)",
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
            ColumnSpec("mtr", "float", "Main Tap Ratio used in model training; low values align with degradation scenarios in this dataset."),
            ColumnSpec("bad_service", "integer", "Binary target label used for model training and evaluation."),
        ),
    ),
    TableSpec(
        slug="predictions_v1",
        file_name="predictions_v1.csv",
        display_title="Bad Service Predictions (Version 1)",
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
REPO_DOCS_DIR = ROOT / "docs"
PROJECT_DOCS_DIR = ROOT.parent / "docs"

SCHEMA_MD = REPO_DOCS_DIR / "table-docs" / "table_schemas.md"
PUBLISHED_TABLE_DOCS_DIR = PROJECT_DOCS_DIR / "table-docs"
HTML_DIR = PUBLISHED_TABLE_DOCS_DIR / "html"
INDEX_HTML = PUBLISHED_TABLE_DOCS_DIR / "index.html"
DIAGRAM_DIR = PROJECT_DOCS_DIR / "diagrams"
MERMAID_MD = DIAGRAM_DIR / "etl_job_flow.mmd"


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def infer_role(column: ColumnSpec) -> str:
    name = column.name.lower()
    if "customer" in name or "mac" in name or name.endswith("_id") or name == "id":
        return "Identifier"
    if "bad_service" in name or "predicted" in name:
        return "Label"
    if column.dtype in {"float", "integer"}:
        return "Telemetry"
    return "Attribute"


def quantile(sorted_values: List[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    low_idx = int(position)
    high_idx = min(low_idx + 1, len(sorted_values) - 1)
    fraction = position - low_idx
    return sorted_values[low_idx] * (1.0 - fraction) + sorted_values[high_idx] * fraction


def format_number(value: float) -> str:
    return f"{value:.4f}"


def is_binary_value(value: str) -> bool:
  normalized = value.strip()
  if normalized in {"0", "1"}:
    return True
  if normalized in {"0.0", "1.0"}:
    return True
  return False


def scale_to_axis(value: float, minimum: float, maximum: float, left: float = 40.0, right: float = 960.0) -> float:
  if maximum == minimum:
    return (left + right) / 2.0
  return left + ((value - minimum) / (maximum - minimum)) * (right - left)


def load_table_rows(table: TableSpec) -> List[Dict[str, str]]:
    csv_path = ROOT.parent / table.source_path
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def profile_table(table: TableSpec) -> TableProfile:
    rows = load_table_rows(table)
    numeric_profiles: Dict[str, NumericProfile] = {}
    binary_counts: Dict[str, Dict[str, int]] = {}

    for column in table.columns:
        values = [row.get(column.name, "").strip() for row in rows]
        non_blank = [value for value in values if value != ""]

        is_binary = bool(non_blank) and all(is_binary_value(value) for value in non_blank)

        if is_binary:
            binary_counts[column.name] = {
                "0": sum(1 for value in non_blank if float(value) == 0.0),
                "1": sum(1 for value in non_blank if float(value) == 1.0),
            }
            continue

        if column.dtype in {"float", "integer"}:
            numeric_values = [float(value) for value in non_blank]
            if numeric_values:
                numeric_values.sort()
                q1 = quantile(numeric_values, 0.25)
                median = quantile(numeric_values, 0.5)
                q3 = quantile(numeric_values, 0.75)
                iqr = q3 - q1
                lower_fence = q1 - 1.5 * iqr
                upper_fence = q3 + 1.5 * iqr
                outlier_count = sum(1 for value in numeric_values if value < lower_fence or value > upper_fence)
                numeric_profiles[column.name] = NumericProfile(
                    minimum=numeric_values[0],
                    q1=q1,
                    median=median,
                    q3=q3,
                    maximum=numeric_values[-1],
                    outlier_count=outlier_count,
                )

    return TableProfile(
        row_count=len(rows),
        numeric_profiles=numeric_profiles,
        binary_counts=binary_counts,
    )


def render_schema_markdown() -> str:
    parts = ["# ExamplePipeline Table Schemas", ""]
    for table in TABLES:
        profile = profile_table(table)
        parts.extend(
            [
                f"## {table.display_title} ({table.file_name})",
                f"- Stage: {table.stage}",
                f"- Source path: `{table.source_path}`",
                f"- Summary: {table.summary}",
                f"- Row count: {profile.row_count}",
                "",
                "| Column | Type | Role | Description |",
                "| --- | --- | --- | --- |",
            ]
        )
        for column in table.columns:
            parts.append(f"| {column.name} | {column.dtype} | {infer_role(column)} | {column.description} |")

        parts.append("")
        parts.append("### Data Summary")
        if profile.numeric_profiles:
            parts.extend(
                [
                    "- Numeric profile:",
                    "",
                    "| Column | Min | Q1 | Median | Q3 | Max | Outliers |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for name, stats in profile.numeric_profiles.items():
                parts.append(
                    f"| {name} | {format_number(stats.minimum)} | {format_number(stats.q1)} | {format_number(stats.median)} | {format_number(stats.q3)} | {format_number(stats.maximum)} | {stats.outlier_count} |"
                )
        else:
            parts.append("- Numeric profile: none")

        parts.append("")
        if profile.binary_counts:
            parts.append("- Binary column counts:")
            for name, counts in profile.binary_counts.items():
                parts.append(f"  - `{name}`: 0={counts['0']}, 1={counts['1']}")
        else:
            parts.append("- Binary column counts: none")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def render_rows_for_schema(table: TableSpec) -> str:
    row_blocks = []
    for column in table.columns:
        row_blocks.append(
            "\n".join(
                [
                    "<tr>",
                    f"  <td>{html_escape(column.name)}</td>",
                    f"  <td>{html_escape(column.dtype)}</td>",
                    f"  <td>{html_escape(infer_role(column))}</td>",
                    f"  <td>{html_escape(column.description)}</td>",
                    "</tr>",
                ]
            )
        )
    return "\n".join(row_blocks)


def render_numeric_profile(profile: TableProfile) -> str:
    if not profile.numeric_profiles:
        return dedent(
            """\
            <section class="card">
              <h2>Numeric Profile</h2>
              <p class="note">No numeric columns were detected for this table.</p>
            </section>
            """
        ).strip()

    row_blocks = []
    plot_blocks = []
    for name, stats in profile.numeric_profiles.items():
        row_blocks.append(
            "\n".join(
                [
                    "<tr>",
                    f"  <td>{html_escape(name)}</td>",
                    f"  <td>{format_number(stats.minimum)}</td>",
                    f"  <td>{format_number(stats.q1)}</td>",
                    f"  <td>{format_number(stats.median)}</td>",
                    f"  <td>{format_number(stats.q3)}</td>",
                    f"  <td>{format_number(stats.maximum)}</td>",
                    f"  <td>{stats.outlier_count}</td>",
                    "</tr>",
                ]
            )
        )

        x_min = scale_to_axis(stats.minimum, stats.minimum, stats.maximum)
        x_q1 = scale_to_axis(stats.q1, stats.minimum, stats.maximum)
        x_median = scale_to_axis(stats.median, stats.minimum, stats.maximum)
        x_q3 = scale_to_axis(stats.q3, stats.minimum, stats.maximum)
        x_max = scale_to_axis(stats.maximum, stats.minimum, stats.maximum)

        plot_blocks.append(
            dedent(
                f"""\
                <article class="plot-wrap">
                  <h3 class="plot-title">{html_escape(name)}</h3>
                  <svg viewBox="0 0 1000 90" width="100%" height="90" role="img" aria-label="Box plot for {html_escape(name)}">
                    <line x1="40" y1="45" x2="960" y2="45" stroke="#aac0da" stroke-width="6" />
                    <line x1="{x_min:.1f}" y1="28" x2="{x_min:.1f}" y2="62" stroke="#3f6ea5" stroke-width="3" />
                    <line x1="{x_max:.1f}" y1="28" x2="{x_max:.1f}" y2="62" stroke="#3f6ea5" stroke-width="3" />
                    <rect x="{x_q1:.1f}" y="24" width="{max(x_q3 - x_q1, 2.0):.1f}" height="42" fill="#4e8ad0" fill-opacity="0.35" stroke="#1d5fa9" stroke-width="2" />
                    <line x1="{x_median:.1f}" y1="22" x2="{x_median:.1f}" y2="68" stroke="#e46e2e" stroke-width="4" />
                  </svg>
                  <p class="plot-meta">min: {format_number(stats.minimum)} | q1: {format_number(stats.q1)} | median: {format_number(stats.median)} | q3: {format_number(stats.q3)} | max: {format_number(stats.maximum)} | outliers (1.5 IQR): {stats.outlier_count}</p>
                </article>
                """
            ).strip()
        )

    return dedent(
        f"""\
        <section class="card">
          <h2>Numeric Profile</h2>
          <p class="note">Summary statistics use min, Q1, median, Q3, max, and outlier counts with the 1.5 IQR rule.</p>
          {chr(10).join(plot_blocks)}
          <div class="legend">
            <span><span class="swatch" style="background:#4e8ad0;"></span>Interquartile range (Q1-Q3)</span>
            <span><span class="swatch" style="background:#e46e2e;"></span>Median</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Column</th>
                <th>Min</th>
                <th>Q1</th>
                <th>Median</th>
                <th>Q3</th>
                <th>Max</th>
                <th>Outliers</th>
              </tr>
            </thead>
            <tbody>
{chr(10).join(row_blocks)}
            </tbody>
          </table>
        </section>
        """
    ).strip()


def render_binary_profile(profile: TableProfile) -> str:
    if not profile.binary_counts:
        return dedent(
            """\
            <section class="card">
              <h2>Binary Column Counts</h2>
              <p class="note">No binary (0/1) columns were detected for this table.</p>
            </section>
            """
        ).strip()

    row_blocks = []
    for name, counts in profile.binary_counts.items():
        row_blocks.append(
            "\n".join(
                [
                    "<tr>",
                    f"  <td>{html_escape(name)}</td>",
                    f"  <td>{counts['0']}</td>",
                    f"  <td>{counts['1']}</td>",
                    "</tr>",
                ]
            )
        )

    return dedent(
        f"""\
        <section class="card">
          <h2>Binary Column Counts</h2>
          <table>
            <thead>
              <tr>
                <th>Column</th>
                <th>Count of 0</th>
                <th>Count of 1</th>
              </tr>
            </thead>
            <tbody>
{chr(10).join(row_blocks)}
            </tbody>
          </table>
        </section>
        """
    ).strip()


def render_table_html(table: TableSpec) -> str:
    profile = profile_table(table)
    binary_label = "None detected" if not profile.binary_counts else ", ".join(profile.binary_counts.keys())

    return dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>{html_escape(table.display_title)}</title>
          <style>
            :root {{
              --bg: #f6f8fc;
              --surface: #ffffff;
              --surface-soft: #edf3fb;
              --text: #0f2238;
              --text-muted: #4b617a;
              --border: #cfdcec;
              --accent: #1d5fa9;
            }}

            body {{
              margin: 32px;
              font-family: "Avenir Next", "Segoe UI", "Noto Sans", sans-serif;
              color: var(--text);
              background:
                radial-gradient(circle at 8% 0%, #dfeafc 0%, transparent 33%),
                radial-gradient(circle at 100% 0%, #fcebdd 0%, transparent 30%),
                var(--bg);
              line-height: 1.6;
            }}

            a {{
              color: var(--accent);
              text-decoration: none;
            }}

            a:hover {{
              text-decoration: underline;
            }}

            .crumbs {{
              margin-bottom: 14px;
              font-weight: 600;
            }}

            h1 {{
              margin: 0;
              color: var(--accent);
              letter-spacing: 0.3px;
            }}

            .subtitle {{
              margin: 8px 0 0 0;
              color: var(--text-muted);
              font-size: 16px;
            }}

            .card {{
              margin-top: 18px;
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: 12px;
              box-shadow: 0 8px 20px rgba(15, 34, 56, 0.06);
              padding: 16px;
            }}

            .meta-grid {{
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
              gap: 10px;
              margin-top: 10px;
            }}

            .meta-item {{
              background: var(--surface-soft);
              border: 1px solid var(--border);
              border-radius: 10px;
              padding: 10px;
            }}

            .meta-item strong {{
              display: block;
              color: var(--accent);
              font-size: 12px;
              text-transform: uppercase;
              letter-spacing: 0.4px;
              margin-bottom: 4px;
            }}

            table {{
              width: 100%;
              border-collapse: collapse;
              margin-top: 10px;
            }}

            th,
            td {{
              border-bottom: 1px solid var(--border);
              padding: 10px 12px;
              text-align: left;
              vertical-align: top;
            }}

            th {{
              background: var(--surface-soft);
              color: var(--accent);
              font-size: 14px;
              text-transform: uppercase;
              letter-spacing: 0.3px;
            }}

            .note {{
              color: var(--text-muted);
              margin: 8px 0 0 0;
            }}

            .plot-wrap {{
              margin-top: 14px;
              border: 1px solid var(--border);
              border-radius: 10px;
              padding: 12px;
              background: #fbfdff;
            }}

            .plot-title {{
              margin: 0 0 8px 0;
              color: var(--accent);
              font-size: 16px;
              font-weight: 700;
            }}

            .plot-meta {{
              margin: 8px 0 0 0;
              color: var(--text-muted);
              font-size: 13px;
            }}

            .legend {{
              margin-top: 12px;
              font-size: 13px;
              color: var(--text-muted);
            }}

            .legend span {{
              display: inline-block;
              margin-right: 14px;
            }}

            .swatch {{
              display: inline-block;
              width: 12px;
              height: 12px;
              border-radius: 2px;
              margin-right: 5px;
              vertical-align: -2px;
            }}

            @media (max-width: 720px) {{
              body {{
                margin: 16px;
              }}

              .card {{
                padding: 12px;
              }}
            }}
          </style>
        </head>
        <body>
          <div class="crumbs"><a href="../index.html">Table index</a></div>

          <h1>{html_escape(table.display_title)}</h1>
          <p class="subtitle">Backing file: {html_escape(table.file_name)}</p>

          <section class="card">
            <p>{html_escape(table.summary)}</p>
            <div class="meta-grid">
              <div class="meta-item">
                <strong>Pipeline Stage</strong>
                {html_escape(table.stage)}
              </div>
              <div class="meta-item">
                <strong>Source Path</strong>
                {html_escape(table.source_path)}
              </div>
              <div class="meta-item">
                <strong>Row Count</strong>
                {profile.row_count}
              </div>
              <div class="meta-item">
                <strong>Binary Columns</strong>
                {html_escape(binary_label)}
              </div>
            </div>
          </section>

          <section class="card">
            <h2>Schema</h2>
            <table>
              <thead>
                <tr>
                  <th>Column</th>
                  <th>Type</th>
                  <th>Role</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
{render_rows_for_schema(table)}
              </tbody>
            </table>
          </section>

          {render_numeric_profile(profile)}
          {render_binary_profile(profile)}
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

    section_blocks = []
    for stage, tables in sections.items():
        list_items = []
        for table in tables:
            list_items.append(
                "\n".join(
                    [
                        "<li>",
                        f"  <a href=\"html/{html_escape(table.slug)}.html\">{html_escape(table.display_title)}</a> ({html_escape(table.file_name)})",
                        f"  - {html_escape(table.summary)}",
                        "</li>",
                    ]
                )
            )
        section_blocks.append(
            "\n".join(
                [
                    "<section>",
                    f"  <h2>{html_escape(stage)}</h2>",
                    "  <ul>",
                    "\n".join(list_items),
                    "  </ul>",
                    "</section>",
                ]
            )
        )

    return dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>ExamplePipeline Table Documentation</title>
          <style>
            :root {{
              --bg: #f2f5fb;
              --surface: #ffffff;
              --surface-tint: #edf3ff;
              --text: #11243b;
              --text-muted: #4c5f78;
              --border: #cfdbeb;
              --ink-strong: #194f92;
              --ink-accent: #2f76c9;
              --highlight: #ff7a59;
            }}

            body {{
              font-family: "Avenir Next", "Segoe UI", "Noto Sans", sans-serif;
              margin: 32px;
              color: var(--text);
              line-height: 1.6;
              background:
                radial-gradient(circle at 0% 0%, #e5efff 0%, transparent 38%),
                radial-gradient(circle at 95% 5%, #ffece7 0%, transparent 30%),
                var(--bg);
            }}

            h1 {{
              margin: 0 0 10px 0;
              color: var(--ink-strong);
              letter-spacing: 0.25px;
            }}

            .lead {{
              color: var(--text-muted);
              max-width: 900px;
              margin: 0 0 20px 0;
              font-size: 16px;
            }}

            section {{
              margin-top: 24px;
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: 12px;
              padding: 14px 16px;
              box-shadow: 0 6px 20px rgba(17, 36, 59, 0.06);
            }}

            h2 {{
              margin: 0;
              color: var(--ink-strong);
              font-size: 20px;
            }}

            ul {{
              margin: 12px 0 0 0;
              padding-left: 20px;
            }}

            li {{
              margin-bottom: 10px;
              color: var(--text);
            }}

            a {{
              color: var(--ink-accent);
              text-decoration: none;
              font-weight: 600;
            }}

            a:hover {{
              color: var(--ink-strong);
              text-decoration: underline;
              text-decoration-color: var(--highlight);
              text-underline-offset: 2px;
            }}

            .diagram-section p {{
              margin: 10px 0 14px 0;
              color: var(--text-muted);
            }}

            .diagram-frame {{
              width: 100%;
              min-height: 700px;
              border: 1px solid var(--border);
              border-radius: 10px;
              background: #ffffff;
            }}

            @media (max-width: 720px) {{
              body {{
                margin: 16px;
              }}

              section {{
                padding: 12px;
              }}
            }}
          </style>
        </head>
        <body>
          <h1>ExamplePipeline Table Documentation</h1>
          <p class="lead">Each page summarizes what the table captures and lists the schema below that summary. The pages are organized by pipeline stage so the ETL flow is easy to follow.</p>

          <section class="diagram-section">
            <h2>ETL Job Flow Diagram</h2>
            <p>The Mermaid ETL flow is embedded below from the shared diagram document.</p>
            <iframe class="diagram-frame" src="../diagrams/etl_job_flow.html" title="ExamplePipeline ETL Mermaid Diagram" loading="lazy"></iframe>
          </section>

          {chr(10).join(section_blocks)}
        </body>
        </html>
        """
    ).strip() + "\n"


def render_mermaid() -> str:
    return dedent(
        """\
        %%{init: {"theme": "base", "themeVariables": {"background": "#F4F8FF", "primaryColor": "#FFFFFF", "primaryTextColor": "#10243E", "primaryBorderColor": "#1D5FAF", "secondaryColor": "#EAF2FF", "secondaryTextColor": "#10243E", "secondaryBorderColor": "#2F7DD1", "tertiaryColor": "#FFE3DE", "tertiaryTextColor": "#10243E", "tertiaryBorderColor": "#F26A5A", "lineColor": "#2F7DD1", "fontFamily": "Avenir Next, Segoe UI, Noto Sans, sans-serif", "fontSize": "14px"}, "flowchart": {"curve": "basis", "htmlLabels": true}}}%%
        flowchart LR
          classDef raw fill:#DCEBFF,stroke:#1D5FAF,color:#10243E,stroke-width:1px;
          classDef job fill:#FFFFFF,stroke:#2F7DD1,color:#10243E,stroke-width:1.5px;
          classDef feature fill:#EAF2FF,stroke:#1D5FAF,color:#10243E,stroke-width:1.5px;
          classDef score fill:#FFE3DE,stroke:#F26A5A,color:#10243E,stroke-width:1.5px;
          classDef note fill:#F4F8FF,stroke:#CFE0F7,color:#4B607C,stroke-dasharray: 4 3;

          subgraph Raw["Raw source<br/>tables"]
            src_map["src_customer_device_map.csv"]:::raw
            src_modem["src_modem_signal.csv"]:::raw
            src_cmts["src_cmts_signal.csv"]:::raw
            src_router["src_router_signal.csv"]:::raw
            src_mtr["src_modem_mtr.csv"]:::raw
          end

          subgraph ETL["Interim ETL<br/>jobs"]
            j_modem["etl_modem_signal_from_notebook.py"]:::job
            j_cmts["etl_cmts_signal.py"]:::job
            j_router["etl_router_signal.py"]:::job
            j_mtr["etl_modem_mtr.py"]:::job
          end

          subgraph Join["Feature<br/>assembly"]
            j_features["etl_unified_features.py"]:::feature
            validation[stage3_join_validation.csv]:::note
          end

          subgraph Score["Inference<br/>scoring"]
            modelref["best_model_reference.json"]:::note
            j_score["score_stage3_features.py"]:::score
          end

          src_map --> j_modem
          src_modem --> j_modem
          j_modem --> trn_modem["trn_modem_signal.csv"]:::feature

          src_map --> j_cmts
          src_cmts --> j_cmts
          j_cmts --> trn_cmts["trn_cmts_signal.csv"]:::feature

          src_map --> j_router
          src_router --> j_router
          j_router --> trn_router["trn_router_signal.csv"]:::feature

          src_map --> j_mtr
          src_mtr --> j_mtr
          j_mtr --> trn_mtr["trn_modem_mtr.csv"]:::feature

          trn_modem --> j_features
          trn_cmts --> j_features
          trn_router --> j_features
          trn_mtr --> j_features
          j_features --> features["features_unified.csv"]:::feature
          j_features --> validation

          features --> j_score
          modelref --> j_score
          j_score --> scored["predictions_v1.csv"]:::score

          linkStyle default stroke:#2F7DD1,stroke-width:1.5px;
        """
    ).strip() + "\n"


def write_outputs() -> None:
    SCHEMA_MD.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHED_TABLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)

    SCHEMA_MD.write_text(render_schema_markdown(), encoding="utf-8")
    INDEX_HTML.write_text(render_index_html(), encoding="utf-8")
    MERMAID_MD.write_text(render_mermaid(), encoding="utf-8")

    for table in TABLES:
        (HTML_DIR / f"{table.slug}.html").write_text(render_table_html(table), encoding="utf-8")


if __name__ == "__main__":
    write_outputs()