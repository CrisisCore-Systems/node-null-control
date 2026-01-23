#!/usr/bin/env python3
"""Weekly Signal Brief v01 builder.

Goals:
- Read a run.json (audit spine)
- Validate required inputs exist + basic schema
- Enforce template variable allowlist
- Render v01 templates (MD + HTML) into an external output directory
- Write an artifact manifest (Phase 2 bridge)

This script intentionally treats PDF generation as a pluggable adapter.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\-\.]+)\s*}}")

BUILDER_NAME = "build_weekly_signal_brief"
BUILDER_VERSION = "v01"
MANIFEST_SCHEMA_VERSION = "v01"


class BuildError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BuildError(f"Failed to read JSON: {path} ({exc})")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head_commit(repo_root: Path) -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root), stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return None


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur] + list(cur.parents):
        if (candidate / ".git").exists():
            return candidate
    # Fallback to current working directory.
    return Path.cwd().resolve()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_csv_header(path: Path) -> List[str]:
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
        if not header:
            return []
        return [h.strip() for h in header if h is not None]
    except Exception as exc:
        raise BuildError(f"Failed to read CSV header: {path} ({exc})")


def validate_csv_header(path: Path, expected: Sequence[str], *, strict: bool) -> None:
    actual = read_csv_header(path)
    expected_list = list(expected)
    if strict:
        if actual != expected_list:
            raise BuildError(
                "CSV header mismatch for "
                f"{path}\nExpected: {expected_list}\nActual:   {actual}"
            )
        return

    # Non-strict mode: require all expected fields to be present (order-insensitive).
    missing = [h for h in expected_list if h not in set(actual)]
    if missing:
        raise BuildError(
            "CSV header missing required fields for "
            f"{path}\nMissing: {missing}\nActual:  {actual}"
        )


def extract_allowlist_vars(allowlist_path: Path) -> Set[str]:
    text = allowlist_path.read_text(encoding="utf-8")
    allowed: Set[str] = set()
    for match in re.finditer(r"`{{\s*([^}]+?)\s*}}`", text):
        allowed.add(match.group(1).strip())
    if not allowed:
        raise BuildError(f"No allowlisted variables found in {allowlist_path}")
    return allowed


def extract_template_vars(template_text: str) -> Set[str]:
    return set(VAR_PATTERN.findall(template_text))


def render_template(template_text: str, values: Dict[str, str]) -> Tuple[str, Set[str]]:
    unresolved: Set[str] = set()

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in values:
            return str(values[key])
        unresolved.add(key)
        return m.group(0)

    rendered = VAR_PATTERN.sub(repl, template_text)
    return rendered, unresolved


def join_list(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def fmt_rate(value: Any) -> str:
    # Preserve existing numeric formatting in inputs; only normalize basic floats.
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".") if value != 0 else "0.0"
    return str(value)


def build_context(run: Dict[str, Any], dataset_health: Dict[str, Any]) -> Dict[str, str]:
    inputs = run.get("inputs", {})

    included_block_ids = inputs.get("included_block_ids", [])

    counts = dataset_health.get("counts", {})
    rates = dataset_health.get("rates", {})

    ctx: Dict[str, str] = {
        # Core
        "week_id": str(run.get("week_id", "")),
        "generated_at_utc": str(run.get("generated_at_utc", "")),
        "included_block_ids": join_list(included_block_ids),
        "platforms_included": "mixed",
        # Dataset counts
        "dataset_total_posts": str(counts.get("total_posts", "")),
        "dataset_valid_posts": str(counts.get("valid_posts", "")),
        "dataset_invalid_posts": str(counts.get("invalid_posts", "")),
        "invalid_rate": fmt_rate(rates.get("invalid_rate", "")),
        # Dataset health
        "missing_metrics_rate": fmt_rate(rates.get("missing_metrics_rate", "")),
        "top_invalid_reasons": join_list(dataset_health.get("top_invalid_reasons", [])),
        "drift_flags": join_list(dataset_health.get("drift_flags", [])),
        "incident_flags": join_list(dataset_health.get("incident_flags", [])),
        "dataset_health_notes": str(dataset_health.get("notes", "")),
        # Appendix pins (best-effort)
        "analytics_schema_version": str(run.get("governance", {}).get("schema_version", "")),
        "hooks_version": str(run.get("governance", {}).get("hooks_version", "")),
    }

    # Optional passthroughs if present in run.json in future
    for k in ["date_range", "duration_band", "voice_style", "visual_style", "caption_policy", "scoring_version"]:
        v = run.get(k)
        if v is not None:
            ctx[k] = str(v)

    return ctx


def validate_run_schema(run: Dict[str, Any], path: Path) -> None:
    """Minimal run.json schema validation (no external deps)."""

    def require(key: str, expected_type: type) -> Any:
        if key not in run:
            raise BuildError(f"run.json missing key '{key}' ({path})")
        value = run[key]
        if not isinstance(value, expected_type):
            raise BuildError(f"run.json '{key}' must be {expected_type.__name__} ({path})")
        return value

    require("asset_id", str)
    require("asset_version", str)
    week_id = require("week_id", str)
    generated_at_utc = require("generated_at_utc", str)
    repo_commit = require("repo_commit", str)
    inputs = require("inputs", dict)
    outputs = require("outputs", dict)

    if not re.match(r"^[0-9]{4}-W[0-9]{2}.*$", week_id):
        raise BuildError(f"run.json week_id must match YYYY-Www (got '{week_id}') ({path})")

    if not re.match(r"^[0-9a-f]{7,40}$", repo_commit):
        raise BuildError(f"run.json repo_commit must be a hex git hash (got '{repo_commit}') ({path})")

    # Basic ISO-ish stamp check (don't be too strict about Z vs offset)
    if "T" not in generated_at_utc:
        raise BuildError(f"run.json generated_at_utc must be ISO datetime-like (got '{generated_at_utc}') ({path})")

    if not isinstance(inputs.get("files"), dict):
        raise BuildError(f"run.json inputs.files must be an object ({path})")

    # Ensure inputs/outputs are relative and stay within their folders.
    for k, v in inputs["files"].items():
        if not isinstance(v, str):
            raise BuildError(f"run.json inputs.files.{k} must be a string ({path})")
        if Path(v).is_absolute() or ":" in v:
            raise BuildError(f"run.json inputs.files.{k} must be a relative path (got '{v}') ({path})")
        if not v.replace("\\", "/").startswith("inputs/"):
            raise BuildError(f"run.json inputs.files.{k} must live under inputs/ (got '{v}') ({path})")

    for ok, ov in outputs.items():
        if not isinstance(ov, str):
            raise BuildError(f"run.json outputs.{ok} must be a string ({path})")
        if Path(ov).is_absolute() or ":" in ov:
            raise BuildError(f"run.json outputs.{ok} must be a relative path (got '{ov}') ({path})")
        if not ov.replace("\\", "/").startswith("outputs/"):
            raise BuildError(f"run.json outputs.{ok} must live under outputs/ (got '{ov}') ({path})")


def default_value_for_var(var: str) -> str:
    if var.endswith("_samples"):
        return "0"
    if var.startswith("dataset_") and ("posts" in var):
        return "0"
    if var.endswith("_rate") or "median" in var or "pct" in var or "ratio" in var or "score" in var:
        return "0.0"
    if var.endswith("_notes") or var.endswith("_evidence") or var.endswith("_why") or var.endswith("_reco"):
        return "TBD"
    return "TBD"


def complete_context(ctx: Dict[str, str], allowed_vars: Set[str]) -> Dict[str, str]:
    """Ensure every allowlisted variable has a deterministic value.

    This makes --fail-on-unresolved a contract check (builder completeness)
    rather than a data-availability check.
    """

    out = dict(ctx)
    for v in allowed_vars:
        out.setdefault(v, default_value_for_var(v))
    return out


def validate_manifest_v01(manifest: Dict[str, Any], schema_path: Path) -> None:
    """Validate manifest structure against our v01 schema semantics.

    This is intentionally dependency-free and aligned to artifacts/manifest.schema.json.
    """

    if not schema_path.exists():
        raise BuildError(f"Manifest schema not found: {schema_path}")

    if not isinstance(manifest, dict):
        raise BuildError("Manifest must be a JSON object")

    required = [
        "schema_version",
        "run_id",
        "week_id",
        "asset_id",
        "asset_version",
        "repo_commit",
        "generated_at_utc",
        "inputs",
        "outputs",
    ]
    for k in required:
        if k not in manifest:
            raise BuildError(f"Manifest missing key '{k}'")

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise BuildError(f"Manifest schema_version must be '{MANIFEST_SCHEMA_VERSION}'")

    week_id = manifest.get("week_id")
    if not isinstance(week_id, str) or not re.match(r"^[0-9]{4}-W[0-9]{2}.*$", week_id):
        raise BuildError("Manifest week_id must match YYYY-Www")

    repo_commit = manifest.get("repo_commit")
    if not isinstance(repo_commit, str) or not re.match(r"^[0-9a-f]{7,40}$", repo_commit):
        raise BuildError("Manifest repo_commit must be a hex git hash")

    inputs = manifest.get("inputs")
    outputs = manifest.get("outputs")
    if not isinstance(inputs, list) or not inputs:
        raise BuildError("Manifest inputs must be a non-empty array")
    if not isinstance(outputs, list) or not outputs:
        raise BuildError("Manifest outputs must be a non-empty array")

    for item in inputs:
        if not isinstance(item, dict):
            raise BuildError("Manifest inputs[] entries must be objects")
        for k in ["name", "path", "sha256"]:
            if k not in item:
                raise BuildError(f"Manifest inputs[] missing '{k}'")
        if not re.match(r"^[0-9a-f]{64}$", str(item.get("sha256", ""))):
            raise BuildError("Manifest inputs[].sha256 must be a sha256 hex string")

    for item in outputs:
        if not isinstance(item, dict):
            raise BuildError("Manifest outputs[] entries must be objects")
        for k in ["type", "filename", "sha256", "size_bytes", "content_type"]:
            if k not in item:
                raise BuildError(f"Manifest outputs[] missing '{k}'")
        if not re.match(r"^[0-9a-f]{64}$", str(item.get("sha256", ""))):
            raise BuildError("Manifest outputs[].sha256 must be a sha256 hex string")
        if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] < 0:
            raise BuildError("Manifest outputs[].size_bytes must be a non-negative integer")

    # Optional metadata blocks
    if "builder" in manifest:
        b = manifest["builder"]
        if not isinstance(b, dict):
            raise BuildError("Manifest builder must be an object")
        for k in ["name", "version"]:
            if k not in b or not isinstance(b[k], str) or not b[k]:
                raise BuildError("Manifest builder.name/version must be non-empty strings")

    if "pdf_adapter" in manifest:
        a = manifest["pdf_adapter"]
        if not isinstance(a, dict):
            raise BuildError("Manifest pdf_adapter must be an object")
        if "name" not in a or not isinstance(a["name"], str) or not a["name"]:
            raise BuildError("Manifest pdf_adapter.name must be a non-empty string")


def run_pdf_adapter(
    *,
    adapter: str,
    html_path: Path,
    pdf_path: Path,
    pdf_cmd: Optional[str],
) -> Dict[str, Any]:
    """Standard adapter seam: given (html_path, pdf_path) produce a PDF."""

    meta: Dict[str, Any] = {
        "name": adapter,
        "version": None,
        "command": None,
        "exit_code": None,
    }

    if adapter == "none":
        return meta

    if adapter == "wkhtmltopdf":
        cmd = ["wkhtmltopdf", str(html_path), str(pdf_path)]
        meta["command"] = " ".join(cmd)
        try:
            v = subprocess.check_output(["wkhtmltopdf", "--version"], stderr=subprocess.STDOUT)
            meta["version"] = v.decode("utf-8", errors="replace").strip()
        except Exception:
            meta["version"] = None
        proc = subprocess.run(cmd, capture_output=True, text=True)
        meta["exit_code"] = proc.returncode
        if proc.returncode != 0:
            raise BuildError(f"wkhtmltopdf failed (exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
        return meta

    if adapter == "command":
        if not pdf_cmd:
            raise BuildError("--pdf-cmd is required when --pdf-adapter=command")
        cmd_str = pdf_cmd.format(html=str(html_path), pdf=str(pdf_path))
        meta["command"] = cmd_str
        proc = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        meta["exit_code"] = proc.returncode
        if proc.returncode != 0:
            raise BuildError(f"pdf adapter command failed (exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
        return meta

    raise BuildError(f"Unknown --pdf-adapter: {adapter}")


def validate_dataset_health(dataset_health: Dict[str, Any], path: Path) -> None:
    required_top = ["week_id", "counts", "rates", "top_invalid_reasons", "drift_flags", "incident_flags", "computed_at_utc"]
    for key in required_top:
        if key not in dataset_health:
            raise BuildError(f"dataset_health.json missing key '{key}' ({path})")

    counts = dataset_health.get("counts")
    rates = dataset_health.get("rates")
    if not isinstance(counts, dict) or not isinstance(rates, dict):
        raise BuildError(f"dataset_health.json invalid 'counts'/'rates' objects ({path})")

    for key in ["total_posts", "valid_posts", "invalid_posts"]:
        if key not in counts:
            raise BuildError(f"dataset_health.json counts missing '{key}' ({path})")

    for key in ["invalid_rate", "missing_metrics_rate"]:
        if key not in rates:
            raise BuildError(f"dataset_health.json rates missing '{key}' ({path})")


@dataclass(frozen=True)
class OutputArtifact:
    type: str
    filename: str
    sha256: str
    size_bytes: int
    content_type: str
    storage: Optional[str] = None
    url: Optional[str] = None
    release_asset_name: Optional[str] = None


def guess_content_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".html"):
        return "text/html"
    if lower.endswith(".md"):
        return "text/markdown"
    if lower.endswith(".css"):
        return "text/css"
    if lower.endswith(".json"):
        return "application/json"
    if lower.endswith(".csv"):
        return "text/csv"
    if lower.endswith(".pdf"):
        return "application/pdf"
    return "application/octet-stream"


def write_manifest(
    *,
    out_path: Path,
    run: Dict[str, Any],
    repo_root: Path,
    repo_commit: str,
    generated_at_utc: str,
    input_files: Dict[str, Path],
    output_files: List[Path],
    unresolved_template_vars: Sequence[str],
    builder_meta: Dict[str, Any],
    pdf_adapter_meta: Optional[Dict[str, Any]],
) -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": str(run.get("week_id", "")),
        "week_id": str(run.get("week_id", "")),
        "asset_id": str(run.get("asset_id", "")),
        "asset_version": str(run.get("asset_version", "")),
        "repo_commit": repo_commit,
        "generated_at_utc": generated_at_utc,
        "unresolved_template_vars": list(sorted(set(unresolved_template_vars))),
        "builder": builder_meta,
        "inputs": [],
        "outputs": [],
    }

    if pdf_adapter_meta and pdf_adapter_meta.get("name") and pdf_adapter_meta.get("name") != "none":
        manifest["pdf_adapter"] = pdf_adapter_meta

    for logical_name, path in input_files.items():
        try:
            display_path = str(path.relative_to(repo_root).as_posix())
        except Exception:
            display_path = str(path.as_posix())
        manifest["inputs"].append(
            {
                "name": logical_name,
                "path": display_path,
                "sha256": sha256_file(path),
            }
        )

    for path in output_files:
        st = path.stat()
        manifest["outputs"].append(
            {
                "type": path.suffix.lstrip(".") or "file",
                "filename": path.name,
                "sha256": sha256_file(path),
                "size_bytes": st.st_size,
                "content_type": guess_content_type(path.name),
                "storage": None,
                "url": None,
                "release_asset_name": None,
            }
        )

    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_appendix_csv(out_path: Path, schema_path: Path, inputs: Dict[str, Path]) -> None:
    """Create a single appendix CSV with multiple schema sections separated by blank lines.

    This mirrors the multi-header style in templates/csv_appendix_schema.csv.
    """

    schema_lines = schema_path.read_text(encoding="utf-8").splitlines()
    headers: List[List[str]] = []
    for line in schema_lines:
        if not line.strip():
            continue
        headers.append([h.strip() for h in line.split(",")])

    sections: List[Tuple[str, Path]] = [
        ("hooks_rollup", inputs["hooks_rollup"]),
        ("verticals_rollup", inputs["verticals_rollup"]),
        ("decisions", inputs["decisions"]),
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        for idx, header in enumerate(headers):
            writer = csv.writer(f)
            writer.writerow(header)

            # Append data rows from the corresponding input file when possible.
            if idx < len(sections):
                _, src = sections[idx]
                with src.open("r", encoding="utf-8", newline="") as src_f:
                    reader = csv.reader(src_f)
                    _ = next(reader, None)  # skip header
                    for row in reader:
                        if row:
                            writer.writerow(row)

            # blank line between sections
            f.write("\n")


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Build Weekly Signal Brief v01 artifacts from a run.json")
    parser.add_argument("--run-file", "--run", dest="run_file", required=True, help="Path to run.json")
    parser.add_argument("--out-dir", "--outdir", dest="out_dir", required=True, help="Output directory for generated artifacts")
    parser.add_argument(
        "--strict-csv-headers",
        action="store_true",
        help="Enforce exact CSV header matches (recommended for CI)",
    )
    parser.add_argument(
        "--fail-on-unresolved",
        action="store_true",
        help="Fail build if any template variables remain unresolved after rendering",
    )
    parser.add_argument(
        "--manifest-schema",
        default=None,
        help="Path to artifacts/manifest.schema.json (defaults to repo-root artifacts/manifest.schema.json)",
    )
    parser.add_argument(
        "--pdf-adapter",
        choices=["none", "wkhtmltopdf", "command"],
        default="none",
        help="PDF adapter to run (builder always emits HTML; adapter optionally produces PDF)",
    )
    parser.add_argument(
        "--pdf-path",
        default=None,
        help="Where to write the generated PDF (defaults under --out-dir)",
    )
    parser.add_argument(
        "--pdf-cmd",
        default=None,
        help="Command template for --pdf-adapter=command. Use {html} and {pdf} placeholders.",
    )
    args = parser.parse_args(argv)

    run_file = Path(args.run_file).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not run_file.exists():
        raise BuildError(f"run.json not found: {run_file}")

    repo_root = find_repo_root(run_file)

    schema_path = Path(args.manifest_schema).resolve() if args.manifest_schema else (repo_root / "artifacts/manifest.schema.json").resolve()

    run = read_json(run_file)

    validate_run_schema(run, run_file)

    run_root = run_file.parent
    inputs_meta = run.get("inputs", {})
    files = inputs_meta.get("files", {})

    required_files = ["posts_export", "hooks_rollup", "verticals_rollup", "decisions", "dataset_health"]
    for fkey in required_files:
        if fkey not in files:
            raise BuildError(f"run.json inputs.files missing '{fkey}' ({run_file})")

    input_paths: Dict[str, Path] = {k: (run_root / Path(v)).resolve() for k, v in files.items()}

    for k, p in input_paths.items():
        if not p.exists():
            raise BuildError(f"Missing required input file '{k}': {p}")

    # Validate CSV headers
    validate_csv_header(
        input_paths["posts_export"],
        [
            "date",
            "platform",
            "vertical",
            "hook_type",
            "hook_text",
            "duration_sec",
            "visual_style",
            "voice_style",
            "block_id",
            "experiment_id",
            "variant_id",
            "is_control",
            "views_1h",
            "views_24h",
            "avg_view_duration_sec",
            "completion_pct",
            "loop_pct",
            "shares",
            "saves",
            "comments",
            "decision",
            "notes",
        ],
        strict=args.strict_csv_headers,
    )
    validate_csv_header(
        input_paths["hooks_rollup"],
        [
            "week_id",
            "platform",
            "duration_band",
            "block_id",
            "hook_type",
            "hook_samples",
            "hook_win_rate",
            "hook_median_completion",
            "hook_median_loop",
            "hook_median_retention_ratio",
            "hook_median_save_share_rate",
            "hook_score_median",
        ],
        strict=args.strict_csv_headers,
    )
    validate_csv_header(
        input_paths["verticals_rollup"],
        [
            "week_id",
            "platform",
            "duration_band",
            "block_id",
            "vertical",
            "vertical_samples",
            "vertical_win_rate",
            "vertical_median_completion",
            "vertical_median_loop",
            "vertical_median_retention_ratio",
            "vertical_median_save_share_rate",
            "vertical_score_median",
        ],
        strict=args.strict_csv_headers,
    )
    validate_csv_header(
        input_paths["decisions"],
        [
            "week_id",
            "decision_type",
            "pattern_type",
            "pattern_id",
            "block_id",
            "evidence_summary",
            "next_action",
            "followup_week",
        ],
        strict=args.strict_csv_headers,
    )

    dataset_health = read_json(input_paths["dataset_health"])
    validate_dataset_health(dataset_health, input_paths["dataset_health"])

    # Enforce template variable allowlist
    allowlist_path = (repo_root / "products/weekly_signal_brief/templates/weekly_brief_variables.md").resolve()
    md_template_path = (repo_root / "products/weekly_signal_brief/templates/weekly_brief_template.md").resolve()
    html_template_path = (repo_root / "products/weekly_signal_brief/templates/weekly_brief_template.html").resolve()
    css_path = (repo_root / "products/weekly_signal_brief/templates/weekly_brief_styles.css").resolve()
    appendix_schema_path = (repo_root / "products/weekly_signal_brief/templates/csv_appendix_schema.csv").resolve()

    for p in [allowlist_path, md_template_path, html_template_path, css_path, appendix_schema_path]:
        if not p.exists():
            raise BuildError(f"Missing template asset: {p}")

    allowed_vars = extract_allowlist_vars(allowlist_path)

    md_template_text = md_template_path.read_text(encoding="utf-8")
    html_template_text = html_template_path.read_text(encoding="utf-8")

    used_vars = extract_template_vars(md_template_text) | extract_template_vars(html_template_text)
    unknown_vars = sorted(v for v in used_vars if v not in allowed_vars)
    if unknown_vars:
        raise BuildError(
            "Template variables not in allowlist (update allowlist only with a version bump):\n"
            + "\n".join(f"- {v}" for v in unknown_vars)
        )

    # Render artifacts
    ensure_dir(out_dir)

    ctx = complete_context(build_context(run, dataset_health), allowed_vars)
    rendered_md, unresolved_md = render_template(md_template_text, ctx)
    rendered_html, unresolved_html = render_template(html_template_text, ctx)

    unresolved = sorted(set(unresolved_md) | set(unresolved_html))

    out_md = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.md"
    out_html = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.html"
    out_css = out_dir / "weekly_brief_styles.css"
    out_appendix = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}_appendix.csv"

    out_md.write_text(rendered_md, encoding="utf-8")
    out_html.write_text(rendered_html, encoding="utf-8")
    out_css.write_text(css_path.read_text(encoding="utf-8"), encoding="utf-8")

    build_appendix_csv(out_appendix, appendix_schema_path, input_paths)

    pdf_adapter_meta: Optional[Dict[str, Any]] = None
    out_pdf: Optional[Path] = None
    if args.pdf_adapter != "none":
        out_pdf = Path(args.pdf_path).resolve() if args.pdf_path else (out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.pdf")
        pdf_adapter_meta = run_pdf_adapter(
            adapter=args.pdf_adapter,
            html_path=out_html,
            pdf_path=out_pdf,
            pdf_cmd=args.pdf_cmd,
        )

    # Manifest
    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_path = out_dir / f"{run['week_id']}.manifest.json"

    output_files: List[Path] = [out_md, out_html, out_css, out_appendix]
    if out_pdf and out_pdf.exists():
        output_files.append(out_pdf)

    write_manifest(
        out_path=manifest_path,
        run=run,
        repo_root=repo_root,
        repo_commit=head_commit,
        generated_at_utc=utc_now_iso(),
        input_files=input_paths,
        output_files=output_files,
        unresolved_template_vars=unresolved,
        builder_meta={"name": BUILDER_NAME, "version": BUILDER_VERSION},
        pdf_adapter_meta=pdf_adapter_meta,
    )

    manifest_obj = read_json(manifest_path)
    validate_manifest_v01(manifest_obj, schema_path)

    if unresolved:
        msg = "Unresolved template variables:\n" + "\n".join(f"- {v}" for v in unresolved)
        if args.fail_on_unresolved:
            raise BuildError(msg)
        print(msg, file=sys.stderr)

    print(f"Built artifacts to: {out_dir}")
    print(f"Wrote manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
