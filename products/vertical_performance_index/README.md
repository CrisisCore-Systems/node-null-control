# Vertical Performance Index v01

Asset: `NNASSET-0003-vertical-performance-index`

Ranked performance dataset system:

- JSON/CSV dataset (what buyers get)
- API feed (optional subscription tier)

Principles:

- Templates are stable.
- Runs are immutable snapshots.
- Data exports can be hashed for integrity.
- Monetization outputs are downstream of analytics and must not contaminate signal.

Hard rule (immutability):

- `runs/<period>/inputs/*` is the frozen snapshot of what you used.
- `runs/<period>/outputs/*` is generated from those inputs.
- No edits after publish. Amendments become a new run folder.

Outputs policy (repo hygiene):

- `runs/**/outputs/**` are generated artifacts and must not be committed.
- Outputs belong in GitHub Releases, an external artifact store, or API delivery.
- The repo keeps: templates, `run.json`, schemas, and a `.gitkeep` to preserve the folder.

---

## Folder structure

```text
products/
  vertical_performance_index/
    README.md
    templates/
      index_schema.json
      index_schema.md
      export_template.json
      api_response_schema.json
    runs/
      YYYY-Www/
        inputs/
        outputs/
        run.json
    licenses/
      LICENSE_commercial_v01.txt
      LICENSE_personal_v01.txt
      LICENSE_team_v01.txt
```

- `templates/` contains stable, versioned schemas and export templates.
- `runs/YYYY-Www/` contains an immutable weekly run:
  - `inputs/` are the frozen data used to compute the index.
  - `outputs/` are the generated datasets.
  - `run.json` is the audit spine tying inputs → outputs → governance versions.

---

## Naming conventions

Dataset export:

- `NNASSET-0003_vertical-performance-index_YYYY-Www_v01.json`
- `NNASSET-0003_vertical-performance-index_YYYY-Www_v01.csv`

---

## Inputs (minimum contract)

A vertical index run must include these files:

- `verticals_raw.csv` (raw vertical performance data)
- `retention_metrics.json` (retention and engagement data by vertical)
- `signal_stability.json` (stability scores over time)
- `dataset_health.json` (counts + validity + drift flags)

---

## Index fields

The Vertical Performance Index includes:

| Field | Type | Description |
| --- | --- | --- |
| vertical_id | string | Unique vertical identifier |
| vertical_name | string | Human-readable vertical name |
| period_id | string | Time period (YYYY-Www) |
| rank | integer | Overall rank for the period |
| performance_score | float | Composite performance score (0-100) |
| retention_score | float | Retention metric score (0-100) |
| engagement_score | float | Engagement metric score (0-100) |
| stability_score | float | Signal stability score (0-100) |
| sample_size | integer | Number of samples |
| trend | string | up / down / stable |
| confidence | string | low / medium / high |

---

## API Response Schema (subscription tier)

```json
{
  "index_version": "v01",
  "period_id": "YYYY-Www",
  "generated_at_utc": "ISO8601",
  "total_verticals": 0,
  "verticals": [
    {
      "vertical_id": "",
      "vertical_name": "",
      "rank": 0,
      "performance_score": 0.0,
      "retention_score": 0.0,
      "engagement_score": 0.0,
      "stability_score": 0.0,
      "sample_size": 0,
      "trend": "",
      "confidence": ""
    }
  ]
}
```

---

## Governance

- No personal data in exports.
- No guaranteed outcomes.
- No identity dependence.
- Export rules must comply with governance.
- Data must not corrupt experiment design.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate.

---

## Monetization telemetry (minimal)

When you deliver the index, log exactly one `product_event` row:

```yaml
timestamp: 2026-01-26T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0003-vertical-performance-index
period_id: 2026-W04
confidence_score: 0.3
```

This belongs to product telemetry (not content analytics inputs).
