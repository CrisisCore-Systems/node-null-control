# Weekly Signal Brief v01 — Template Variables

Contract: v01 templates use only these variables. New variables require a version bump.

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

- `{{hook_1}}`
- `{{hook_1_samples}}`
- `{{hook_1_win_rate}}`
- `{{hook_1_median_completion}}`
- `{{hook_1_median_loop}}`
- `{{hook_1_median_retention_ratio}}`
- `{{hook_1_median_save_share_rate}}`
- `{{hook_1_why}}`

- `{{hook_2}}`
- `{{hook_2_samples}}`
- `{{hook_2_win_rate}}`
- `{{hook_2_median_completion}}`
- `{{hook_2_median_loop}}`
- `{{hook_2_median_retention_ratio}}`
- `{{hook_2_median_save_share_rate}}`
- `{{hook_2_why}}`

- `{{hook_3}}`
- `{{hook_3_samples}}`
- `{{hook_3_win_rate}}`
- `{{hook_3_median_completion}}`
- `{{hook_3_median_loop}}`
- `{{hook_3_median_retention_ratio}}`
- `{{hook_3_median_save_share_rate}}`
- `{{hook_3_why}}`

Top verticals (n = 1..3):

- `{{vertical_1}}`
- `{{vertical_1_samples}}`
- `{{vertical_1_win_rate}}`
- `{{vertical_1_median_completion}}`
- `{{vertical_1_median_loop}}`
- `{{vertical_1_median_retention_ratio}}`
- `{{vertical_1_median_save_share_rate}}`
- `{{vertical_1_why}}`

- `{{vertical_2}}`
- `{{vertical_2_samples}}`
- `{{vertical_2_win_rate}}`
- `{{vertical_2_median_completion}}`
- `{{vertical_2_median_loop}}`
- `{{vertical_2_median_retention_ratio}}`
- `{{vertical_2_median_save_share_rate}}`
- `{{vertical_2_why}}`

- `{{vertical_3}}`
- `{{vertical_3_samples}}`
- `{{vertical_3_win_rate}}`
- `{{vertical_3_median_completion}}`
- `{{vertical_3_median_loop}}`
- `{{vertical_3_median_retention_ratio}}`
- `{{vertical_3_median_save_share_rate}}`
- `{{vertical_3_why}}`

---

## Losers

Bottom hooks (n = 1..3):

- `{{hook_loser_1}}`
- `{{hook_loser_1_samples}}`
- `{{hook_loser_1_win_rate}}`
- `{{hook_loser_1_evidence}}`
- `{{hook_loser_1_reco}}`

- `{{hook_loser_2}}`
- `{{hook_loser_2_samples}}`
- `{{hook_loser_2_win_rate}}`
- `{{hook_loser_2_evidence}}`
- `{{hook_loser_2_reco}}`

- `{{hook_loser_3}}`
- `{{hook_loser_3_samples}}`
- `{{hook_loser_3_win_rate}}`
- `{{hook_loser_3_evidence}}`
- `{{hook_loser_3_reco}}`

Bottom verticals (n = 1..3):

- `{{vertical_loser_1}}`
- `{{vertical_loser_1_samples}}`
- `{{vertical_loser_1_win_rate}}`
- `{{vertical_loser_1_evidence}}`
- `{{vertical_loser_1_reco}}`

- `{{vertical_loser_2}}`
- `{{vertical_loser_2_samples}}`
- `{{vertical_loser_2_win_rate}}`
- `{{vertical_loser_2_evidence}}`
- `{{vertical_loser_2_reco}}`

- `{{vertical_loser_3}}`
- `{{vertical_loser_3_samples}}`
- `{{vertical_loser_3_win_rate}}`
- `{{vertical_loser_3_evidence}}`
- `{{vertical_loser_3_reco}}`

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

- `{{block_1_id}}`
- `{{block_1_hypothesis}}`
- `{{block_1_primary_metric}}`
- `{{block_1_variable}}`
- `{{block_1_sample_plan}}`
- `{{block_1_stop}}`

- `{{block_2_id}}`
- `{{block_2_hypothesis}}`
- `{{block_2_primary_metric}}`
- `{{block_2_variable}}`
- `{{block_2_sample_plan}}`
- `{{block_2_stop}}`

---

## Appendix (optional)

- `{{analytics_schema_version}}`
- `{{scoring_version}}`
- `{{drift_notes}}`
- `{{incident_notes}}`
