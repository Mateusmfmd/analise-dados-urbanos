from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from urban_analysis.analysis import (  # noqa: E402
    aggregate_by_zone,
    load_records,
    render_report,
    write_bar_chart_svg,
    write_summary_csv,
)


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data_path = ROOT / "data" / "amostra_dados_urbanos.csv"
        self.records = load_records(self.data_path)

    def test_sample_is_explicit_and_has_expected_size(self) -> None:
        self.assertEqual(len(self.records), 6)
        self.assertTrue(all(record["is_sample"] is True for record in self.records))
        self.assertTrue(all(record["source"] == "amostra_sintetica" for record in self.records))

    def test_aggregate_by_zone_is_sorted_and_deterministic(self) -> None:
        summary = aggregate_by_zone(self.records)
        self.assertEqual([row["zone"] for row in summary], ["Centro", "Zona Norte", "Zona Sul"])
        centro = summary[0]
        self.assertEqual(centro["records"], 2)
        self.assertEqual(centro["residents_total"], 2430)
        self.assertEqual(centro["green_area_m2_avg"], 2400.0)
        self.assertEqual(centro["traffic_index_avg"], 63.5)
        self.assertEqual(centro["occupancy_rate_avg"], 0.79)

    def test_outputs_are_written_without_external_packages(self) -> None:
        summary = aggregate_by_zone(self.records)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            summary_path = directory / "summary.csv"
            svg_path = directory / "chart.svg"
            write_summary_csv(summary, summary_path)
            write_bar_chart_svg(summary, "residents_total", "Teste", svg_path)
            report = directory / "report.html"
            report.write_text(render_report(summary), encoding="utf-8")

            self.assertTrue(summary_path.exists())
            self.assertIn("Centro", summary_path.read_text(encoding="utf-8"))
            svg_text = svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg_text)
            self.assertIn("role=\"img\"", svg_text)
            html_text = report.read_text(encoding="utf-8")
            self.assertIn("Amostra, não dado real", html_text)
            with summary_path.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 3)


if __name__ == "__main__":
    unittest.main()
