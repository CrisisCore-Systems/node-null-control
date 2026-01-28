#!/usr/bin/env python3
"""Release build runner for product artifacts.

This is intentionally separate from the CI smoke runner:
- Smoke builds default to deterministic + dependency-light placeholders.
- Release builds can opt into heavier tooling (e.g., wkhtmltopdf) and
  additional deliverables (e.g., dashboard webapp zip).

Usage examples:
  python scripts/release_products.py --pdf-adapter wkhtmltopdf
  python scripts/release_products.py --pdf-adapter command --pdf-cmd "wkhtmltopdf {html} {pdf}"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RunInfo:
    product: str
    run_id: str
    run_json: Path


def iter_run_json(repo_root: Path) -> Iterable[RunInfo]:
    products_dir = repo_root / "products"
    for run_json in sorted(products_dir.glob("*/runs/*/run.json")):
        try:
            product = run_json.parents[2].name
            run_id = run_json.parent.name
        except Exception:  # noqa: BLE001
            continue
        yield RunInfo(product=product, run_id=run_id, run_json=run_json)


def is_fixture_run(info: RunInfo) -> bool:
    return "fixture" in info.run_id.lower()


def _run(argv: list[str], cwd: Path) -> None:
    subprocess.run(argv, cwd=str(cwd), check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release build products")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to node-null-control repo root (defaults to auto-detect from this script location)",
    )
    parser.add_argument(
        "--out-root",
        default=None,
        help="Root output directory (default: build/release under repo root)",
    )
    parser.add_argument(
        "--include-non-fixture",
        action="store_true",
        help="Also run non-fixture runs (not recommended unless inputs are real).",
    )
    parser.add_argument(
        "--pdf-adapter",
        choices=["none", "wkhtmltopdf", "command"],
        default="none",
        help="PDF generator adapter for release builds.",
    )
    parser.add_argument(
        "--pdf-cmd",
        default=None,
        help="Command template for --pdf-adapter=command. Use {html} and {pdf} placeholders.",
    )
    parser.add_argument(
        "--bundle-dashboard-webapp",
        action="store_true",
        help="Also build the Signal Dashboard webapp zip deliverable.",
    )

    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root).resolve() if args.out_root else (repo_root / "build" / "release")
    out_root.mkdir(parents=True, exist_ok=True)

    # Keep this explicit: release should be boring and predictable.
    builders: dict[str, list[str]] = {
        "weekly_signal_brief": [
            sys.executable,
            "scripts/build_weekly_signal_brief.py",
            "--run",
            "{run_json}",
            "--outdir",
            "{out_dir}",
            "--strict-csv-headers",
            "--strict-context",
            "--pdf-adapter",
            args.pdf_adapter,
        ],
        "hook_performance_index": [
            sys.executable,
            "scripts/build_hook_performance_index.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
            "--fail-on-unresolved",
        ],
        "attention_mechanics_report": [
            sys.executable,
            "scripts/build_attention_mechanics_report.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
            "--fail-on-unresolved",
            "--pdf-adapter",
            args.pdf_adapter,
        ],
        "pattern_engine_report": [
            sys.executable,
            "scripts/build_pattern_engine_report.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
            "--fail-on-unresolved",
            "--pdf-adapter",
            args.pdf_adapter,
        ],
        "vertical_performance_index": [
            sys.executable,
            "scripts/build_vertical_performance_index.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
            "--validate-schema",
        ],
        "signal_dashboard": [
            sys.executable,
            "scripts/build_signal_dashboard.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
        ],
        "content_template_pack": [
            sys.executable,
            "scripts/build_content_template_pack.py",
            "--run-json",
            "{run_json}",
            "--out-dir",
            "{out_dir}",
            "--pdf-adapter",
            args.pdf_adapter,
        ],
    }

    if args.pdf_adapter == "command":
        if not args.pdf_cmd:
            print("ERROR: --pdf-cmd is required when --pdf-adapter=command", file=sys.stderr)
            return 2
        for product in [
            "weekly_signal_brief",
            "attention_mechanics_report",
            "pattern_engine_report",
            "content_template_pack",
        ]:
            builders[product].extend(["--pdf-cmd", args.pdf_cmd])

    if args.bundle_dashboard_webapp:
        builders["signal_dashboard"].append("--bundle-webapp")

    runs = list(iter_run_json(repo_root))
    if not runs:
        print("No run.json files found under products/*/runs/*/run.json")
        return 2

    built = 0
    for info in runs:
        if info.product not in builders:
            continue
        if not args.include_non_fixture and not is_fixture_run(info):
            continue

        out_dir = out_root / info.product / info.run_id
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            a.format(
                run_json=str(info.run_json),
                out_dir=str(out_dir),
            )
            for a in builders[info.product]
        ]
        print(f"[release] {info.product}/{info.run_id}")
        _run(cmd, cwd=repo_root)
        built += 1

    print(f"Release builds complete: {built} run(s) -> {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
