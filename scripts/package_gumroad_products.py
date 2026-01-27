#!/usr/bin/env python3
"""Package Gumroad-ready zips for all Node-Null products.

Creates three zip variants per product:
  - personal
  - team
  - commercial

Each zip:
  - includes product README + templates
  - includes a run scaffold (run.json + .gitkeep files only)
  - includes the tier-specific license as products/<product>/licenses/<...> and as top-level LICENSE.txt
  - includes required tooling for products that ship builders (e.g., hook_performance_index)

Safety rules:
  - excludes build/ dist/ .git/
  - excludes runs/**/inputs/* (except .gitkeep) to avoid shipping real data
  - excludes runs/**/outputs/* (except .gitkeep)

Usage:
  python scripts/package_gumroad_products.py
  python scripts/package_gumroad_products.py --product hook_performance_index
  python scripts/package_gumroad_products.py --out-dir dist/gumroad
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set

TIERS: Sequence[str] = ("personal", "team", "commercial")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur] + list(cur.parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_version_from_readme(readme_text: str) -> str:
    # Expected: "# Name v01" on the first line.
    first_line = (readme_text.splitlines() or [""])[0]
    m = re.search(r"\bv(\d{2})\b", first_line)
    if not m:
        return "v01"
    return f"v{m.group(1)}"


def safe_rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def iter_glob_files(repo_root: Path, pattern: str) -> Iterable[Path]:
    # pattern is relative posix
    base = repo_root
    for p in base.glob(pattern):
        if p.is_file():
            yield p


def iter_rglob_files(folder: Path) -> Iterable[Path]:
    for p in folder.rglob("*"):
        if p.is_file():
            yield p


def should_exclude(rel_posix: str) -> bool:
    if rel_posix.startswith(("build/", "dist/", ".git/")):
        return True

    # Exclude run inputs/outputs except the keep files.
    if "/runs/" in rel_posix:
        if "/inputs/" in rel_posix and not rel_posix.endswith("/inputs/.gitkeep"):
            return True
        if "/outputs/" in rel_posix and not rel_posix.endswith("/outputs/.gitkeep"):
            return True

    return False


def add_file(z: zipfile.ZipFile, repo_root: Path, path: Path, *, included: Set[str]) -> None:
    rel = safe_rel(repo_root, path)
    if should_exclude(rel):
        return
    if rel in included:
        return
    z.write(path, arcname=rel)
    included.add(rel)


def add_folder_tree(z: zipfile.ZipFile, repo_root: Path, folder: Path, *, included: Set[str]) -> None:
    for p in iter_rglob_files(folder):
        add_file(z, repo_root, p, included=included)


@dataclass(frozen=True)
class ProductConfig:
    name: str  # folder name under products/
    extra_files: Sequence[str]
    fixture_allowlist: Sequence[str]


def default_products() -> List[ProductConfig]:
    return [
        ProductConfig(
            name="weekly_signal_brief",
            extra_files=(
                # Tooling used for aggregation/build (optional but useful for buyers).
                "scripts/build_weekly_signal_brief.py",
                "scripts/aggregate_weekly_inputs.py",
                "scripts/requirements.txt",
                "artifacts/manifest.schema.json",
                "analytics/schema.md",
                "monetization/assets/validation.md",
                "monetization/assets/registry.md",
            ),
            # Include the synthetic fixture only (safe to ship)
            fixture_allowlist=(
                "products/weekly_signal_brief/runs/2099-W01-fixture/run.json",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/posts_export.csv",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/decisions.csv",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/hooks_rollup.csv",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/verticals_rollup.csv",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/dataset_health.json",
                "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/template_context.json",
                "products/weekly_signal_brief/runs/2099-W01-fixture/outputs/.gitkeep",
            ),
        ),
        ProductConfig(
            name="hook_performance_index",
            extra_files=(
                "scripts/build_hook_performance_index.py",
                "scripts/aggregate_weekly_inputs.py",
                "scripts/requirements.txt",
                "artifacts/manifest.schema.json",
                "monetization/assets/registry.md",
            ),
            fixture_allowlist=(),
        ),
        ProductConfig(name="pattern_engine_report", extra_files=(), fixture_allowlist=()),
        ProductConfig(name="vertical_performance_index", extra_files=(), fixture_allowlist=()),
        ProductConfig(name="signal_dashboard", extra_files=(), fixture_allowlist=()),
        ProductConfig(name="attention_mechanics_report", extra_files=(), fixture_allowlist=()),
        ProductConfig(name="content_template_pack", extra_files=(), fixture_allowlist=()),
    ]


def license_path(product: str, tier: str, version: str) -> str:
    if tier not in TIERS:
        raise ValueError(f"Invalid tier: {tier}")
    return f"products/{product}/licenses/LICENSE_{tier}_{version}.txt"


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        default="dist/gumroad",
        help="Output directory under repo root (default: dist/gumroad)",
    )
    ap.add_argument(
        "--product",
        default=None,
        help="Optional product folder name (e.g., hook_performance_index). If omitted, packages all.",
    )
    ap.add_argument(
        "--tiers",
        default=",".join(TIERS),
        help="Comma-separated tiers to build (default: personal,team,commercial)",
    )
    args = ap.parse_args(argv)

    repo_root = find_repo_root(Path(__file__).parent)
    out_dir = (repo_root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Hygiene: keep outputs under dist/
    try:
        out_rel = out_dir.relative_to(repo_root).as_posix()
    except Exception:
        raise SystemExit("--out-dir must be inside the repo")
    if not out_rel.startswith("dist/"):
        raise SystemExit("--out-dir must be under dist/")

    tiers = [t.strip() for t in args.tiers.split(",") if t.strip()]
    for t in tiers:
        if t not in TIERS:
            raise SystemExit(f"Unknown tier '{t}'. Expected: {', '.join(TIERS)}")

    products = default_products()
    if args.product:
        products = [p for p in products if p.name == args.product]
        if not products:
            raise SystemExit(f"Unknown product '{args.product}'.")

    wrote: List[str] = []

    for p in products:
        product_root = repo_root / "products" / p.name
        readme_path = product_root / "README.md"
        if not readme_path.exists():
            raise SystemExit(f"Missing README: products/{p.name}/README.md")

        version = parse_version_from_readme(_read_text(readme_path))

        # Base inclusions for every product.
        base_paths: List[Path] = []
        base_paths.append(readme_path)

        templates_dir = product_root / "templates"
        if templates_dir.exists():
            base_paths.append(templates_dir)

        # Run scaffold: run.json + keep files.
        for run_json in iter_glob_files(repo_root, f"products/{p.name}/runs/**/run.json"):
            base_paths.append(run_json)
        for keep in iter_glob_files(repo_root, f"products/{p.name}/runs/**/inputs/.gitkeep"):
            base_paths.append(keep)
        for keep in iter_glob_files(repo_root, f"products/{p.name}/runs/**/outputs/.gitkeep"):
            base_paths.append(keep)

        # Product-specific extras.
        for rel in p.extra_files:
            extra_path = repo_root / rel
            if not extra_path.exists():
                raise SystemExit(f"Missing extra file: {rel}")
            base_paths.append(extra_path)

        # Product-specific fixture files (explicit allowlist). These may include "inputs".
        fixture_paths: List[Path] = []
        for rel in p.fixture_allowlist:
            fp = repo_root / rel
            if not fp.exists():
                raise SystemExit(f"Missing fixture allowlist file: {rel}")
            fixture_paths.append(fp)

        for tier in tiers:
            lic_rel = license_path(p.name, tier, version)
            lic_path = repo_root / lic_rel
            if not lic_path.exists():
                raise SystemExit(
                    f"Missing license for {p.name} ({tier}): {lic_rel}. "
                    "Create products/<product>/licenses/LICENSE_<tier>_<version>.txt"
                )
            lic_text = _read_text(lic_path)

            # Zip naming: product_folder__vXX__tier.zip
            zip_name = f"{p.name}__{version}__{tier}.zip"
            zip_path = out_dir / p.name / zip_name
            zip_path.parent.mkdir(parents=True, exist_ok=True)

            included: Set[str] = set()
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
                for item in base_paths:
                    if item.is_dir():
                        add_folder_tree(z, repo_root, item, included=included)
                    else:
                        add_file(z, repo_root, item, included=included)

                # Always include the selected tier license file in its repo path.
                add_file(z, repo_root, lic_path, included=included)

                # Also include a convenient top-level LICENSE.txt.
                z.writestr("LICENSE.txt", lic_text)

                # Fixture files (explicitly allowlisted) come last and bypass the generic run input exclusion.
                for fp in fixture_paths:
                    rel = safe_rel(repo_root, fp)
                    if rel in included:
                        continue
                    z.write(fp, arcname=rel)
                    included.add(rel)

            wrote.append(zip_path.relative_to(repo_root).as_posix())

    for w in wrote:
        print(f"Wrote: {w}")
    print(f"Done. ({len(wrote)} zips)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
