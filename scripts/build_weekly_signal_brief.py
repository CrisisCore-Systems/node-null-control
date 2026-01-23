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
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\-\.]+)\s*}}")


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


def validate_csv_header(path: Path, expected: Sequence[str]) -> None:
    actual = read_csv_header(path)
    if actual != list(expected):
        raise BuildError(
            "CSV header mismatch for "
            f"{path}\nExpected: {list(expected)}\nActual:   {actual}"
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
) -> None:
    manifest = {
        "schema_version": "v01",
        "run_id": str(run.get("week_id", "")),
        "week_id": str(run.get("week_id", "")),
        "asset_id": str(run.get("asset_id", "")),
        "asset_version": str(run.get("asset_version", "")),
        "repo_commit": repo_commit,
        "generated_at_utc": generated_at_utc,
        "unresolved_template_vars": list(sorted(set(unresolved_template_vars))),
        "inputs": [],
        "outputs": [],
    }

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
    parser.add_argument("--run-file", required=True, help="Path to run.json")
    parser.add_argument("--out-dir", required=True, help="Output directory for generated artifacts")
    parser.add_argument(
        "--fail-on-unresolved",
        action="store_true",
        help="Fail build if any template variables remain unresolved after rendering",
    )
    args = parser.parse_args(argv)

    run_file = Path(args.run_file).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not run_file.exists():
        raise BuildError(f"run.json not found: {run_file}")

    repo_root = find_repo_root(run_file)

    run = read_json(run_file)

    required_run_keys = ["asset_id", "asset_version", "week_id", "generated_at_utc", "repo_commit", "inputs", "outputs"]
    for k in required_run_keys:
        if k not in run:
            raise BuildError(f"run.json missing key '{k}' ({run_file})")

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

    # Validate CSV headers (basic schema)
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

    ctx = build_context(run, dataset_health)
    rendered_md, unresolved_md = render_template(md_template_text, ctx)
    rendered_html, unresolved_html = render_template(html_template_text, ctx)

    unresolved = sorted(set(unresolved_md) | set(unresolved_html))

    out_md = out_dir / f"weekly_signal_brief_{run['week_id']}_v01.md"
    out_html = out_dir / f"weekly_signal_brief_{run['week_id']}_v01.html"
    out_css = out_dir / "weekly_brief_styles.css"
    out_appendix = out_dir / f"weekly_signal_brief_{run['week_id']}_v01_appendix.csv"

    out_md.write_text(rendered_md, encoding="utf-8")
    out_html.write_text(rendered_html, encoding="utf-8")
    out_css.write_text(css_path.read_text(encoding="utf-8"), encoding="utf-8")

    build_appendix_csv(out_appendix, appendix_schema_path, input_paths)

    # Manifest
    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_path = out_dir / f"{run['week_id']}.manifest.json"
    write_manifest(
        out_path=manifest_path,
        run=run,
        repo_root=repo_root,
        repo_commit=head_commit,
        generated_at_utc=utc_now_iso(),
        input_files=input_paths,
        output_files=[out_md, out_html, out_css, out_appendix],
        unresolved_template_vars=unresolved,
    )

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
