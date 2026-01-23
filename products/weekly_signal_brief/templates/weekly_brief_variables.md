# Weekly Signal Brief v01 — Template Variables (Allowlist)

This file is the contract.

Rule:

- The v01 templates must not introduce any `{{...}}` variables not listed here.
- If you need a new variable, bump the asset/template version and update this allowlist.

---

## Core

- `{{week_id}}`
- `{{date_range}}` (optional; if used, keep ISO dates)
- `{{platforms_included}}`
- `{{included_block_ids}}`
- `{{generated_at_utc}}`

---

## Dataset counts

- `{{dataset_total_posts}}`
- `{{dataset_valid_posts}}`
- `{{dataset_invalid_posts}}`
- `{{invalid_rate}}`

---

## Executive signal

- `{{executive_summary_paragraph}}`
- `{{shift_1}}`
- `{{shift_2}}`
- `{{shift_3}}`

---

## Dataset health

- `{{missing_metrics_rate}}`
- `{{top_invalid_reasons}}`
- `{{drift_flags}}`
- `{{incident_flags}}`
- `{{dataset_health_notes}}`

---

## Winners

Top hooks (n = 1..3):

- `{{hook_n}}`
- `{{hook_n_samples}}`
- `{{hook_n_win_rate}}`
- `{{hook_n_median_completion}}`
- `{{hook_n_median_loop}}`
- `{{hook_n_median_retention_ratio}}`
- `{{hook_n_median_save_share_rate}}`
- `{{hook_n_why}}`

Top verticals (n = 1..3):

- `{{vertical_n}}`
- `{{vertical_n_samples}}`
- `{{vertical_n_win_rate}}`
- `{{vertical_n_median_completion}}`
- `{{vertical_n_median_loop}}`
- `{{vertical_n_median_retention_ratio}}`
- `{{vertical_n_median_save_share_rate}}`
- `{{vertical_n_why}}`

---

## Losers

Bottom hooks (n = 1..3):

- `{{hook_loser_n}}`
- `{{hook_loser_n_samples}}`
- `{{hook_loser_n_win_rate}}`
- `{{hook_loser_n_evidence}}`
- `{{hook_loser_n_reco}}`

Bottom verticals (n = 1..3):

- `{{vertical_loser_n}}`
- `{{vertical_loser_n_samples}}`
- `{{vertical_loser_n_win_rate}}`
- `{{vertical_loser_n_evidence}}`
- `{{vertical_loser_n_reco}}`

---

## Decisions

Kill list:

- `{{kill_1}}`
- `{{kill_2}}`
- `{{kill_3}}`

Scale list (constraints):

- `{{scale_1}}`
- `{{scale_1_constraints}}`
- `{{scale_2}}`
- `{{scale_2_constraints}}`

Iterate list (one-variable plans):

- `{{iterate_1}}`
- `{{iterate_1_variable}}`
- `{{iterate_1_controls}}`
- `{{iterate_2}}`
- `{{iterate_2_variable}}`
- `{{iterate_2_controls}}`

- `{{threshold_citations}}`

---

## Next week plan

- `{{duration_band}}`
- `{{voice_style}}`
- `{{visual_style}}`
- `{{caption_policy}}`
- `{{hooks_version}}`

Experiment blocks (n = 1..2):

- `{{block_n_id}}`
- `{{block_n_hypothesis}}`
- `{{block_n_primary_metric}}`
- `{{block_n_variable}}`
- `{{block_n_sample_plan}}`
- `{{block_n_stop}}`

---

## Appendix (optional)

- `{{analytics_schema_version}}`
- `{{scoring_version}}`
- `{{drift_notes}}`
- `{{incident_notes}}`
