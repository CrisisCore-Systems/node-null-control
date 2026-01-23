# Weekly Signal Brief — {{week_id}} (v01)

Platforms: {{platforms_included}}

Sample counts:

- Total posts: {{dataset_total_posts}}
- Valid posts: {{dataset_valid_posts}}
- Invalid posts: {{dataset_invalid_posts}} (invalid_rate={{invalid_rate}})

Block IDs included: {{included_block_ids}}

---

## 1) Executive signal

One paragraph:

{{executive_summary_paragraph}}

Highest-confidence shifts:

- {{shift_1}}
- {{shift_2}}
- {{shift_3}}

---

## 2) Dataset health

- Missing-metrics rate: {{missing_metrics_rate}}
- Top invalid reasons: {{top_invalid_reasons}}
- Drift flags: {{drift_flags}}
- Incident flags: {{incident_flags}}

Notes:

{{dataset_health_notes}}

### 2.1 Transparency note (sample awareness)

Valid posts: {{dataset_valid_posts}}

Drift flags: {{drift_flags}}

If drift flags include `low_sample_size`, treat this week's rollups as directional signals rather than high-confidence inference.

---

## 3) Winners

### 3.1 Top hooks

| Rank | Hook Type | Samples | Win rate | Median completion | Median loop | Median retention ratio | Median save+share rate | Why it won |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | {{hook_1}} | {{hook_1_samples}} | {{hook_1_win_rate}} | {{hook_1_median_completion}} | {{hook_1_median_loop}} | {{hook_1_median_retention_ratio}} | {{hook_1_median_save_share_rate}} | {{hook_1_why}} |
| 2 | {{hook_2}} | {{hook_2_samples}} | {{hook_2_win_rate}} | {{hook_2_median_completion}} | {{hook_2_median_loop}} | {{hook_2_median_retention_ratio}} | {{hook_2_median_save_share_rate}} | {{hook_2_why}} |
| 3 | {{hook_3}} | {{hook_3_samples}} | {{hook_3_win_rate}} | {{hook_3_median_completion}} | {{hook_3_median_loop}} | {{hook_3_median_retention_ratio}} | {{hook_3_median_save_share_rate}} | {{hook_3_why}} |

### 3.2 Top verticals

| Rank | Vertical | Samples | Win rate | Median completion | Median loop | Median retention ratio | Median save+share rate | Why it won |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | {{vertical_1}} | {{vertical_1_samples}} | {{vertical_1_win_rate}} | {{vertical_1_median_completion}} | {{vertical_1_median_loop}} | {{vertical_1_median_retention_ratio}} | {{vertical_1_median_save_share_rate}} | {{vertical_1_why}} |
| 2 | {{vertical_2}} | {{vertical_2_samples}} | {{vertical_2_win_rate}} | {{vertical_2_median_completion}} | {{vertical_2_median_loop}} | {{vertical_2_median_retention_ratio}} | {{vertical_2_median_save_share_rate}} | {{vertical_2_why}} |
| 3 | {{vertical_3}} | {{vertical_3_samples}} | {{vertical_3_win_rate}} | {{vertical_3_median_completion}} | {{vertical_3_median_loop}} | {{vertical_3_median_retention_ratio}} | {{vertical_3_median_save_share_rate}} | {{vertical_3_why}} |

---

## 4) Losers

### 4.1 Bottom hooks

| Rank | Hook Type | Samples | Win rate | Evidence summary | Recommendation |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | {{hook_loser_1}} | {{hook_loser_1_samples}} | {{hook_loser_1_win_rate}} | {{hook_loser_1_evidence}} | {{hook_loser_1_reco}} |
| 2 | {{hook_loser_2}} | {{hook_loser_2_samples}} | {{hook_loser_2_win_rate}} | {{hook_loser_2_evidence}} | {{hook_loser_2_reco}} |
| 3 | {{hook_loser_3}} | {{hook_loser_3_samples}} | {{hook_loser_3_win_rate}} | {{hook_loser_3_evidence}} | {{hook_loser_3_reco}} |

### 4.2 Bottom verticals

| Rank | Vertical | Samples | Win rate | Evidence summary | Recommendation |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | {{vertical_loser_1}} | {{vertical_loser_1_samples}} | {{vertical_loser_1_win_rate}} | {{vertical_loser_1_evidence}} | {{vertical_loser_1_reco}} |
| 2 | {{vertical_loser_2}} | {{vertical_loser_2_samples}} | {{vertical_loser_2_win_rate}} | {{vertical_loser_2_evidence}} | {{vertical_loser_2_reco}} |
| 3 | {{vertical_loser_3}} | {{vertical_loser_3_samples}} | {{vertical_loser_3_win_rate}} | {{vertical_loser_3_evidence}} | {{vertical_loser_3_reco}} |

---

## 5) Decisions

### 5.1 Kill list

- {{kill_1}}
- {{kill_2}}
- {{kill_3}}

### 5.2 Scale list (constraints)

- {{scale_1}} — stays fixed: {{scale_1_constraints}}
- {{scale_2}} — stays fixed: {{scale_2_constraints}}

### 5.3 Iterate list (one-variable plans)

- {{iterate_1}} — variable changed: {{iterate_1_variable}}; controls held: {{iterate_1_controls}}
- {{iterate_2}} — variable changed: {{iterate_2_variable}}; controls held: {{iterate_2_controls}}

Threshold citations:

{{threshold_citations}}

---

## 6) Next week plan

### 6.1 Controls locked

- Duration band: {{duration_band}}
- Voice: {{voice_style}}
- Visuals: {{visual_style}}
- Caption policy: {{caption_policy}}
- Hook library version: {{hooks_version}}

### 6.2 Experiment blocks

| block_id | hypothesis | primary metric | variable changed | sample plan | stop conditions |
| --- | --- | --- | --- | --- | --- |
| {{block_1_id}} | {{block_1_hypothesis}} | {{block_1_primary_metric}} | {{block_1_variable}} | {{block_1_sample_plan}} | {{block_1_stop}} |
| {{block_2_id}} | {{block_2_hypothesis}} | {{block_2_primary_metric}} | {{block_2_variable}} | {{block_2_sample_plan}} | {{block_2_stop}} |

---

## Appendix (optional)

### Definitions snapshot

- Analytics schema version: {{analytics_schema_version}}
- Scoring/threshold version: {{scoring_version}}

### Drift notes

{{drift_notes}}

### Incident notes

{{incident_notes}}
