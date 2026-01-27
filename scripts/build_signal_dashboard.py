#!/usr/bin/env python3
"""Signal Dashboard v01 builder (fixture-safe).

This builder validates the dashboard configuration schema and emits a
resolved config artifact plus a manifest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

from product_build_utils import (
    BuildError,
    ensure_dir,
    find_repo_root,
    git_head_commit,
    read_json,
    utc_now_iso,
    validate_json_against_schema,
    validate_manifest_schema,
    write_json,
    write_manifest,
)

BUILDER_NAME = "build_signal_dashboard"
BUILDER_VERSION = "v01"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Signal Dashboard v01")
    ap.add_argument("--run-json", required=True, help="Path to products/signal_dashboard/runs/<id>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    period_id = _require_str(run, "period_id") if "period_id" in run else _require_str(run, "week_id")
    asset_id = _require_str(run, "asset_id")
    asset_version = _require_str(run, "asset_version")

    template_dir = repo_root / "products" / "signal_dashboard" / "templates"
    schema_path = template_dir / "dashboard_config_schema.json"

    cfg_rel = (
        (run.get("configuration") or {}).get("dashboard_config") if isinstance(run.get("configuration"), dict) else None
    )
    if not isinstance(cfg_rel, str) or not cfg_rel.strip():
        raise BuildError("run.json configuration.dashboard_config must be a string")

    if cfg_rel.startswith("templates/"):
        cfg_path = (repo_root / "products" / "signal_dashboard" / cfg_rel).resolve()
    else:
        cfg_path = (run_path.parent / cfg_rel).resolve()
    if not cfg_path.exists():
        raise BuildError(f"Missing dashboard config: {cfg_path}")

    cfg = read_json(cfg_path)

    # Apply theme (optional).
    theme = (run.get("configuration") or {}).get("theme") if isinstance(run.get("configuration"), dict) else None
    if isinstance(theme, str) and theme.strip():
        cfg = dict(cfg)
        cfg["theme"] = theme.strip()

    validate_json_against_schema(cfg, schema_path)

    out_dir = Path(args.out_dir).resolve() if args.out_dir else (repo_root / "build" / "signal_dashboard" / period_id)
    ensure_dir(out_dir)

    out_cfg = out_dir / f"dashboard_config_{period_id}.json"
    manifest_path = out_dir / f"{period_id}.manifest.json"

    write_json(out_cfg, cfg)

    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_schema_ref = f"artifacts/manifest.schema.json@{head_commit}"

    write_manifest(
        out_path=manifest_path,
        run_id=period_id,
        asset_id=asset_id,
        asset_version=asset_version,
        repo_root=repo_root,
        repo_commit=head_commit,
        generated_at_utc=utc_now_iso(),
        builder_name=BUILDER_NAME,
        builder_version=BUILDER_VERSION,
        manifest_schema_ref=manifest_schema_ref,
        input_files=[cfg_path, schema_path],
        output_files=[out_cfg],
        unresolved_template_vars=[],
    )

    manifest_schema_path = repo_root / "artifacts" / "manifest.schema.json"
    validate_manifest_schema(read_json(manifest_path), manifest_schema_path)

    print(f"Built artifacts to: {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
