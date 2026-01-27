#!/usr/bin/env python3
"""Content Template Pack v01 builder (fixture-safe).

This builder packages the template pack into a zip and produces a placeholder PDF.
It also enforces that templates only use allowlisted variables.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set

from product_build_utils import (
    BuildError,
    ensure_dir,
    extract_allowlist_vars,
    extract_template_vars,
    find_repo_root,
    git_head_commit,
    read_json,
    utc_now_iso,
    validate_manifest_schema,
    write_manifest,
    write_minimal_pdf,
)

BUILDER_NAME = "build_content_template_pack"
BUILDER_VERSION = "v01"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def _resolve_templates(template_dir: Path, kind: str, names: List[str]) -> List[Path]:
    subdir = template_dir / f"{kind}_templates"
    if not subdir.exists():
        raise BuildError(f"Missing templates directory: {subdir}")
    out: List[Path] = []
    for name in names:
        p = (subdir / name).resolve()
        if not p.exists():
            raise BuildError(f"Missing template file: {p}")
        out.append(p)
    return out


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Content Template Pack v01")
    ap.add_argument("--run-json", required=True, help="Path to products/content_template_pack/runs/<id>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    period_id = _require_str(run, "period_id") if "period_id" in run else _require_str(run, "week_id")
    asset_id = _require_str(run, "asset_id")
    asset_version = _require_str(run, "asset_version")

    template_dir = repo_root / "products" / "content_template_pack" / "templates"

    contents = run.get("contents")
    if not isinstance(contents, dict):
        raise BuildError("run.json contents must be an object")

    hook_names = contents.get("hook_templates") or []
    structure_names = contents.get("structure_templates") or []
    script_names = contents.get("script_templates") or []
    caption_names = contents.get("caption_templates") or []

    if not all(isinstance(x, list) for x in [hook_names, structure_names, script_names, caption_names]):
        raise BuildError("run.json contents.*_templates must be arrays")

    hook_paths = _resolve_templates(template_dir, "hook", list(hook_names))
    structure_paths = _resolve_templates(template_dir, "structure", list(structure_names))
    script_paths = _resolve_templates(template_dir, "script", list(script_names))
    caption_paths = _resolve_templates(template_dir, "caption", list(caption_names))

    usage_guide = (template_dir / "usage_guide.md").resolve()
    variables_md = (template_dir / "template_variables.md").resolve()

    allowlisted = extract_allowlist_vars(variables_md)

    used_vars: Set[str] = set()
    for p in hook_paths + structure_paths + script_paths + caption_paths:
        used_vars |= extract_template_vars(p.read_text(encoding="utf-8"))

    extra = sorted(v for v in used_vars if v not in allowlisted)
    if extra:
        raise BuildError(f"Templates use non-allowlisted vars: {extra}")

    out_dir = (
        Path(args.out_dir).resolve() if args.out_dir else (repo_root / "build" / "content_template_pack" / period_id)
    )
    ensure_dir(out_dir)

    out_zip = out_dir / f"content_template_pack_{period_id}_{BUILDER_VERSION}.zip"
    out_pdf = out_dir / f"content_template_pack_{period_id}_{BUILDER_VERSION}.pdf"
    manifest_path = out_dir / f"{period_id}.manifest.json"

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # include metadata/docs
        if usage_guide.exists():
            z.write(usage_guide, arcname="usage_guide.md")
        z.write(variables_md, arcname="template_variables.md")

        # include templates
        for p in hook_paths:
            z.write(p, arcname=f"hook_templates/{p.name}")
        for p in structure_paths:
            z.write(p, arcname=f"structure_templates/{p.name}")
        for p in script_paths:
            z.write(p, arcname=f"script_templates/{p.name}")
        for p in caption_paths:
            z.write(p, arcname=f"caption_templates/{p.name}")

    write_minimal_pdf(
        out_pdf,
        title=f"Content Template Pack {period_id} ({BUILDER_VERSION})",
        body_lines=[
            "Fixture PDF placeholder.",
            f"Pack zip: {out_zip.name}",
            f"Allowlisted vars: {len(allowlisted)}",
            f"Vars used by templates: {len(used_vars)}",
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
        input_files=[variables_md] + hook_paths + structure_paths + script_paths + caption_paths,
        output_files=[out_zip, out_pdf],
        unresolved_template_vars=[],
    )

    schema_path = repo_root / "artifacts" / "manifest.schema.json"
    validate_manifest_schema(read_json(manifest_path), schema_path)

    print(f"Built artifacts to: {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
