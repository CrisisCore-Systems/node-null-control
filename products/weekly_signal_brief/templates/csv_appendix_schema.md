# Weekly Signal Brief Appendix CSV (v01) — Schema

Filename convention:

- `NNASSET-0001_weekly-signal-brief_YYYY-Www_v01_appendix.csv`

Goal:

- Flat file, ingestion-friendly.
- Explicit repetition of `week_id` for row-level joins.

Important note:

A strict CSV normally has one header row.
The appendix is delivered as **four logical tables** inside one file (each table has its own header), separated by a blank line.

This format imports cleanly into spreadsheets and is still automation-friendly as long as the parser reads table sections.

If you need strict single-header DB ingestion, split the appendix into four CSVs downstream.

---

## Table 1 — Hook rollup

Header:

```
week_id,platform,duration_band,block_id,hook_type,hook_samples,hook_win_rate,hook_median_completion,hook_median_loop,hook_median_retention_ratio,hook_median_save_share_rate,hook_score_median
```

Example row:

```
2026-W04,yt_shorts,20-35,BLK-001,H1,12,0.58,0.41,0.12,0.93,0.017,0.62
```

---

## Table 2 — Vertical rollup

Header:

```
week_id,platform,duration_band,block_id,vertical,vertical_samples,vertical_win_rate,vertical_median_completion,vertical_median_loop,vertical_median_retention_ratio,vertical_median_save_share_rate,vertical_score_median
```

Example row:

```
2026-W04,yt_shorts,20-35,BLK-001,AIThreat,9,0.44,0.38,0.11,0.90,0.012,0.55
```

---

## Table 3 — Decisions

Header:

```
week_id,decision_type,pattern_type,pattern_id,block_id,evidence_summary,next_action,followup_week
```

Example row:

```
2026-W04,kill,hook,H7,BLK-001,"below-baseline completion and saves across min samples",retire,2026-W05
```

---

## Table 4 — Dataset summary

Header:

```
week_id,dataset_total_posts,dataset_valid_posts,dataset_invalid_posts,invalid_rate,missing_metrics_rate,drift_flags,incident_flags
```

Example row:

```
2026-W04,34,29,5,0.147,0.000,"none","none"
```
