# Signal Dashboard v01

Asset: `NNASSET-0004-signal-dashboard`

Real-time visualization interface system:

- Web application (what buyers get)
- Self-hosted option (advanced tier)

Principles:

- Configuration templates are stable.
- Dashboard state is ephemeral (not stored in repo).
- Monetization outputs are downstream of analytics and must not contaminate signal.
- No urgency mechanics or gamification.

Hard rule (no addiction loops):

- Dashboard must not create pressure to check constantly.
- No notifications, badges, or gamification elements.
- Metrics display is informational, not manipulative.

Outputs policy (repo hygiene):

- Configuration and templates only in repo.
- Runtime data, user sessions, and caches are never committed.
- The repo keeps: component templates, config schemas, and setup documentation.

---

## Folder structure

```text
products/
  signal_dashboard/
    README.md
    templates/
      dashboard_config.json
      dashboard_config_schema.json
      component_library.md
      widget_templates/
        metric_card.html
        trend_chart.html
        ranking_table.html
        health_indicator.html
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

- `templates/` contains stable, versioned configuration schemas and widget templates.
- `runs/YYYY-Www/` contains configuration snapshots for specific deployments.

---

## Dashboard components

### Core widgets

| Widget | Purpose | Data source |
| --- | --- | --- |
| Metric Card | Display single KPI | Real-time metrics API |
| Trend Chart | Show metric over time | Time-series data |
| Ranking Table | Display ranked items | Index data |
| Health Indicator | Show system status | Health check API |

### Layout options

- Single column (mobile)
- Two column (tablet)
- Three column (desktop)
- Custom grid

---

## Configuration schema

```json
{
  "dashboard_version": "v01",
  "dashboard_name": "",
  "refresh_interval_seconds": 300,
  "layout": "two_column",
  "widgets": [
    {
      "widget_id": "",
      "widget_type": "metric_card | trend_chart | ranking_table | health_indicator",
      "position": { "row": 0, "col": 0 },
      "data_source": "",
      "config": {}
    }
  ]
}
```

---

## Widget templates

### Metric Card

Displays a single numeric value with optional trend indicator.

```html
<div class="metric-card">
  <div class="label">{{metric_name}}</div>
  <div class="value">{{metric_value}}</div>
  <div class="trend {{trend_direction}}">{{trend_value}}</div>
</div>
```

### Trend Chart

Displays time-series data as a line or bar chart.

```html
<div class="trend-chart">
  <div class="chart-title">{{chart_title}}</div>
  <div class="chart-container" data-series="{{series_data}}"></div>
  <div class="chart-legend">{{legend}}</div>
</div>
```

### Ranking Table

Displays ranked items with scores.

```html
<div class="ranking-table">
  <table>
    <thead>
      <tr>
        <th>Rank</th>
        <th>{{item_column}}</th>
        <th>{{score_column}}</th>
      </tr>
    </thead>
    <tbody>
      {{#each items}}
      <tr>
        <td>{{rank}}</td>
        <td>{{name}}</td>
        <td>{{score}}</td>
      </tr>
      {{/each}}
    </tbody>
  </table>
</div>
```

---

## Governance

- No urgency mechanics.
- No gamification that distorts content decisions.
- No addiction loops or constant notification pressure.
- No identity dependence.
- Metrics are informational only.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate.

---

## Deployment options

### Web application (hosted)

- Managed deployment
- Automatic updates
- No infrastructure required

### Self-hosted

- Docker container
- Kubernetes helm chart
- Configuration via environment variables

---

## Monetization telemetry (minimal)

When a subscription is active, log monthly:

```yaml
timestamp: 2026-01-26T00:00:00Z
conversion_type: subscription_renewal
product_id: NNASSET-0004-signal-dashboard
subscription_period: 2026-01
confidence_score: 0.5
```

This belongs to product telemetry (not content analytics inputs).
