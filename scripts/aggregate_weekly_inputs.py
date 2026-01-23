"""Aggregate weekly inputs for Weekly Signal Brief.

This script is intentionally dependency-free (stdlib only) and produces:

- hooks_rollup.csv
- verticals_rollup.csv
- dataset_health.json

from a run's frozen inputs/posts_export.csv.

Design goals:
- Deterministic output given the same input rows.
- Valid-only rollups (invalid rows remain in posts_export.csv for auditability).
- Small-sample friendly: emits explicit flags/notes when the dataset is thin.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PostRow:
    date: str
    platform: str
    vertical: str
    hook_type: str
    duration_sec: Optional[float]
    block_id: str
    decision: str
    notes: str

    views_1h: Optional[float]
    views_24h: Optional[float]
    avg_view_duration_sec: Optional[float]
    completion_pct: Optional[float]
    loop_pct: Optional[float]
    shares: Optional[float]
    saves: Optional[float]


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


def _parse_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "yes"}:
        return True
    if s in {"false", "0", "no"}:
        return False
    return None


def _duration_band(duration_sec: Optional[float]) -> str:
    if duration_sec is None:
        return "unknown"
    d = float(duration_sec)
    if 15 <= d <= 19:
        return "15-19"
    if 20 <= d <= 27:
        return "20-27"
    if 28 <= d <= 35:
        return "28-35"
    return "other"


def _robust_norm(values: Sequence[float]) -> List[float]:
    """Robust normalize values to 0..1 via median/MAD + logistic.

    Matches analytics/schema.md intent without external deps.
    """

    if not values:
        return []
    m = median(values)
    abs_dev = [abs(x - m) for x in values]
    d = median(abs_dev)
    denom = max(1e-9, 1.4826 * d)
    out: List[float] = []
    for x in values:
        z = (x - m) / denom
        out.append(1.0 / (1.0 + math.exp(-z)))
    return out


def _format_float(v: Optional[float]) -> str:
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return ""
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _extract_invalid_reason(decision: str, notes: str, missing: List[str]) -> Optional[str]:
    # Prefer explicit note tag if present.
    n = (notes or "")
    upper = n.upper()
    if "INVALID_REASON:" in upper:
        try:
            after = upper.split("INVALID_REASON:", 1)[1].strip()
            reason = after.split(" ", 1)[0].strip().strip(",;.")
            return reason.lower() if reason else None
        except Exception:
            pass

    if decision.strip().lower() == "invalid":
        # If caller marked invalid but no explicit reason, fall back.
        if missing:
            return f"missing_{missing[0]}"
        return "marked_invalid"

    if missing:
        return f"missing_{missing[0]}"

    return None


def _parse_posts_csv(path: Path) -> List[PostRow]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows: List[PostRow] = []
        for r in reader:
            rows.append(
                PostRow(
                    date=str(r.get("date", "")).strip(),
                    platform=str(r.get("platform", "")).strip(),
                    vertical=str(r.get("vertical", "")).strip(),
                    hook_type=str(r.get("hook_type", "")).strip(),
                    duration_sec=_parse_float(r.get("duration_sec")),
                    block_id=str(r.get("block_id", "")).strip(),
                    decision=str(r.get("decision", "")).strip(),
                    notes=str(r.get("notes", "")).strip(),
                    views_1h=_parse_float(r.get("views_1h")),
                    views_24h=_parse_float(r.get("views_24h")),
                    avg_view_duration_sec=_parse_float(r.get("avg_view_duration_sec")),
                    completion_pct=_parse_float(r.get("completion_pct")),
                    loop_pct=_parse_float(r.get("loop_pct")),
                    shares=_parse_float(r.get("shares")),
                    saves=_parse_float(r.get("saves")),
                )
            )
        return rows


def _retention_ratio(row: PostRow) -> Optional[float]:
    if row.avg_view_duration_sec is None or row.duration_sec is None or row.duration_sec <= 0:
        return None
    return min(1.0, row.avg_view_duration_sec / row.duration_sec)


def _save_share_rate(row: PostRow) -> Optional[float]:
    if row.views_24h is None or row.views_24h <= 0:
        return None
    shares = row.shares or 0.0
    saves = row.saves or 0.0
    return (shares + saves) / max(1.0, row.views_24h)


def _is_valid(row: PostRow) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    # Treat explicit invalid decision as invalid.
    if row.decision.strip().lower() == "invalid":
        return False, missing

    # Minimum metrics for rollups.
    if row.views_24h is None:
        missing.append("views_24h")
    if row.completion_pct is None:
        missing.append("completion_pct")
    if row.loop_pct is None:
        missing.append("loop_pct")
    if row.duration_sec is None:
        missing.append("duration_sec")
    if row.avg_view_duration_sec is None:
        missing.append("avg_view_duration_sec")

    return (len(missing) == 0), missing


def _compute_scores(rows: List[PostRow]) -> Dict[int, float]:
    """Compute composite scores per row index within each comparison set.

    Comparison set = (platform, duration_band, block_id).
    """

    # Collect metrics per row.
    rr: List[Optional[float]] = []
    cc: List[Optional[float]] = []
    ll: List[Optional[float]] = []
    ss: List[Optional[float]] = []
    for r in rows:
        rr.append(_retention_ratio(r))
        cc.append(r.completion_pct)
        ll.append(r.loop_pct)
        ss.append(_save_share_rate(r))

    # Group indices.
    groups: Dict[Tuple[str, str, str], List[int]] = {}
    for idx, r in enumerate(rows):
        key = (r.platform, _duration_band(r.duration_sec), r.block_id)
        groups.setdefault(key, []).append(idx)

    scores: Dict[int, float] = {}
    for _, idxs in groups.items():
        # Build vectors, dropping None by replacing with group median after normalization.
        def vec(vals: List[Optional[float]]) -> List[Optional[float]]:
            return [vals[i] for i in idxs]

        rr_v = vec(rr)
        cc_v = vec(cc)
        ll_v = vec(ll)
        ss_v = vec(ss)

        def norm(v: List[Optional[float]]) -> List[float]:
            present = [x for x in v if x is not None]
            if not present:
                return [0.5 for _ in v]
            n_present = _robust_norm([float(x) for x in present])
            # Map back, using 0.5 for missing.
            it = iter(n_present)
            out: List[float] = []
            for x in v:
                out.append(next(it) if x is not None else 0.5)
            return out

        R = norm(rr_v)
        C = norm(cc_v)
        L = norm(ll_v)
        S = norm(ss_v)

        for local_pos, idx in enumerate(idxs):
            score = 0.35 * R[local_pos] + 0.25 * C[local_pos] + 0.20 * L[local_pos] + 0.20 * S[local_pos]
            scores[idx] = float(score)

    return scores


def _win_rate(rows: List[PostRow]) -> float:
    """Heuristic win rate for v1.

    Because posts_export.csv doesn't carry WIN/NEUTRAL/LOSS explicitly in the minimal contract,
    we compute win_rate from the decision label:
    - win: keep|scale
    - not win: iterate|kill
    """

    wins = 0
    total = 0
    for r in rows:
        d = r.decision.strip().lower()
        if d == "invalid":
            continue
        if d not in {"keep", "iterate", "kill", "scale"}:
            continue
        total += 1
        if d in {"keep", "scale"}:
            wins += 1
    return 0.0 if total == 0 else wins / total


def _group_rollups(
    week_id: str,
    rows: List[PostRow],
    scores_by_idx: Dict[int, float],
    group_field: str,
) -> List[Dict[str, Any]]:
    """Build rollup dict rows.

    group_field: "hook_type" or "vertical".
    """

    grouped: Dict[Tuple[str, str, str, str], List[int]] = {}
    for idx, r in enumerate(rows):
        key = (r.platform, _duration_band(r.duration_sec), r.block_id, getattr(r, group_field))
        grouped.setdefault(key, []).append(idx)

    out: List[Dict[str, Any]] = []
    for (platform, band, block_id, group_val), idxs in sorted(grouped.items(), key=lambda x: x[0]):
        g_rows = [rows[i] for i in idxs]
        completions = [rows[i].completion_pct for i in idxs if rows[i].completion_pct is not None]
        loops = [rows[i].loop_pct for i in idxs if rows[i].loop_pct is not None]
        ret = [_retention_ratio(rows[i]) for i in idxs if _retention_ratio(rows[i]) is not None]
        ssr = [_save_share_rate(rows[i]) for i in idxs if _save_share_rate(rows[i]) is not None]
        score_vals = [scores_by_idx.get(i) for i in idxs if i in scores_by_idx]

        row: Dict[str, Any] = {
            "week_id": week_id,
            "platform": platform,
            "duration_band": band,
            "block_id": block_id,
            group_field: group_val,
            f"{group_field}_samples" if group_field != "hook_type" else "hook_samples": len(idxs),
        }

        # Column names must match csv_appendix_schema.*
        if group_field == "hook_type":
            row.update(
                {
                    "hook_samples": len(idxs),
                    "hook_win_rate": _win_rate(g_rows),
                    "hook_median_completion": median(completions) if completions else None,
                    "hook_median_loop": median(loops) if loops else None,
                    "hook_median_retention_ratio": median(ret) if ret else None,
                    "hook_median_save_share_rate": median(ssr) if ssr else None,
                    "hook_score_median": median([float(x) for x in score_vals if x is not None]) if score_vals else None,
                }
            )
        elif group_field == "vertical":
            row.update(
                {
                    "vertical_samples": len(idxs),
                    "vertical_win_rate": _win_rate(g_rows),
                    "vertical_median_completion": median(completions) if completions else None,
                    "vertical_median_loop": median(loops) if loops else None,
                    "vertical_median_retention_ratio": median(ret) if ret else None,
                    "vertical_median_save_share_rate": median(ssr) if ssr else None,
                    "vertical_score_median": median([float(x) for x in score_vals if x is not None]) if score_vals else None,
                }
            )
        else:
            raise ValueError(f"unsupported group_field: {group_field}")

        out.append(row)
    return out


def _write_hooks_rollup(path: Path, rows: List[Dict[str, Any]]) -> None:
    cols = [
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            out = dict(r)
            for k in cols:
                if isinstance(out.get(k), float) or out.get(k) is None:
                    out[k] = _format_float(out.get(k))
            w.writerow(out)


def _write_verticals_rollup(path: Path, rows: List[Dict[str, Any]]) -> None:
    cols = [
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            out = dict(r)
            for k in cols:
                if isinstance(out.get(k), float) or out.get(k) is None:
                    out[k] = _format_float(out.get(k))
            w.writerow(out)


def _compute_date_range(rows: List[PostRow]) -> Optional[str]:
    ds: List[dt.date] = []
    for r in rows:
        try:
            ds.append(dt.date.fromisoformat(r.date))
        except Exception:
            continue
    if not ds:
        return None
    return f"{min(ds).isoformat()}..{max(ds).isoformat()}"


def _write_dataset_health(
    path: Path,
    *,
    week_id: str,
    posts_source: str,
    posts_range: Optional[str],
    total_posts: int,
    valid_posts: int,
    invalid_posts: int,
    missing_metrics_rate: float,
    top_invalid_reasons: List[str],
    drift_flags: List[str],
    incident_flags: List[str],
    notes: str,
    computed_at_utc: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "week_id": week_id,
        "posts_source": posts_source,
        "posts_range": posts_range or "TBD",
        "counts": {
            "total_posts": total_posts,
            "valid_posts": valid_posts,
            "invalid_posts": invalid_posts,
        },
        "rates": {
            "invalid_rate": 0.0 if total_posts == 0 else round(invalid_posts / total_posts, 4),
            "missing_metrics_rate": round(missing_metrics_rate, 4),
        },
        "top_invalid_reasons": top_invalid_reasons,
        "drift_flags": drift_flags,
        "incident_flags": incident_flags,
        "notes": notes,
        "computed_at_utc": computed_at_utc,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_run_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_run_paths(run_json_path: Path) -> Tuple[str, Path, Path, Path, Path, str]:
    run = _load_run_json(run_json_path)
    week_id = str(run.get("week_id") or "").strip()
    if not week_id:
        raise SystemExit("run.json missing week_id")

    posts_source = str(((run.get("inputs") or {}).get("posts_source")) or "UNKNOWN").strip()
    posts_range = str(((run.get("inputs") or {}).get("posts_range")) or "").strip() or None

    files = (((run.get("inputs") or {}).get("files")) or {})
    def rp(key: str) -> Path:
        rel = files.get(key)
        if not rel:
            raise SystemExit(f"run.json missing inputs.files.{key}")
        return (run_json_path.parent / str(rel)).resolve()

    return week_id, rp("posts_export"), rp("hooks_rollup"), rp("verticals_rollup"), rp("dataset_health"), posts_source


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Aggregate weekly inputs from posts_export.csv")
    ap.add_argument("--run-json", required=True, help="Path to runs/<week>/run.json")
    ap.add_argument("--computed-at-utc", default=None, help="Override computed_at_utc (ISO 8601).")
    ap.add_argument("--low-sample-threshold", type=int, default=10, help="Add a drift flag and note when valid_posts < N")
    args = ap.parse_args(argv)

    run_json_path = Path(args.run_json).resolve()
    if not run_json_path.exists():
        raise SystemExit(f"run.json not found: {run_json_path}")

    week_id, posts_export, hooks_rollup, verticals_rollup, dataset_health, posts_source = _resolve_run_paths(run_json_path)
    if not posts_export.exists():
        raise SystemExit(f"posts_export.csv not found: {posts_export}")

    all_rows = _parse_posts_csv(posts_export)
    total_posts = len(all_rows)

    invalid_reasons: List[str] = []
    missing_metrics_count = 0
    valid_rows: List[PostRow] = []

    for r in all_rows:
        is_valid, missing = _is_valid(r)
        if missing:
            missing_metrics_count += 1
        if is_valid:
            valid_rows.append(r)
        else:
            reason = _extract_invalid_reason(r.decision, r.notes, missing)
            if reason:
                invalid_reasons.append(reason)

    valid_posts = len(valid_rows)
    invalid_posts = total_posts - valid_posts
    missing_metrics_rate = 0.0 if total_posts == 0 else missing_metrics_count / total_posts

    # Top invalid reasons (stable ordering)
    reason_counts: Dict[str, int] = {}
    for r in invalid_reasons:
        reason_counts[r] = reason_counts.get(r, 0) + 1
    top_invalid = [k for k, _ in sorted(reason_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:5]

    drift_flags: List[str] = []
    incident_flags: List[str] = []

    note_parts: List[str] = []
    if valid_posts < int(args.low_sample_threshold):
        drift_flags.append("low_sample_size")
        note_parts.append(f"LOW CONFIDENCE: valid_posts={valid_posts} below threshold={int(args.low_sample_threshold)}")
    if any(_duration_band(r.duration_sec) == "other" for r in valid_rows):
        drift_flags.append("duration_out_of_band")
        note_parts.append("Some valid rows fall outside preferred duration bands; comparability reduced.")

    computed_at_utc = args.computed_at_utc or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    posts_range = _compute_date_range(all_rows)

    # Compute rollups.
    scores = _compute_scores(valid_rows)
    hooks = _group_rollups(week_id, valid_rows, scores, "hook_type")
    verticals = _group_rollups(week_id, valid_rows, scores, "vertical")

    _write_hooks_rollup(hooks_rollup, hooks)
    _write_verticals_rollup(verticals_rollup, verticals)
    _write_dataset_health(
        dataset_health,
        week_id=week_id,
        posts_source=posts_source,
        posts_range=posts_range,
        total_posts=total_posts,
        valid_posts=valid_posts,
        invalid_posts=invalid_posts,
        missing_metrics_rate=missing_metrics_rate,
        top_invalid_reasons=top_invalid,
        drift_flags=drift_flags,
        incident_flags=incident_flags,
        notes=(" ".join(note_parts)).strip() or "Dataset health computed.",
        computed_at_utc=computed_at_utc,
    )

    print(f"OK week_id={week_id} total={total_posts} valid={valid_posts} invalid={invalid_posts}")
    print(f"Wrote {hooks_rollup}")
    print(f"Wrote {verticals_rollup}")
    print(f"Wrote {dataset_health}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
