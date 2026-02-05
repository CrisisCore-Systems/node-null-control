#!/usr/bin/env python3
"""Pattern Engine Report v01 builder (fixture-safe).

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
    html_escape,
    read_json,
    render_template,
    run_pdf_adapter,
    utc_now_iso,
    validate_manifest_schema,
    wrap_html_document,
    write_json,
    write_manifest,
    write_minimal_pdf,
    write_text,
)

BUILDER_NAME = "build_pattern_engine_report"
BUILDER_VERSION = "v01"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Pattern Engine Report v01")
    ap.add_argument("--run-json", required=True, help="Path to products/pattern_engine_report/runs/<id>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    ap.add_argument("--fail-on-unresolved", action="store_true", help="Fail if template vars remain unresolved")
    ap.add_argument(
        "--pdf-adapter",
        default="none",
        choices=["none", "wkhtmltopdf", "command"],
        help="PDF generator adapter for release builds (default: none)",
    )
    ap.add_argument(
        "--pdf-cmd",
        default=None,
        help="Command template for --pdf-adapter=command. Use {html} and {pdf} placeholders.",
    )
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    period_id = _require_str(run, "period_id") if "period_id" in run else _require_str(run, "week_id")
    asset_id = _require_str(run, "asset_id")
    asset_version = _require_str(run, "asset_version")

    run_dir = run_path.parent
    template_dir = repo_root / "products" / "pattern_engine_report" / "templates"

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

    for key in ["patterns_export", "attention_metrics", "structural_analysis", "distribution_rules", "dataset_health"]:
        rel = files.get(key)
        if not isinstance(rel, str) or not rel.strip():
            raise BuildError(f"run.json inputs.files.{key} is required")
        p = (run_dir / rel).resolve()
        if not p.exists():
            raise BuildError(f"Missing input file: {p}")
        input_paths.append(p)
        merged_ctx.update(flatten_values(read_json(p)))

    gov = run.get("governance", {}) if isinstance(run.get("governance"), dict) else {}
    merged_ctx.setdefault("analytics_schema_version", str(gov.get("schema_version", "")))
    merged_ctx.setdefault("pattern_scoring_version", str(merged_ctx.get("pattern_scoring_version", "v01")))

    allowlist_path = template_dir / "pattern_report_variables.md"
    template_path = template_dir / "pattern_report_template.md"

    allowed = extract_allowlist_vars(allowlist_path)
    template = template_path.read_text(encoding="utf-8")

    used = extract_template_vars(template)
    extra = sorted(v for v in used if v not in allowed)
    if extra:
        raise BuildError(f"Template uses non-allowlisted vars: {extra}")

    rendered_md, unresolved = render_template(template, merged_ctx)
    unresolved_sorted = sorted(unresolved)

    css_path = template_dir / "pattern_report_styles.css"
    css_text = css_path.read_text(encoding="utf-8") if css_path.exists() else None
    body_html = (
        '<main style="max-width: 900px; margin: 0 auto; padding: 24px;">'
        f"<h1>{html_escape('Pattern Engine Report')}</h1>"
        f"<p><strong>period</strong>: {html_escape(period_id)}</p>"
        '<pre style="white-space: pre-wrap;">' + html_escape(rendered_md) + "</pre>"
        "</main>"
    )
    rendered_html = wrap_html_document(
        title=f"Pattern Engine Report {period_id}", body_html=body_html, css_text=css_text
    )

    out_dir = (
        Path(args.out_dir).resolve() if args.out_dir else (repo_root / "build" / "pattern_engine_report" / period_id)
    )
    ensure_dir(out_dir)

    outputs_spec = run.get("outputs") if isinstance(run.get("outputs"), dict) else {}
    md_name = Path(str(outputs_spec.get("md", f"pattern_engine_report_{period_id}_{BUILDER_VERSION}.md"))).name
    data_name = Path(
        str(outputs_spec.get("data_appendix", f"pattern_engine_report_{period_id}_{BUILDER_VERSION}_data.json"))
    ).name
    pdf_name = Path(str(outputs_spec.get("pdf", f"pattern_engine_report_{period_id}_{BUILDER_VERSION}.pdf"))).name

    out_md = out_dir / md_name
    out_data = out_dir / data_name
    out_pdf = out_dir / pdf_name
    out_html = out_dir / f"{Path(md_name).stem}.html"
    manifest_path = out_dir / f"{period_id}.manifest.json"

    out_md.write_text(rendered_md, encoding="utf-8")
    write_text(out_html, rendered_html)

    data_appendix = {
        "asset_id": asset_id,
        "asset_version": asset_version,
        "period_id": period_id,
        "generated_at_utc": merged_ctx["generated_at_utc"],
        "inputs": {p.name: read_json(p) for p in input_paths},
    }
    write_json(out_data, data_appendix)

    if args.pdf_adapter == "none":
        write_minimal_pdf(
            out_pdf,
            title=f"Pattern Engine Report {period_id} ({BUILDER_VERSION})",
            body_lines=[
                "PDF adapter disabled; placeholder generated.",
                f"See {out_md.name} for rendered content.",
                f"Unresolved vars: {len(unresolved_sorted)}",
            ],
        )
    else:
        run_pdf_adapter(adapter=args.pdf_adapter, html_path=out_html, pdf_path=out_pdf, pdf_cmd=args.pdf_cmd)

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
        output_files=[out_md, out_html, out_data, out_pdf],
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
