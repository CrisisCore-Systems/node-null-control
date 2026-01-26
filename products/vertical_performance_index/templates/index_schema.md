# Vertical Performance Index v01 — Schema Documentation

Contract: v01 exports use only these fields. New fields require a version bump.

---

## Root object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| index_version | string | yes | Always "v01" for this version |
| period_id | string | yes | Time period in YYYY-Www format |
| generated_at_utc | string | yes | ISO8601 timestamp of generation |
| total_verticals | integer | no | Count of verticals in the index |
| dataset_health | object | no | Health metrics for the source data |
| verticals | array | yes | Array of vertical performance objects |

---

## dataset_health object

| Field | Type | Description |
| --- | --- | --- |
| total_samples | integer | Total number of content samples |
| valid_samples | integer | Number of valid samples used |
| invalid_rate | number | Percentage of invalid samples |
| drift_flags | array | List of drift flag strings |

---

## vertical object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| vertical_id | string | yes | Unique vertical identifier |
| vertical_name | string | yes | Human-readable vertical name |
| rank | integer | yes | Overall rank for the period (1 = best) |
| performance_score | number | yes | Composite performance score (0-100) |
| retention_score | number | no | Retention metric score (0-100) |
| engagement_score | number | no | Engagement metric score (0-100) |
| stability_score | number | no | Signal stability score (0-100) |
| sample_size | integer | no | Number of samples for this vertical |
| trend | string | no | Performance trend: up / down / stable |
| confidence | string | no | Confidence level: low / medium / high |

---

## Scoring methodology

### performance_score

Composite score calculated as weighted average:
- retention_score × 0.35
- engagement_score × 0.35
- stability_score × 0.30

### confidence levels

| Level | Sample size |
| --- | --- |
| low | < 10 |
| medium | 10-50 |
| high | > 50 |

### trend determination

Trend is calculated by comparing current period score to previous period:
- **up**: current > previous + 5%
- **down**: current < previous - 5%
- **stable**: within ±5%

---

## Example export

```json
{
  "index_version": "v01",
  "period_id": "2026-W04",
  "generated_at_utc": "2026-01-26T00:00:00Z",
  "total_verticals": 3,
  "dataset_health": {
    "total_samples": 150,
    "valid_samples": 142,
    "invalid_rate": 0.053,
    "drift_flags": []
  },
  "verticals": [
    {
      "vertical_id": "ai-threat",
      "vertical_name": "AI Threat",
      "rank": 1,
      "performance_score": 87.5,
      "retention_score": 89.2,
      "engagement_score": 85.1,
      "stability_score": 88.4,
      "sample_size": 52,
      "trend": "up",
      "confidence": "high"
    }
  ]
}
```
