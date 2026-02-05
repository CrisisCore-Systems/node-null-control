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
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\-\.]+)\s*}}")

BUILDER_NAME = "build_weekly_signal_brief"
BUILDER_VERSION = "v01"
MANIFEST_SCHEMA_VERSION = "v01"

MISSING_TOKEN_PREFIX = "[[MISSING:"
MISSING_TOKEN_SUFFIX = "]]"


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
            raise BuildError("CSV header mismatch for " f"{path}\nExpected: {expected_list}\nActual:   {actual}")
        return

    # Non-strict mode: require all expected fields to be present (order-insensitive).
    missing = [h for h in expected_list if h not in set(actual)]
    if missing:
        raise BuildError("CSV header missing required fields for " f"{path}\nMissing: {missing}\nActual:  {actual}")


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


def validate_run_schema(run: Dict[str, Any], path: Path, *, repo_root: Path) -> None:
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

    # run.json must be within the repo and under products/weekly_signal_brief/runs/**/run.json
    try:
        rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        raise BuildError(f"run.json must live inside the repo (got '{path}')")
    if not rel.startswith("products/weekly_signal_brief/runs/") or not rel.endswith("/run.json"):
        raise BuildError("run.json must live under products/weekly_signal_brief/runs/**/run.json " f"(got '{rel}')")

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
        # traversal-safe: disallow .. segments
        posix_parts = Path(v.replace("\\", "/")).parts
        if ".." in posix_parts:
            raise BuildError(f"run.json inputs.files.{k} must not contain '..' (got '{v}') ({path})")
        if not v.replace("\\", "/").startswith("inputs/"):
            raise BuildError(f"run.json inputs.files.{k} must live under inputs/ (got '{v}') ({path})")

    for ok, ov in outputs.items():
        if not isinstance(ov, str):
            raise BuildError(f"run.json outputs.{ok} must be a string ({path})")
        if Path(ov).is_absolute() or ":" in ov:
            raise BuildError(f"run.json outputs.{ok} must be a relative path (got '{ov}') ({path})")
        posix_parts = Path(ov.replace("\\", "/")).parts
        if ".." in posix_parts:
            raise BuildError(f"run.json outputs.{ok} must not contain '..' (got '{ov}') ({path})")
        if not ov.replace("\\", "/").startswith("outputs/"):
            raise BuildError(f"run.json outputs.{ok} must live under outputs/ (got '{ov}') ({path})")


def missing_token(var: str) -> str:
    return f"{MISSING_TOKEN_PREFIX}{var}{MISSING_TOKEN_SUFFIX}"


def complete_context(
    ctx: Dict[str, str],
    allowed_vars: Set[str],
    *,
    render_missing_as: str,
) -> Tuple[Dict[str, str], List[str]]:
    """Ensure every allowlisted variable is present.

    Non-strict behavior must never silently blank: missing vars render as a visible token.
    Strict behavior is enforced by callers using the returned missing list.
    """

    out = dict(ctx)
    missing: List[str] = []
    for v in sorted(allowed_vars):
        if v in out and out[v] != "":
            continue
        missing.append(v)
        if render_missing_as == "token":
            out[v] = missing_token(v)
        elif render_missing_as == "empty":
            out[v] = ""
        else:
            raise BuildError(f"Unknown render_missing_as mode: {render_missing_as}")
    return out, missing


def apply_template_context_overlay(
    ctx: Dict[str, str],
    *,
    overlay: Dict[str, Any],
    allowed_vars: Set[str],
    source_path: Path,
) -> Dict[str, str]:
    """Overlay explicit template context values.

    Guardrail: overlay keys must be within the allowlist.
    """

    out = dict(ctx)
    for k, v in overlay.items():
        if k not in allowed_vars:
            raise BuildError(
                f"template_context contains non-allowlisted key '{k}' ({source_path}). "
                "Bump template version to expand the allowlist."
            )
        out[k] = str(v)
    return out


def validate_manifest_schema(manifest: Dict[str, Any], schema_path: Path) -> None:
    """Validate manifest against artifacts/manifest.schema.json using jsonschema.

    This is the enforcement point that prevents drift and corrupted manifests.
    """

    if not schema_path.exists():
        raise BuildError(f"Manifest schema not found: {schema_path}")

    try:
        import jsonschema  # type: ignore
    except Exception as exc:
        raise BuildError(
            "Missing dependency 'jsonschema' required for manifest validation. "
            "Install it (pip install jsonschema) or run via CI. "
            f"({exc})"
        )

    schema = read_json(schema_path)

    try:
        jsonschema.Draft202012Validator(schema).validate(manifest)
    except jsonschema.ValidationError as exc:
        path_str = "/".join(str(p) for p in exc.path) if exc.path else "(root)"
        raise BuildError(f"Manifest failed schema validation at {path_str}: {exc.message}")


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
        "command_template": None,
        "command_executed": None,
        "exit_code": None,
        "stdout_path": None,
        "stderr_path": None,
        "stdout_tail": None,
        "stderr_tail": None,
    }

    if adapter == "none":
        return meta

    if adapter == "wkhtmltopdf":
        exe = shutil.which("wkhtmltopdf")
        if not exe:
            env_path = os.environ.get("WKHTMLTOPDF_PATH") or os.environ.get("WKHTMLTOPDF")
            if env_path and Path(env_path).exists():
                exe = str(Path(env_path))

        if not exe:
            candidates = [
                Path(r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"),
                Path(r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"),
                Path(r"C:\Program Files\wkhtmltopdf\wkhtmltopdf.exe"),
                Path(r"C:\Program Files (x86)\wkhtmltopdf\wkhtmltopdf.exe"),
            ]
            for c in candidates:
                if c.exists():
                    exe = str(c)
                    break

        if not exe:
            raise BuildError(
                "wkhtmltopdf not found on PATH. Install it or set WKHTMLTOPDF_PATH to the wkhtmltopdf executable."
            )

        cmd = [
            exe,
            "--enable-local-file-access",
            "--load-error-handling",
            "ignore",
            "--load-media-error-handling",
            "ignore",
            str(html_path),
            str(pdf_path),
        ]
        meta["command_executed"] = " ".join(cmd)
        try:
            v = subprocess.check_output([exe, "--version"], stderr=subprocess.STDOUT)
            meta["version"] = v.decode("utf-8", errors="replace").strip()
        except Exception:
            meta["version"] = None
        proc = subprocess.run(cmd, capture_output=True, text=True)
        meta["exit_code"] = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        stdout_path = pdf_path.with_suffix(".wkhtmltopdf.stdout.txt")
        stderr_path = pdf_path.with_suffix(".wkhtmltopdf.stderr.txt")
        stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
        stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
        meta["stdout_path"] = stdout_path.name
        meta["stderr_path"] = stderr_path.name
        meta["stdout_tail"] = stdout[-4000:]
        meta["stderr_tail"] = stderr[-4000:]
        if proc.returncode != 0:
            raise BuildError(f"wkhtmltopdf failed (exit {proc.returncode}): {stderr.strip() or stdout.strip()}")
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise BuildError("wkhtmltopdf reported success but PDF was not created")
        return meta

    if adapter == "command":
        if not pdf_cmd:
            raise BuildError("--pdf-cmd is required when --pdf-adapter=command")
        meta["command_template"] = pdf_cmd
        cmd_str = pdf_cmd.format(html=str(html_path), pdf=str(pdf_path))
        meta["command_executed"] = cmd_str
        proc = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        meta["exit_code"] = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        stdout_path = pdf_path.with_suffix(".adapter.stdout.txt")
        stderr_path = pdf_path.with_suffix(".adapter.stderr.txt")
        stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
        stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
        meta["stdout_path"] = stdout_path.name
        meta["stderr_path"] = stderr_path.name
        meta["stdout_tail"] = stdout[-4000:]
        meta["stderr_tail"] = stderr[-4000:]
        if proc.returncode != 0:
            raise BuildError(f"pdf adapter command failed (exit {proc.returncode}): {stderr.strip() or stdout.strip()}")
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise BuildError("PDF adapter reported success but PDF was not created")
        return meta

    raise BuildError(f"Unknown --pdf-adapter: {adapter}")


def validate_dataset_health(dataset_health: Dict[str, Any], path: Path) -> None:
    required_top = [
        "week_id",
        "counts",
        "rates",
        "top_invalid_reasons",
        "drift_flags",
        "incident_flags",
        "computed_at_utc",
    ]
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
    manifest_schema_ref: str,
    missing_template_vars: Sequence[str],
) -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": str(run.get("week_id", "")),
        "week_id": str(run.get("week_id", "")),
        "asset_id": str(run.get("asset_id", "")),
        "asset_version": str(run.get("asset_version", "")),
        "manifest_schema_ref": manifest_schema_ref,
        "repo_commit": repo_commit,
        "generated_at_utc": generated_at_utc,
        "unresolved_template_vars": list(sorted(set(unresolved_template_vars))),
        "missing_template_vars": list(sorted(set(missing_template_vars))),
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


def build_dataset_health_csv(out_path: Path, *, run: Dict[str, Any], dataset_health: Dict[str, Any]) -> None:
    """Emit a single-row dataset health CSV.

    This is intended for public appendix publishing and tooling.
    """

    counts = dataset_health.get("counts", {})
    rates = dataset_health.get("rates", {})

    header = [
        "week_id",
        "dataset_total_posts",
        "dataset_valid_posts",
        "dataset_invalid_posts",
        "invalid_rate",
        "missing_metrics_rate",
        "drift_flags",
        "incident_flags",
    ]

    row = [
        str(run.get("week_id", "")),
        str(counts.get("total_posts", "")),
        str(counts.get("valid_posts", "")),
        str(counts.get("invalid_posts", "")),
        fmt_rate(rates.get("invalid_rate", "")),
        fmt_rate(rates.get("missing_metrics_rate", "")),
        join_list(dataset_health.get("drift_flags", [])),
        join_list(dataset_health.get("incident_flags", [])),
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(row)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Build Weekly Signal Brief v01 artifacts from a run.json")
    parser.add_argument("--run-file", "--run", dest="run_file", required=True, help="Path to run.json")
    parser.add_argument(
        "--out-dir", "--outdir", dest="out_dir", required=True, help="Output directory for generated artifacts"
    )
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
        "--strict-context",
        action="store_true",
        help="Fail build if any allowlisted template variables are missing data (alias for --fail-on-unresolved)",
    )
    parser.add_argument(
        "--render-missing-as",
        choices=["token", "empty"],
        default="token",
        help="How to render allowlisted-but-missing variables when not strict (default: visible token)",
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

    # Alias: strict-context is the same enforcement as fail-on-unresolved.
    if args.strict_context:
        args.fail_on_unresolved = True

    run_file = Path(args.run_file).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not run_file.exists():
        raise BuildError(f"run.json not found: {run_file}")

    repo_root = find_repo_root(run_file)

    schema_path = (
        Path(args.manifest_schema).resolve()
        if args.manifest_schema
        else (repo_root / "artifacts/manifest.schema.json").resolve()
    )

    run = read_json(run_file)

    validate_run_schema(run, run_file, repo_root=repo_root)

    # Output dir must never target the immutable run outputs folder.
    run_root = run_file.parent
    forbidden_outputs_dir = (run_root / "outputs").resolve()
    try:
        out_rel = out_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        out_rel = None
    if out_dir.resolve() == forbidden_outputs_dir or forbidden_outputs_dir in out_dir.resolve().parents:
        raise BuildError("--out-dir must not be under runs/**/outputs/** (repo hygiene + immutability)")
    if out_rel and "/products/weekly_signal_brief/runs/" in f"/{out_rel}" and "/outputs/" in f"/{out_rel}/":
        raise BuildError("--out-dir must not be under products/weekly_signal_brief/runs/**/outputs/**")

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

    # Build context
    ensure_dir(out_dir)

    ctx = build_context(run, dataset_health)

    # Optional explicit overlay used for fixture runs and manual runs.
    if "template_context" in files:
        overlay_path = (run_root / Path(files["template_context"])).resolve()
        overlay = read_json(overlay_path)
        if not isinstance(overlay, dict):
            raise BuildError(f"template_context must be a JSON object ({overlay_path})")
        ctx = apply_template_context_overlay(ctx, overlay=overlay, allowed_vars=allowed_vars, source_path=overlay_path)

    ctx, missing_vars = complete_context(ctx, allowed_vars, render_missing_as=args.render_missing_as)

    if missing_vars and args.fail_on_unresolved:
        raise BuildError("Missing template context values (strict):\n" + "\n".join(f"- {v}" for v in missing_vars))

    # Render artifacts
    rendered_md, unresolved_md = render_template(md_template_text, ctx)
    rendered_html, unresolved_html = render_template(html_template_text, ctx)

    unresolved = sorted(set(unresolved_md) | set(unresolved_html))

    out_md = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.md"
    out_html = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.html"
    out_css = out_dir / "weekly_brief_styles.css"
    out_appendix = out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}_appendix.csv"

    # Split appendix datasets (stable names for Release assets).
    out_hook_metrics = out_dir / "hook_metrics.csv"
    out_vertical_metrics = out_dir / "vertical_metrics.csv"
    out_decisions = out_dir / "decisions.csv"
    out_dataset_health = out_dir / "dataset_health.csv"

    out_md.write_text(rendered_md, encoding="utf-8")
    out_html.write_text(rendered_html, encoding="utf-8")
    out_css.write_text(css_path.read_text(encoding="utf-8"), encoding="utf-8")

    build_appendix_csv(out_appendix, appendix_schema_path, input_paths)

    # Emit split datasets for public publishing.
    shutil.copyfile(input_paths["hooks_rollup"], out_hook_metrics)
    shutil.copyfile(input_paths["verticals_rollup"], out_vertical_metrics)
    shutil.copyfile(input_paths["decisions"], out_decisions)
    build_dataset_health_csv(out_dataset_health, run=run, dataset_health=dataset_health)

    pdf_adapter_meta: Optional[Dict[str, Any]] = None
    out_pdf: Optional[Path] = None
    if args.pdf_adapter != "none":
        out_pdf = (
            Path(args.pdf_path).resolve()
            if args.pdf_path
            else (out_dir / f"weekly_signal_brief_{run['week_id']}_{BUILDER_VERSION}.pdf")
        )
        pdf_adapter_meta = run_pdf_adapter(
            adapter=args.pdf_adapter,
            html_path=out_html,
            pdf_path=out_pdf,
            pdf_cmd=args.pdf_cmd,
        )

    # Manifest
    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_path = out_dir / f"{run['week_id']}.manifest.json"

    manifest_schema_ref = f"artifacts/manifest.schema.json@{head_commit}"

    output_files: List[Path] = [
        out_md,
        out_html,
        out_css,
        out_appendix,
        out_hook_metrics,
        out_vertical_metrics,
        out_decisions,
        out_dataset_health,
    ]
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
        manifest_schema_ref=manifest_schema_ref,
        missing_template_vars=missing_vars,
    )

    manifest_obj = read_json(manifest_path)
    validate_manifest_schema(manifest_obj, schema_path)

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
