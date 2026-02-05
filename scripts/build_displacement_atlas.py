#!/usr/bin/env python3
"""Displacement Risk Atlas v1.1 builder.

Generates a 20-page PDF analyzing 10 sectors approaching automation displacement thresholds.
Uses Jinja2 templates and Playwright HTML-to-PDF rendering for designed artifacts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

from product_build_utils import (
    BuildError,
    count_pdf_pages,
    ensure_dir,
    find_repo_root,
    git_head_commit,
    read_json,
    utc_now_iso,
    write_html_to_pdf,
    write_json,
    write_manifest,
)

BUILDER_NAME = "build_displacement_atlas"
BUILDER_VERSION = "v1.1"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def load_sector_data(product_dir: Path) -> list[Dict[str, Any]]:
    """Load sector data from JSON file."""
    sectors_file = product_dir / "data" / "sectors.json"
    if not sectors_file.exists():
        raise BuildError(f"Sectors data file not found: {sectors_file}")
    
    data = read_json(sectors_file)
    return data.get("sectors", [])


def render_html_template(
    template_dir: Path,
    template_name: str,
    context: Dict[str, Any],
    output_path: Path,
) -> None:
    """Render Jinja2 template to HTML file."""
    try:
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template(template_name)
        html_content = template.render(**context)
        output_path.write_text(html_content, encoding="utf-8")
    except Exception as exc:
        raise BuildError(f"Failed to render template {template_name}: {exc}") from exc


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Displacement Risk Atlas v1.1")
    ap.add_argument("--run-json", required=True, help="Path to run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory (defaults to same dir as run.json)")
    args = ap.parse_args(argv)

    run_json_path = Path(args.run_json).resolve()
    if not run_json_path.exists():
        print(f"ERROR: run.json not found: {run_json_path}", file=sys.stderr)
        return 1

    try:
        run = read_json(run_json_path)
    except BuildError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    run_id = _require_str(run, "run_id")
    asset_id = _require_str(run, "product_id")
    version = _require_str(run, "version")

    if args.out_dir:
        out_dir = Path(args.out_dir).resolve()
    else:
        out_dir = run_json_path.parent / "outputs"

    ensure_dir(out_dir)

    repo_root = find_repo_root(run_json_path)
    # Product directory is two levels up from run.json (products/displacement_risk_atlas/)
    product_dir = run_json_path.parent.parent.parent
    template_dir = product_dir / "templates"
    repo_commit = git_head_commit(repo_root) or "unknown"
    generated_at = utc_now_iso()

    print(f"Building Displacement Risk Atlas v{version}")
    print(f"Run ID: {run_id}")
    print(f"Product directory: {product_dir}")
    print(f"Template directory: {template_dir}")
    print(f"Output directory: {out_dir}")

    # Load sector data from JSON
    print("\nLoading sector data...")
    sectors = load_sector_data(product_dir)
    print(f"Loaded {len(sectors)} sectors")

    # Prepare template context
    build_date = run.get("build_date", generated_at.split("T")[0])
    
    context = {
        "version": version,
        "run_id": run_id,
        "build_date": build_date,
        "generated_at": generated_at,
        "repo_commit": repo_commit,
        "builder_name": BUILDER_NAME,
        "builder_version": BUILDER_VERSION,
        "sectors": sectors,
    }

    # Generate full atlas HTML
    print("\nGenerating full atlas HTML...")
    full_html_path = out_dir / "displacement_risk_atlas_full.html"
    render_html_template(template_dir, "atlas.html", context, full_html_path)
    print(f"  ✓ {full_html_path.name}")

    # Generate preview HTML
    print("Generating preview HTML...")
    preview_context = context.copy()
    # Use first sector (AI/ML Engineering) as sample
    preview_context["sample_sector"] = sectors[0] if sectors else {}
    preview_context["all_sectors"] = sectors
    
    preview_html_path = out_dir / "displacement_risk_atlas_preview.html"
    render_html_template(template_dir, "preview.html", preview_context, preview_html_path)
    print(f"  ✓ {preview_html_path.name}")

    # Convert HTML to PDF
    print("\nGenerating PDFs (this may take a moment)...")
    
    full_pdf_path = out_dir / f"displacement_risk_atlas_v{version}.pdf"
    print(f"  Converting full atlas to PDF...")
    write_html_to_pdf(full_html_path, full_pdf_path)
    print(f"  ✓ {full_pdf_path.name} ({full_pdf_path.stat().st_size:,} bytes)")
    
    preview_pdf_path = out_dir / "displacement_risk_atlas_preview.pdf"
    print(f"  Converting preview to PDF...")
    write_html_to_pdf(preview_html_path, preview_pdf_path)
    print(f"  ✓ {preview_pdf_path.name} ({preview_pdf_path.stat().st_size:,} bytes)")

    # Verify page counts
    print("\nVerifying PDF page counts...")
    try:
        full_page_count = count_pdf_pages(full_pdf_path)
        preview_page_count = count_pdf_pages(preview_pdf_path)
        print(f"  Full PDF: {full_page_count} pages")
        print(f"  Preview PDF: {preview_page_count} pages")
        
        # Validate expected page counts
        if full_page_count < 15:  # Should be ~20 pages, but allow some variation
            print(f"  ⚠️  WARNING: Full PDF has only {full_page_count} pages (expected ~20)")
        if preview_page_count < 2:  # Should be ~3 pages
            print(f"  ⚠️  WARNING: Preview PDF has only {preview_page_count} pages (expected ~3)")
    except BuildError as e:
        print(f"  ⚠️  Could not verify page counts: {e}")

    # Write manifest
    manifest_path = out_dir / "manifest.json"
    print(f"\nWriting manifest: {manifest_path.name}")
    
    input_files = [run_json_path, product_dir / "data" / "sectors.json"]
    output_files = [full_pdf_path, preview_pdf_path, full_html_path, preview_html_path]
    
    write_manifest(
        out_path=manifest_path,
        run_id=run_id,
        asset_id=asset_id,
        asset_version=version,
        repo_root=repo_root,
        repo_commit=repo_commit,
        generated_at_utc=generated_at,
        builder_name=BUILDER_NAME,
        builder_version=BUILDER_VERSION,
        manifest_schema_ref="../../../artifacts/manifest.schema.json",
        input_files=input_files,
        output_files=output_files,
        unresolved_template_vars=[],
    )

    # Update run.json status
    run["status"] = "completed"
    run["build_completed_at"] = generated_at
    run["builder"] = {
        "name": BUILDER_NAME,
        "version": BUILDER_VERSION
    }
    write_json(run_json_path, run)

    print("\n✓ Build completed successfully!")
    print(f"\nOutput files:")
    print(f"  - Full PDF: {full_pdf_path.name} ({full_pdf_path.stat().st_size:,} bytes)")
    print(f"  - Preview PDF: {preview_pdf_path.name} ({preview_pdf_path.stat().st_size:,} bytes)")
    print(f"  - Full HTML: {full_html_path.name}")
    print(f"  - Preview HTML: {preview_html_path.name}")
    print(f"  - Manifest: {manifest_path.name}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
