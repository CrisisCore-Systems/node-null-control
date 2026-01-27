#!/usr/bin/env python3
"""Vertical Performance Index v01 builder (fixture-safe).

Design goals:
- Dependency-light (stdlib + jsonschema for schema + manifest validation)
- Deterministic output given the same inputs
- Validate output JSON against products/vertical_performance_index/templates/index_schema.json
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

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

BUILDER_NAME = "build_vertical_performance_index"
BUILDER_VERSION = "v01"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def _clamp_0_100(v: float) -> float:
    if v < 0:
        return 0.0
    if v > 100:
        return 100.0
    return float(v)


def _to_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:  # noqa: BLE001
        return None


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Vertical Performance Index v01")
    ap.add_argument("--run-json", required=True, help="Path to products/vertical_performance_index/runs/<id>/run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory")
    ap.add_argument("--validate-schema", action="store_true", help="Validate output JSON against index_schema.json")
    args = ap.parse_args(list(argv))

    run_path = Path(args.run_json).resolve()
    repo_root = find_repo_root(run_path)

    run = read_json(run_path)
    period_id = _require_str(run, "period_id") if "period_id" in run else _require_str(run, "week_id")
    asset_id = _require_str(run, "asset_id")
    asset_version = _require_str(run, "asset_version")

    run_dir = run_path.parent
    files = (run.get("inputs") or {}).get("files") if isinstance(run.get("inputs"), dict) else None
    if not isinstance(files, dict):
        raise BuildError("run.json inputs.files must be an object")

    verticals_raw_rel = files.get("verticals_raw")
    retention_rel = files.get("retention_metrics")
    stability_rel = files.get("signal_stability")
    dataset_health_rel = files.get("dataset_health")

    if not all(
        isinstance(x, str) and x.strip() for x in [verticals_raw_rel, retention_rel, stability_rel, dataset_health_rel]
    ):
        raise BuildError(
            "run.json inputs.files missing one of required keys: verticals_raw, retention_metrics, signal_stability, dataset_health"
        )

    verticals_raw_path = (run_dir / str(verticals_raw_rel)).resolve()
    retention_path = (run_dir / str(retention_rel)).resolve()
    stability_path = (run_dir / str(stability_rel)).resolve()
    dataset_health_path = (run_dir / str(dataset_health_rel)).resolve()

    for p in [verticals_raw_path, retention_path, stability_path, dataset_health_path]:
        if not p.exists():
            raise BuildError(f"Missing input file: {p}")

    retention = read_json(retention_path)
    stability = read_json(stability_path)
    dataset_health = read_json(dataset_health_path)

    raw_rows: List[Dict[str, Any]] = []
    with verticals_raw_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not r.get("vertical_id"):
                continue
            raw_rows.append(r)

    verticals: List[Dict[str, Any]] = []
    for r in raw_rows:
        vid = str(r.get("vertical_id", "")).strip()
        vname = str(r.get("vertical_name", "")).strip()
        sample_size = int(float(r.get("sample_size") or 0))
        trend = str(r.get("trend", "stable")).strip() or "stable"
        confidence = str(r.get("confidence", "medium")).strip() or "medium"

        ret_obj = retention.get(vid, {}) if isinstance(retention, dict) else {}
        stab_obj = stability.get(vid, {}) if isinstance(stability, dict) else {}

        retention_score = _to_float(ret_obj.get("retention_score"))
        engagement_score = _to_float(ret_obj.get("engagement_score"))
        stability_score = _to_float(stab_obj.get("stability_score"))

        weighted: List[tuple[float, float]] = []
        if retention_score is not None:
            weighted.append((retention_score, 0.5))
        if engagement_score is not None:
            weighted.append((engagement_score, 0.3))
        if stability_score is not None:
            weighted.append((stability_score, 0.2))

        if weighted:
            score = sum(v * w for v, w in weighted) / sum(w for _, w in weighted)
        else:
            score = 0.0

        verticals.append(
            {
                "vertical_id": vid,
                "vertical_name": vname,
                "performance_score": _clamp_0_100(score),
                "retention_score": _clamp_0_100(retention_score) if retention_score is not None else None,
                "engagement_score": _clamp_0_100(engagement_score) if engagement_score is not None else None,
                "stability_score": _clamp_0_100(stability_score) if stability_score is not None else None,
                "sample_size": sample_size,
                "trend": trend,
                "confidence": confidence,
            }
        )

    verticals_sorted = sorted(
        verticals, key=lambda d: (d.get("performance_score") or 0.0, d.get("sample_size") or 0), reverse=True
    )
    for i, v in enumerate(verticals_sorted, start=1):
        v["rank"] = i

    counts = dataset_health.get("counts", {}) if isinstance(dataset_health, dict) else {}
    rates = dataset_health.get("rates", {}) if isinstance(dataset_health, dict) else {}

    out_obj: Dict[str, Any] = {
        "index_version": BUILDER_VERSION,
        "period_id": period_id,
        "generated_at_utc": str(run.get("generated_at_utc") or utc_now_iso()),
        "total_verticals": len(verticals_sorted),
        "dataset_health": {
            "total_samples": int(counts.get("total_posts") or 0),
            "valid_samples": int(counts.get("valid_posts") or 0),
            "invalid_rate": float(rates.get("invalid_rate") or 0.0),
            "drift_flags": list(dataset_health.get("drift_flags", [])) if isinstance(dataset_health, dict) else [],
        },
        "verticals": [
            {
                k: v
                for k, v in vert.items()
                if v is not None
                and k
                in {
                    "vertical_id",
                    "vertical_name",
                    "rank",
                    "performance_score",
                    "retention_score",
                    "engagement_score",
                    "stability_score",
                    "sample_size",
                    "trend",
                    "confidence",
                }
            }
            for vert in verticals_sorted
        ],
    }

    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else (repo_root / "build" / "vertical_performance_index" / period_id)
    )
    ensure_dir(out_dir)

    out_json = out_dir / f"vertical_performance_index_{period_id}_{BUILDER_VERSION}.json"
    out_csv = out_dir / f"vertical_performance_index_{period_id}_{BUILDER_VERSION}.csv"
    manifest_path = out_dir / f"{period_id}.manifest.json"

    write_json(out_json, out_obj)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "vertical_id",
            "vertical_name",
            "rank",
            "performance_score",
            "retention_score",
            "engagement_score",
            "stability_score",
            "sample_size",
            "trend",
            "confidence",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for v in out_obj["verticals"]:
            w.writerow({k: v.get(k) for k in fieldnames})

    if args.validate_schema:
        schema_path = repo_root / "products" / "vertical_performance_index" / "templates" / "index_schema.json"
        validate_json_against_schema(out_obj, schema_path)

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
        input_files=[verticals_raw_path, retention_path, stability_path, dataset_health_path],
        output_files=[out_json, out_csv],
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
