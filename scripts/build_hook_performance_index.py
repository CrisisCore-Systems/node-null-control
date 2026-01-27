#!/usr/bin/env python3
"""Hook Performance Index v01 builder.

Design goals:
- Dependency-light (stdlib + jsonschema for manifest validation)
- Deterministic output given the same inputs
- Mirrors Weekly Signal Brief conventions: run.json -> outputs + manifest

Inputs:
- products/hook_performance_index/runs/<week>/inputs/hooks_rollup.csv
- products/hook_performance_index/runs/<week>/inputs/dataset_health.json (optional)
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\-\.]+)\s*}}")

BUILDER_NAME = "build_hook_performance_index"
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
    return Path.cwd().resolve()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


@dataclass(frozen=True)
class HookRow:
    hook_type: str
    hook_samples: int
    hook_win_rate: Optional[float]
    hook_score_median: Optional[float]
    hook_median_completion: Optional[float]
    hook_median_loop: Optional[float]
    hook_median_retention_ratio: Optional[float]
    hook_median_save_share_rate: Optional[float]


def _parse_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_int(v: Any) -> int:
    if v is None:
        return 0
    s = str(v).strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def read_hooks_rollup(path: Path) -> List[HookRow]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        out: List[HookRow] = []
        for r in reader:
            hook_type = str(r.get("hook_type", "")).strip()
            if not hook_type:
                continue
            out.append(
                HookRow(
                    hook_type=hook_type,
                    hook_samples=_parse_int(r.get("hook_samples")),
                    hook_win_rate=_parse_float(r.get("hook_win_rate")),
                    hook_score_median=_parse_float(r.get("hook_score_median")),
                    hook_median_completion=_parse_float(r.get("hook_median_completion")),
                    hook_median_loop=_parse_float(r.get("hook_median_loop")),
                    hook_median_retention_ratio=_parse_float(r.get("hook_median_retention_ratio")),
                    hook_median_save_share_rate=_parse_float(r.get("hook_median_save_share_rate")),
                )
            )
        return out


def fmt(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def build_tables(rows: List[HookRow], *, top_n: int) -> Tuple[str, str]:
    if not rows:
        md = "No hook rows available (empty rollup)."
        html = '<div class="note">No hook rows available (empty rollup).</div>'
        return md, html

    # Sort primarily by composite score, then win rate, then samples.
    def sort_key(r: HookRow) -> Tuple[float, float, int, str]:
        score = r.hook_score_median if r.hook_score_median is not None else -1e9
        win = r.hook_win_rate if r.hook_win_rate is not None else -1e9
        return (score, win, r.hook_samples, r.hook_type)

    ranked = sorted(rows, key=sort_key, reverse=True)[:top_n]

    md_lines = [
        "| rank | hook_type | samples | score_median | win_rate | completion_med | loop_med | retention_med | save_share_med |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(ranked, start=1):
        md_lines.append(
            "| "
            + " | ".join(
                [
                    str(i),
                    r.hook_type.replace("|", "\\|"),
                    str(r.hook_samples),
                    fmt(r.hook_score_median),
                    fmt(r.hook_win_rate),
                    fmt(r.hook_median_completion),
                    fmt(r.hook_median_loop),
                    fmt(r.hook_median_retention_ratio),
                    fmt(r.hook_median_save_share_rate),
                ]
            )
            + " |"
        )

    html_rows = []
    for i, r in enumerate(ranked, start=1):
        html_rows.append(
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{html_escape(r.hook_type)}</td>"
            f"<td>{r.hook_samples}</td>"
            f"<td>{fmt(r.hook_score_median)}</td>"
            f"<td>{fmt(r.hook_win_rate)}</td>"
            f"<td>{fmt(r.hook_median_completion)}</td>"
            f"<td>{fmt(r.hook_median_loop)}</td>"
            f"<td>{fmt(r.hook_median_retention_ratio)}</td>"
            f"<td>{fmt(r.hook_median_save_share_rate)}</td>"
            "</tr>"
        )

    html = (
        '<table class="table">'
        "<thead><tr>"
        "<th>rank</th><th>hook_type</th><th>samples</th><th>score_median</th><th>win_rate</th>"
        "<th>completion_med</th><th>loop_med</th><th>retention_med</th><th>save_share_med</th>"
        "</tr></thead>"
        "<tbody>" + "".join(html_rows) + "</tbody></table>"
    )

    return "\n".join(md_lines), html


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
    )


def validate_manifest_schema(manifest: Dict[str, Any], schema_path: Path) -> None:
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


def write_manifest(
    *,
    out_path: Path,
    run: Dict[str, Any],
    repo_root: Path,
    repo_commit: str,
    generated_at_utc: str,
    input_files: Sequence[Path],
    output_files: Sequence[Path],
    unresolved_template_vars: Sequence[str],
    builder_meta: Dict[str, str],
    manifest_schema_ref: str,
) -> None:
    inputs = []
    for p in input_files:
        rel = p.resolve().relative_to(repo_root.resolve()).as_posix()
        inputs.append({"name": p.name, "path": rel, "sha256": sha256_file(p)})

    outputs = []
    for p in output_files:
        outputs.append(
            {
                "type": p.suffix.lstrip(".") or "file",
                "filename": p.name,
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
                "content_type": _content_type_for(p),
                "storage": None,
                "url": None,
                "release_asset_name": None,
            }
        )

    obj: Dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_schema_ref": manifest_schema_ref,
        "run_id": str(run.get("week_id", "")),
        "week_id": str(run.get("week_id", "")),
        "asset_id": str(run.get("asset_id", "")),
        "asset_version": str(run.get("asset_version", "")),
        "repo_commit": repo_commit,
        "generated_at_utc": generated_at_utc,
        "builder": builder_meta,
        "inputs": inputs,
        "outputs": outputs,
        "unresolved_template_vars": list(unresolved_template_vars),
    }

    out_path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _content_type_for(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".md":
        return "text/markdown"
    if ext == ".html":
        return "text/html"
    if ext == ".css":
        return "text/css"
    if ext == ".json":
        return "application/json"
    if ext == ".csv":
        return "text/csv"
    return "application/octet-stream"


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Hook Performance Index v01")
    ap.add_argument("--run-json", required=True, help="Path to products/hook_performance_index/runs/<week>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory (default: build/hook_performance_index/<week>)")
    ap.add_argument("--top-n", type=int, default=10, help="Number of hooks to display")
    ap.add_argument("--fail-on-unresolved", action="store_true", help="Fail if template vars remain unresolved")
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    week_id = str(run.get("week_id", "")).strip()
    if not week_id:
        raise BuildError("run.json missing week_id")

    run_dir = run_path.parent
    template_dir = repo_root / "products" / "hook_performance_index" / "templates"

    hooks_rollup_rel = run.get("inputs", {}).get("files", {}).get("hooks_rollup")
    if not hooks_rollup_rel:
        raise BuildError("run.json inputs.files.hooks_rollup is required")
    hooks_rollup_path = (run_dir / str(hooks_rollup_rel)).resolve()
    if not hooks_rollup_path.exists():
        raise BuildError(f"Missing hooks_rollup.csv: {hooks_rollup_path}")

    dataset_note = ""
    dataset_health_rel = run.get("inputs", {}).get("files", {}).get("dataset_health")
    input_files: List[Path] = [hooks_rollup_path]
    if dataset_health_rel:
        dh_path = (run_dir / str(dataset_health_rel)).resolve()
        if dh_path.exists():
            input_files.append(dh_path)
            dh = read_json(dh_path)
            counts = dh.get("counts", {}) if isinstance(dh, dict) else {}
            valid = counts.get("valid_posts")
            total = counts.get("total_posts")
            dataset_note = f"Dataset: total_posts={total} valid_posts={valid}."

    rows = read_hooks_rollup(hooks_rollup_path)
    md_table, html_table = build_tables(rows, top_n=int(args.top_n))

    allowlist_path = template_dir / "hook_index_variables.md"
    allowed = extract_allowlist_vars(allowlist_path)

    md_template_path = template_dir / "hook_index_template.md"
    html_template_path = template_dir / "hook_index_template.html"
    css_path = template_dir / "hook_index_styles.css"

    md_template = md_template_path.read_text(encoding="utf-8")
    html_template = html_template_path.read_text(encoding="utf-8")

    # Guardrail: templates must only use allowlisted vars.
    used = extract_template_vars(md_template) | extract_template_vars(html_template)
    extra = sorted(v for v in used if v not in allowed)
    if extra:
        raise BuildError(f"Template uses non-allowlisted vars: {extra}")

    ctx: Dict[str, str] = {
        "week_id": week_id,
        "generated_at_utc": utc_now_iso(),
        "hooks_count": str(len(rows)),
        "dataset_note": dataset_note or "Dataset note: none.",
        "top_hooks_table_md": md_table,
        "top_hooks_table_html": html_table,
    }

    rendered_md, unresolved_md = render_template(md_template, ctx)
    rendered_html, unresolved_html = render_template(html_template, ctx)
    unresolved = sorted(set(unresolved_md) | set(unresolved_html))

    out_dir = (
        Path(args.out_dir).resolve() if args.out_dir else (repo_root / "build" / "hook_performance_index" / week_id)
    )
    ensure_dir(out_dir)

    out_md = out_dir / f"hook_performance_index_{week_id}_{BUILDER_VERSION}.md"
    out_html = out_dir / f"hook_performance_index_{week_id}_{BUILDER_VERSION}.html"
    out_css = out_dir / "hook_index_styles.css"
    manifest_path = out_dir / f"{week_id}.manifest.json"

    out_md.write_text(rendered_md, encoding="utf-8")
    out_html.write_text(rendered_html, encoding="utf-8")
    out_css.write_text(css_path.read_text(encoding="utf-8"), encoding="utf-8")

    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_schema_ref = f"artifacts/manifest.schema.json@{head_commit}"

    write_manifest(
        out_path=manifest_path,
        run=run,
        repo_root=repo_root,
        repo_commit=head_commit,
        generated_at_utc=utc_now_iso(),
        input_files=input_files,
        output_files=[out_md, out_html, out_css],
        unresolved_template_vars=unresolved,
        builder_meta={"name": BUILDER_NAME, "version": BUILDER_VERSION},
        manifest_schema_ref=manifest_schema_ref,
    )

    schema_path = repo_root / "artifacts" / "manifest.schema.json"
    validate_manifest_schema(read_json(manifest_path), schema_path)

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
