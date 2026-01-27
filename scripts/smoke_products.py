from __future__ import annotations

import argparse
import json
import shutil
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


BUILDERS: dict[str, list[str]] = {
    # argv template; {run_json} and {out_dir} expanded.
    "weekly_signal_brief": [
        "{python}",
        "scripts/build_weekly_signal_brief.py",
        "--run",
        "{run_json}",
        "--outdir",
        "{out_dir}",
        "--strict-csv-headers",
        "--pdf-adapter",
        "none",
    ],
    "hook_performance_index": [
        "{python}",
        "scripts/build_hook_performance_index.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
        "--fail-on-unresolved",
    ],
    "attention_mechanics_report": [
        "{python}",
        "scripts/build_attention_mechanics_report.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
        "--fail-on-unresolved",
    ],
    "pattern_engine_report": [
        "{python}",
        "scripts/build_pattern_engine_report.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
        "--fail-on-unresolved",
    ],
    "vertical_performance_index": [
        "{python}",
        "scripts/build_vertical_performance_index.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
        "--validate-schema",
    ],
    "signal_dashboard": [
        "{python}",
        "scripts/build_signal_dashboard.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
    ],
    "content_template_pack": [
        "{python}",
        "scripts/build_content_template_pack.py",
        "--run-json",
        "{run_json}",
        "--out-dir",
        "{out_dir}",
    ],
}


FIXTURE_ONLY_PRODUCTS: set[str] = {
    # These products have placeholder (non-fixture) runs that intentionally lack real inputs.
    # We only enforce the builders on fixture runs for CI stability.
    "attention_mechanics_report",
    "pattern_engine_report",
    "vertical_performance_index",
    "signal_dashboard",
    "content_template_pack",
}


def is_fixture_run(info: RunInfo) -> bool:
    return "fixture" in info.run_id.lower()


def iter_run_json(repo_root: Path) -> Iterable[RunInfo]:
    products_dir = repo_root / "products"
    for run_json in sorted(products_dir.glob("*/runs/*/run.json")):
        # products/<product>/runs/<run_id>/run.json
        try:
            product = run_json.parents[2].name
            run_id = run_json.parent.name
        except Exception:  # noqa: BLE001
            continue
        yield RunInfo(product=product, run_id=run_id, run_json=run_json)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_safe_relative_path(p: str) -> bool:
    try:
        path = Path(p)
    except Exception:  # noqa: BLE001
        return False

    if path.is_absolute():
        return False

    # Disallow parent traversal
    if ".." in path.parts:
        return False

    return True


def _validate_run_structure(run: dict, run_json: Path) -> list[str]:
    errors: list[str] = []

    if not isinstance(run, dict):
        return [f"{run_json}: run.json must be an object"]

    asset_id = run.get("asset_id")
    asset_version = run.get("asset_version")
    if not isinstance(asset_id, str) or not asset_id.strip():
        errors.append(f"{run_json}: missing/invalid asset_id")
    if not isinstance(asset_version, str) or not asset_version.strip():
        errors.append(f"{run_json}: missing/invalid asset_version")

    if not (isinstance(run.get("week_id"), str) and run.get("week_id")) and not (
        isinstance(run.get("period_id"), str) and run.get("period_id")
    ):
        errors.append(f"{run_json}: expected week_id or period_id")

    inputs = run.get("inputs")
    if inputs is not None and not isinstance(inputs, dict):
        errors.append(f"{run_json}: inputs must be an object when present")

    outputs = run.get("outputs")
    if outputs is not None and not isinstance(outputs, dict):
        errors.append(f"{run_json}: outputs must be an object when present")

    files = (inputs or {}).get("files") if isinstance(inputs, dict) else None
    if files is not None and not isinstance(files, dict):
        errors.append(f"{run_json}: inputs.files must be an object when present")

    # Validate paths are safe + scoped
    if isinstance(files, dict):
        for key, rel in files.items():
            if not isinstance(rel, str) or not rel.strip():
                errors.append(f"{run_json}: inputs.files.{key} must be a non-empty string")
                continue
            if not is_safe_relative_path(rel):
                errors.append(f"{run_json}: inputs.files.{key} must be a safe relative path: {rel}")
                continue
            if not Path(rel).as_posix().startswith("inputs/"):
                errors.append(f"{run_json}: inputs.files.{key} should live under inputs/: {rel}")

    if isinstance(outputs, dict):
        for key, rel in outputs.items():
            if not isinstance(rel, str) or not rel.strip():
                errors.append(f"{run_json}: outputs.{key} must be a non-empty string")
                continue
            if not is_safe_relative_path(rel):
                errors.append(f"{run_json}: outputs.{key} must be a safe relative path: {rel}")
                continue
            if not Path(rel).as_posix().startswith("outputs/"):
                errors.append(f"{run_json}: outputs.{key} should live under outputs/: {rel}")

    return errors


def _resolve_inputs(run: dict, run_json: Path) -> dict[str, Path]:
    run_dir = run_json.parent
    files = ((run.get("inputs") or {}).get("files") or {}) if isinstance(run.get("inputs"), dict) else {}
    if not isinstance(files, dict):
        return {}
    resolved: dict[str, Path] = {}
    for k, v in files.items():
        if isinstance(v, str) and v.strip():
            resolved[k] = (run_dir / v).resolve()
    return resolved


def run_builder(repo_root: Path, info: RunInfo, out_dir: Path) -> None:
    argv_template = BUILDERS[info.product]
    argv = [
        a.format(
            python=sys.executable,
            run_json=str(info.run_json),
            out_dir=str(out_dir),
        )
        for a in argv_template
    ]
    subprocess.run(argv, cwd=str(repo_root), check=True)


def run_weekly_strict_fixture(repo_root: Path, info: RunInfo, out_dir: Path) -> None:
    argv = [
        sys.executable,
        "scripts/build_weekly_signal_brief.py",
        "--run",
        str(info.run_json),
        "--outdir",
        str(out_dir),
        "--strict-csv-headers",
        "--strict-context",
        "--fail-on-unresolved",
        "--pdf-adapter",
        "none",
    ]
    subprocess.run(argv, cwd=str(repo_root), check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke test product runs")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to repo root (defaults to auto-detect from this script location)",
    )
    parser.add_argument(
        "--strict-missing-inputs",
        action="store_true",
        help="Fail if any run.json references missing inputs, even for products without a builder.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep smoke build outputs under build/smoke instead of deleting them.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    smoke_root = repo_root / "build" / "smoke"

    errors: list[str] = []
    warnings: list[str] = []

    runs = list(iter_run_json(repo_root))
    if not runs:
        print("No run.json files found under products/*/runs/*/run.json")
        return 0

    for info in runs:
        run = read_json(info.run_json)
        errors.extend(_validate_run_structure(run, info.run_json))

        product_dir = repo_root / "products" / info.product
        if not (product_dir / "templates").exists():
            warnings.append(f"{info.run_json}: missing templates/ directory for product {info.product}")

        resolved_inputs = _resolve_inputs(run, info.run_json)

        should_build = info.product in BUILDERS and (info.product not in FIXTURE_ONLY_PRODUCTS or is_fixture_run(info))

        if should_build:
            missing = [f"{k} -> {p}" for k, p in resolved_inputs.items() if not p.exists()]
            if missing:
                errors.append(f"{info.run_json}: missing required builder inputs: {', '.join(missing)}")
                continue

            out_dir = smoke_root / info.product / info.run_id
            if out_dir.exists():
                shutil.rmtree(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            try:
                run_builder(repo_root, info, out_dir=out_dir)
            except subprocess.CalledProcessError as exc:
                errors.append(f"{info.run_json}: build failed (exit {exc.returncode})")
                continue

            # Extra enforcement: fixture runs should be fully strict.
            if info.product == "weekly_signal_brief" and is_fixture_run(info):
                strict_dir = smoke_root / info.product / f"{info.run_id}__strict"
                if strict_dir.exists():
                    shutil.rmtree(strict_dir)
                strict_dir.mkdir(parents=True, exist_ok=True)
                try:
                    run_weekly_strict_fixture(repo_root, info, out_dir=strict_dir)
                except subprocess.CalledProcessError as exc:
                    errors.append(f"{info.run_json}: strict fixture build failed (exit {exc.returncode})")
                    continue
                finally:
                    if strict_dir.exists() and not args.keep:
                        shutil.rmtree(strict_dir, ignore_errors=True)

            # Expect the builder to produce *something*.
            produced = [p for p in out_dir.rglob("*") if p.is_file()]
            if not produced:
                errors.append(f"{info.run_json}: builder produced no files in {out_dir}")

            if not args.keep:
                shutil.rmtree(out_dir, ignore_errors=True)
        else:
            # For template-only products, allow placeholder inputs by default.
            if info.product in FIXTURE_ONLY_PRODUCTS and not is_fixture_run(info):
                continue

            missing_inputs = [f"{k} -> {p}" for k, p in resolved_inputs.items() if not p.exists()]
            if missing_inputs:
                msg = f"{info.run_json}: referenced inputs not present yet: {', '.join(missing_inputs)}"
                if args.strict_missing_inputs:
                    errors.append(msg)
                else:
                    warnings.append(msg)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")

    if errors:
        print("Errors:")
        for e in errors:
            print(f"- {e}")
        return 2

    print("OK: product smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
