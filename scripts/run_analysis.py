#!/usr/bin/env python3
"""Executa a análise da amostra e gera artefatos estáticos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from urban_analysis.analysis import run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "amostra_dados_urbanos.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--report", type=Path, default=ROOT / "outputs" / "relatorio.html")
    args = parser.parse_args()

    summary = run(args.input, args.output_dir, args.report)
    print(f"Gerados {len(summary)} agregados em {args.output_dir}")
    print(f"Relatório: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
