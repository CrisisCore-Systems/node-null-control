#!/usr/bin/env python3
"""Package the Weekly Signal Brief (Model B) Core kit for distribution.

This creates a single zip containing:
- Builder + low-infra aggregator scripts
- Templates + variable allowlist + appendix schema
- Artifact manifest schema
- Minimal referenced docs (analytics schema + monetization validation + asset registry)
- A synthetic fixture run (2099-W01-fixture) for deterministic verification

It intentionally EXCLUDES:
- Any real run data (e.g., products/weekly_signal_brief/runs/2026-W04)
- Any generated artifacts under build/ or dist/
- Any git history

Usage:
  python scripts/package_weekly_signal_brief_kit.py \
    --out dist/gumroad/weekly_signal_brief_core_kit_v01.zip

"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional


BASE_ALLOWLIST: List[str] = [
    # Core docs and governance references used by the kit README.
    "products/weekly_signal_brief/README.md",
    "analytics/schema.md",
    "monetization/assets/validation.md",
    "monetization/assets/registry.md",
    # Templates and schemas.
    "products/weekly_signal_brief/templates/weekly_brief_template.md",
    "products/weekly_signal_brief/templates/weekly_brief_template.html",
    "products/weekly_signal_brief/templates/weekly_brief_styles.css",
    "products/weekly_signal_brief/templates/weekly_brief_variables.md",
    "products/weekly_signal_brief/templates/csv_appendix_schema.csv",
    "products/weekly_signal_brief/templates/csv_appendix_schema.md",
    # Artifact manifest schema.
    "artifacts/manifest.schema.json",
    # Tooling.
    "scripts/build_weekly_signal_brief.py",
    "scripts/aggregate_weekly_inputs.py",
    "scripts/requirements.txt",
    # Synthetic fixture run (safe to ship).
    "products/weekly_signal_brief/runs/2099-W01-fixture/run.json",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/posts_export.csv",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/decisions.csv",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/hooks_rollup.csv",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/verticals_rollup.csv",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/dataset_health.json",
    "products/weekly_signal_brief/runs/2099-W01-fixture/inputs/template_context.json",
    # Keep outputs folder present but empty.
    "products/weekly_signal_brief/runs/2099-W01-fixture/outputs/.gitkeep",
]


TIER_LICENSE_PATHS = {
    "personal": "products/weekly_signal_brief/licenses/LICENSE_personal_v01.txt",
    "team": "products/weekly_signal_brief/licenses/LICENSE_team_v01.txt",
    "commercial": "products/weekly_signal_brief/licenses/LICENSE_commercial_v01.txt",
}

EXCLUDE_PREFIXES = [
    "build/",
    "dist/",
    ".git/",
    "products/weekly_signal_brief/runs/2026-W04/",
]


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur] + list(cur.parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def _is_excluded(rel_posix: str) -> bool:
    return any(rel_posix.startswith(p) for p in EXCLUDE_PREFIXES)


def iter_allowlisted_paths(repo_root: Path) -> Iterable[Path]:
    for rel in BASE_ALLOWLIST:
        rel_posix = rel.replace("\\", "/")
        if _is_excluded(rel_posix):
            raise SystemExit(f"Allowlist contains excluded path: {rel_posix}")
        p = (repo_root / rel_posix).resolve()
        try:
            p.relative_to(repo_root)
        except Exception:
            raise SystemExit(f"Path escapes repo root: {rel_posix}")
        if not p.exists():
            raise SystemExit(f"Missing file: {rel_posix}")
        yield p


def read_license_text(repo_root: Path, tier: str) -> str:
    rel = TIER_LICENSE_PATHS.get(tier)
    if not rel:
        raise SystemExit(f"Unknown tier '{tier}'. Expected one of: {sorted(TIER_LICENSE_PATHS.keys())}")
    path = (repo_root / rel).resolve()
    try:
        path.relative_to(repo_root)
    except Exception:
        raise SystemExit(f"License path escapes repo root: {rel}")
    if not path.exists():
        raise SystemExit(f"Missing license file: {rel}")
    return path.read_text(encoding="utf-8")


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        required=True,
        help="Output zip path (e.g., dist/gumroad/weekly_signal_brief_core_kit_v01.zip)",
    )
    ap.add_argument(
        "--tier",
        choices=sorted(TIER_LICENSE_PATHS.keys()),
        default=None,
        help="Optional tier name; if set, embeds LICENSE.txt into the zip (personal/team/commercial).",
    )
    args = ap.parse_args(argv)

    repo_root = find_repo_root(Path(__file__).parent)
    out_path = (repo_root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Prevent accidentally writing inside the repo in a non-ignored location.
    try:
        out_rel = out_path.relative_to(repo_root).as_posix()
    except Exception:
        raise SystemExit("--out must be inside the repo")
    if not out_rel.startswith("dist/"):
        raise SystemExit("--out must be under dist/ (repo hygiene)")

    files = list(iter_allowlisted_paths(repo_root))

    license_text: Optional[str] = None
    if args.tier:
        # Include the tier's license file as a normal repo path, and also embed
        # a convenient top-level LICENSE.txt for buyers.
        license_rel = TIER_LICENSE_PATHS[args.tier]
        BASE_ALLOWLIST.append(license_rel)
        files = list(iter_allowlisted_paths(repo_root))
        license_text = read_license_text(repo_root, args.tier)

    # Always use forward slashes in zip for cross-platform stability.
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            rel = p.relative_to(repo_root).as_posix()
            if _is_excluded(rel):
                raise SystemExit(f"Refusing to include excluded file: {rel}")
            z.write(p, arcname=rel)

        if license_text is not None:
            z.writestr("LICENSE.txt", license_text)

    print(f"Wrote: {out_rel} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
