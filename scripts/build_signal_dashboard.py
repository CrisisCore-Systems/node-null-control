#!/usr/bin/env python3
"""Signal Dashboard v01 builder (fixture-safe).

This builder validates the dashboard configuration schema and emits a
resolved config artifact plus a manifest.

Release add-on:
- Optional static webapp bundle (zip) that renders the resolved config.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Sequence

from product_build_utils import (
    BuildError,
    ensure_dir,
    find_repo_root,
    git_head_commit,
    html_escape,
    read_json,
    utc_now_iso,
    validate_json_against_schema,
    validate_manifest_schema,
    wrap_html_document,
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
    ap.add_argument(
        "--bundle-webapp",
        action="store_true",
        help="Also emit a static webapp zip (release deliverable).",
    )
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

    theme = (run.get("configuration") or {}).get("theme") if isinstance(run.get("configuration"), dict) else None
    if isinstance(theme, str) and theme.strip():
        cfg = dict(cfg)
        cfg["theme"] = theme.strip()

    validate_json_against_schema(cfg, schema_path)

    out_dir = Path(args.out_dir).resolve() if args.out_dir else (repo_root / "build" / "signal_dashboard" / period_id)
    ensure_dir(out_dir)

    outputs_spec = run.get("outputs") if isinstance(run.get("outputs"), dict) else {}
    cfg_name = Path(str(outputs_spec.get("dashboard_config", f"dashboard_config_{period_id}.json"))).name
    out_cfg = out_dir / cfg_name
    manifest_path = out_dir / f"{period_id}.manifest.json"

    write_json(out_cfg, cfg)

    out_webapp_zip: Path | None = None
    if args.bundle_webapp:
        zip_name = Path(
            str(outputs_spec.get("webapp_zip", f"signal_dashboard_webapp_{period_id}_{BUILDER_VERSION}.zip"))
        ).name
        out_webapp_zip = out_dir / zip_name

        title = f"Signal Dashboard {period_id}"
        body_html = (
            '<main style="max-width: 1100px; margin: 0 auto; padding: 24px;">'
            f"<h1>{html_escape(title)}</h1>"
            '<p class="muted">Static preview app (no tracking; no notifications).</p>'
            '<div id="app"></div>'
            "</main>"
        )
        html_text = wrap_html_document(title=title, body_html=body_html, css_text=None)

        css_text = """
        :root { color-scheme: light dark; }
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; }
        .muted { opacity: 0.75; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
        .card { border: 1px solid rgba(127,127,127,0.35); border-radius: 10px; padding: 12px; }
        .k { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.7; }
        .h { font-size: 16px; font-weight: 650; margin-top: 6px; }
        .p { font-size: 13px; opacity: 0.9; }
        code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
        pre { white-space: pre-wrap; }
        """.strip()

        js_text = """
        async function loadConfig() {
          const res = await fetch('./assets/dashboard_config.json');
          if (!res.ok) throw new Error('failed to load config');
          return await res.json();
        }

        function el(tag, attrs, children) {
          const n = document.createElement(tag);
          if (attrs) {
            for (const [k,v] of Object.entries(attrs)) {
              if (k === 'class') n.className = v;
              else n.setAttribute(k, v);
            }
          }
          if (children) {
            for (const c of children) {
              if (typeof c === 'string') n.appendChild(document.createTextNode(c));
              else if (c) n.appendChild(c);
            }
          }
          return n;
        }

        function render(cfg) {
          const root = document.getElementById('app');
          root.innerHTML = '';

          root.appendChild(el('div', { class: 'card' }, [
            el('div', { class: 'k' }, ['dashboard_name']),
            el('div', { class: 'h' }, [cfg.dashboard_name || '(unnamed)']),
            el('div', { class: 'p' }, ['refresh_interval_seconds: ' + String(cfg.refresh_interval_seconds)]),
            el('div', { class: 'p' }, ['layout: ' + String(cfg.layout)]),
          ]));

          const widgets = Array.isArray(cfg.widgets) ? cfg.widgets : [];
          const grid = el('div', { class: 'grid' }, []);
          for (const w of widgets) {
            grid.appendChild(el('div', { class: 'card' }, [
              el('div', { class: 'k' }, ['widget']),
              el('div', { class: 'h' }, [String(w.widget_type || 'unknown')]),
              el('div', { class: 'p' }, ['id: ' + String(w.widget_id || '')]),
              el('div', { class: 'p' }, ['data_source: ' + String(w.data_source || '')]),
              el('pre', null, [JSON.stringify(w, null, 2)]),
            ]));
          }
          root.appendChild(el('h2', null, ['Widgets']));
          root.appendChild(grid);
        }

        loadConfig().then(render).catch((err) => {
          const root = document.getElementById('app');
          root.textContent = 'Error: ' + String(err);
        });
        """.strip()

        with zipfile.ZipFile(out_webapp_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("index.html", html_text)
            z.writestr("assets/styles.css", css_text)
            z.writestr("assets/app.js", js_text)
            z.writestr("assets/dashboard_config.json", json.dumps(cfg, indent=2, sort_keys=True))

    head_commit = git_head_commit(repo_root) or str(run.get("repo_commit", ""))
    manifest_schema_ref = f"artifacts/manifest.schema.json@{head_commit}"

    output_files = [out_cfg]
    if out_webapp_zip is not None:
        output_files.append(out_webapp_zip)

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
        output_files=output_files,
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
