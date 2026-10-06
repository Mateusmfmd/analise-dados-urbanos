"""Pipeline determinístico e sem dependências para a amostra urbana.

O módulo não tenta inferir propriedades de uma população. Ele apenas valida,
agrega e renderiza o conteúdo fornecido pelo usuário.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Iterable, Mapping

REQUIRED_COLUMNS = {
    "zone",
    "month",
    "residents",
    "green_area_m2",
    "traffic_index",
    "occupancy_rate",
    "is_sample",
    "source",
}
NUMERIC_COLUMNS = ("residents", "green_area_m2", "traffic_index", "occupancy_rate")


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "t", "yes", "sim"}


def load_records(csv_path: str | Path) -> list[dict[str, object]]:
    """Lê e valida o CSV, convertendo as métricas para números Python."""
    path = Path(csv_path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")

        records: list[dict[str, object]] = []
        for line_number, raw in enumerate(reader, start=2):
            if not raw.get("zone", "").strip():
                raise ValueError(f"Linha {line_number}: zone não pode ser vazia")
            record: dict[str, object] = dict(raw)
            try:
                record["residents"] = int(str(raw["residents"]))
                record["green_area_m2"] = float(str(raw["green_area_m2"]))
                record["traffic_index"] = float(str(raw["traffic_index"]))
                record["occupancy_rate"] = float(str(raw["occupancy_rate"]))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Linha {line_number}: métrica numérica inválida") from exc
            record["zone"] = str(raw["zone"]).strip()
            record["month"] = str(raw["month"]).strip()
            record["is_sample"] = _as_bool(str(raw["is_sample"]))
            record["source"] = str(raw["source"]).strip()
            records.append(record)

    if not records:
        raise ValueError("O CSV não contém registros")
    return records


def aggregate_by_zone(records: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Calcula agregados descritivos por zona, em ordem estável."""
    groups: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        zone = str(record["zone"])
        groups.setdefault(zone, []).append(record)

    if not groups:
        raise ValueError("Não há registros para agregar")

    summary: list[dict[str, object]] = []
    for zone in sorted(groups):
        rows = groups[zone]
        summary.append(
            {
                "zone": zone,
                "records": len(rows),
                "residents_total": sum(int(row["residents"]) for row in rows),
                "green_area_m2_avg": round(
                    sum(float(row["green_area_m2"]) for row in rows) / len(rows), 2
                ),
                "traffic_index_avg": round(
                    sum(float(row["traffic_index"]) for row in rows) / len(rows), 2
                ),
                "occupancy_rate_avg": round(
                    sum(float(row["occupancy_rate"]) for row in rows) / len(rows), 4
                ),
            }
        )
    return summary


def write_summary_csv(summary: Iterable[Mapping[str, object]], output_path: str | Path) -> None:
    """Grava os agregados com cabeçalho e separador CSV padrão."""
    rows = list(summary)
    fields = [
        "zone",
        "records",
        "residents_total",
        "green_area_m2_avg",
        "traffic_index_avg",
        "occupancy_rate_avg",
    ]
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)


def write_bar_chart_svg(
    summary: Iterable[Mapping[str, object]],
    value_key: str,
    title: str,
    output_path: str | Path,
    *,
    value_suffix: str = "",
) -> None:
    """Renderiza um gráfico de barras horizontal simples, sem biblioteca gráfica."""
    rows = list(summary)
    if not rows:
        raise ValueError("Não há dados para o gráfico")
    values = [float(row[value_key]) for row in rows]
    maximum = max(values) or 1.0
    width, left, right = 760, 180, 30
    row_height, top, bottom = 38, 64, 28
    height = top + row_height * len(rows) + bottom
    plot_width = width - left - right
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.title{font-size:18px;font-weight:700}.label{font-size:13px}.value{font-size:12px;font-weight:700}.grid{stroke:#d1d5db;stroke-width:1}.bar{fill:#2563eb}</style>',
        f'<text id="chart-title" class="title" x="{left}" y="28">{html.escape(title)}</text>',
        f'<line class="grid" x1="{left}" y1="{top - 8}" x2="{left}" y2="{height - bottom}" />',
    ]
    for index, (row, value) in enumerate(zip(rows, values)):
        y = top + index * row_height
        label = html.escape(str(row["zone"]))
        bar_width = max(0.0, plot_width * value / maximum)
        shown = f"{value:g}{value_suffix}"
        svg.extend(
            [
                f'<text class="label" x="{left - 12}" y="{y + 17}" text-anchor="end">{label}</text>',
                f'<rect class="bar" x="{left}" y="{y + 3}" width="{bar_width:.2f}" height="22" rx="3" />',
                f'<text class="value" x="{left + bar_width + 8:.2f}" y="{y + 19}">{html.escape(shown)}</text>',
            ]
        )
    svg.append("</svg>\n")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(svg), encoding="utf-8")


def render_report(summary: Iterable[Mapping[str, object]]) -> str:
    """Retorna HTML estático do relatório; os links assumem a pasta outputs/."""
    rows = list(summary)
    table_rows = "\n".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row[field]))}</td>"
            for field in (
                "zone",
                "records",
                "residents_total",
                "green_area_m2_avg",
                "traffic_index_avg",
                "occupancy_rate_avg",
            )
        )
        + "</tr>"
        for row in rows
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatório de análise urbana — amostra</title>
  <style>
    body{{font-family:Arial,sans-serif;line-height:1.5;color:#172033;background:#f8fafc;max-width:1020px;margin:0 auto;padding:2rem}}
    h1,h2{{color:#0f172a}} .notice{{background:#fff7ed;border-left:5px solid #ea580c;padding:1rem}}
    .card{{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:1rem;margin:1rem 0;overflow-x:auto}}
    img{{max-width:100%;height:auto}} table{{border-collapse:collapse;width:100%}}
    th,td{{border:1px solid #cbd5e1;padding:.55rem;text-align:right}} th:first-child,td:first-child{{text-align:left}}
    th{{background:#e2e8f0}} code{{background:#e2e8f0;padding:.1rem .25rem}}
  </style>
</head>
<body>
  <h1>Relatório de análise urbana</h1>
  <p><strong>Execução offline e reproduzível.</strong> O conteúdo abaixo é calculado exclusivamente do arquivo <code>data/amostra_dados_urbanos.csv</code>.</p>
  <p class="notice"><strong>Amostra, não dado real:</strong> esta é uma amostra sintética, pequena e não oficial. As métricas são descritivas do exemplo de software e não permitem conclusões sobre uma cidade, população ou período reais.</p>
  <h2>Resumo por zona</h2>
  <div class="card">
    <table>
      <thead><tr><th>Zona</th><th>Registros</th><th>Residentes (total)</th><th>Área verde (m², média)</th><th>Índice de trânsito (média)</th><th>Ocupação (média)</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
  <h2>Gráficos</h2>
  <div class="card"><h3>Residentes totais por zona</h3><img src="grafico_residentes.svg" alt="Barras horizontais de residentes totais por zona"></div>
  <div class="card"><h3>Índice médio de trânsito por zona</h3><img src="grafico_transito.svg" alt="Barras horizontais do índice médio de trânsito por zona"></div>
  <h2>Metodologia e limitações</h2>
  <p>A leitura, agregação e renderização usam apenas a biblioteca padrão do Python. Consulte <a href="../metodologia.md">metodologia.md</a>, <a href="../limitacoes.md">limitacoes.md</a> e o <a href="summary.csv">CSV de resumo</a>. O campo <code>is_sample=true</code> do arquivo de entrada mantém explícito o escopo ilustrativo.</p>
</body>
</html>
"""


def run(input_path: str | Path, output_dir: str | Path, report_path: str | Path) -> list[dict[str, object]]:
    """Executa o pipeline completo e retorna o resumo gerado."""
    records = load_records(input_path)
    summary = aggregate_by_zone(records)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write_summary_csv(summary, output / "summary.csv")
    write_bar_chart_svg(summary, "residents_total", "Residentes totais por zona", output / "grafico_residentes.svg")
    write_bar_chart_svg(summary, "traffic_index_avg", "Índice médio de trânsito por zona", output / "grafico_transito.svg")
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_report(summary), encoding="utf-8")
    return summary
