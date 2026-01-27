#!/usr/bin/env python3
"""Attention Mechanics Report v01 builder (fixture-safe).

Design goals:
- Dependency-light (stdlib + jsonschema for manifest validation)
- Deterministic output given the same inputs
- Enforce template variable allowlist
- Render MD + write data appendix + placeholder PDF
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

from product_build_utils import (
    BuildError,
    ensure_dir,
    extract_allowlist_vars,
    extract_template_vars,
    find_repo_root,
    flatten_values,
    git_head_commit,
    read_json,
    render_template,
    utc_now_iso,
    validate_manifest_schema,
    write_json,
    write_manifest,
    write_minimal_pdf,
)

BUILDER_NAME = "build_attention_mechanics_report"
BUILDER_VERSION = "v01"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Attention Mechanics Report v01")
    ap.add_argument("--run-json", required=True, help="Path to products/attention_mechanics_report/runs/<id>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    ap.add_argument("--fail-on-unresolved", action="store_true", help="Fail if template vars remain unresolved")
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    period_id = _require_str(run, "period_id") if "period_id" in run else _require_str(run, "week_id")
    asset_id = _require_str(run, "asset_id")
    asset_version = _require_str(run, "asset_version")

    run_dir = run_path.parent
    template_dir = repo_root / "products" / "attention_mechanics_report" / "templates"

    files = (run.get("inputs") or {}).get("files") if isinstance(run.get("inputs"), dict) else None
    if not isinstance(files, dict):
        raise BuildError("run.json inputs.files must be an object")

    input_paths: List[Path] = []
    merged_ctx: Dict[str, str] = {
        "period_id": period_id,
        "generated_at_utc": str(run.get("generated_at_utc") or utc_now_iso()),
        "date_range": str((run.get("inputs") or {}).get("date_range") or ""),
    }

    platforms = (run.get("inputs") or {}).get("platforms_included")
    if isinstance(platforms, list):
        merged_ctx["platforms_included"] = ", ".join(str(p) for p in platforms)
    else:
        merged_ctx["platforms_included"] = str(platforms or "")

    # Read each referenced input JSON and merge keys as template variables.
    for key in ["attention_flow", "platform_mechanics", "behavioral_patterns", "dataset_health"]:
        rel = files.get(key)
        if not isinstance(rel, str) or not rel.strip():
            raise BuildError(f"run.json inputs.files.{key} is required")
        p = (run_dir / rel).resolve()
        if not p.exists():
            raise BuildError(f"Missing input file: {p}")
        input_paths.append(p)
        merged_ctx.update(flatten_values(read_json(p)))

    # Map dataset_health counts into the template's naming.
    dh = read_json((run_dir / str(files["dataset_health"])).resolve())
    counts = dh.get("counts", {}) if isinstance(dh, dict) else {}
    merged_ctx.setdefault("total_samples", str(counts.get("total_posts", "")))
    merged_ctx.setdefault("valid_samples", str(counts.get("valid_posts", "")))

    # Governance passthroughs.
    gov = run.get("governance", {}) if isinstance(run.get("governance"), dict) else {}
    merged_ctx.setdefault("analytics_schema_version", str(gov.get("schema_version", "")))
    merged_ctx.setdefault("attention_scoring_version", str(merged_ctx.get("attention_scoring_version", "v01")))

    allowlist_path = template_dir / "attention_report_variables.md"
    template_path = template_dir / "attention_report_template.md"

    allowed = extract_allowlist_vars(allowlist_path)
    template = template_path.read_text(encoding="utf-8")

    used = extract_template_vars(template)
    extra = sorted(v for v in used if v not in allowed)
    if extra:
        raise BuildError(f"Template uses non-allowlisted vars: {extra}")

    rendered_md, unresolved = render_template(template, merged_ctx)
    unresolved_sorted = sorted(unresolved)

    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else (repo_root / "build" / "attention_mechanics_report" / period_id)
    )
    ensure_dir(out_dir)

    out_md = out_dir / f"attention_mechanics_report_{period_id}_{BUILDER_VERSION}.md"
    out_data = out_dir / f"attention_mechanics_report_{period_id}_{BUILDER_VERSION}_data.json"
    out_pdf = out_dir / f"attention_mechanics_report_{period_id}_{BUILDER_VERSION}.pdf"
    manifest_path = out_dir / f"{period_id}.manifest.json"

    out_md.write_text(rendered_md, encoding="utf-8")

    data_appendix = {
        "asset_id": asset_id,
        "asset_version": asset_version,
        "period_id": period_id,
        "generated_at_utc": merged_ctx["generated_at_utc"],
        "inputs": {p.name: read_json(p) for p in input_paths},
    }
    write_json(out_data, data_appendix)

    write_minimal_pdf(
        out_pdf,
        title=f"Attention Mechanics Report {period_id} ({BUILDER_VERSION})",
        body_lines=[
            "Fixture PDF placeholder.",
            f"See {out_md.name} for rendered content.",
            f"Unresolved vars: {len(unresolved_sorted)}",
        ],
    )

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
        input_files=input_paths,
        output_files=[out_md, out_data, out_pdf],
        unresolved_template_vars=unresolved_sorted,
    )

    schema_path = repo_root / "artifacts" / "manifest.schema.json"
    validate_manifest_schema(read_json(manifest_path), schema_path)

    if unresolved_sorted:
        msg = "Unresolved template variables:\n" + "\n".join(f"- {v}" for v in unresolved_sorted)
        if args.fail_on_unresolved:
            raise BuildError(msg)
        print(msg, file=sys.stderr)

    print(f"Built artifacts to: {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
