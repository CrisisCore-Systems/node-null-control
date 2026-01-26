# Signal Dashboard v01 — Component Library

Contract: v01 dashboards use only these components. New components require a version bump.

---

## Widget types

### 1. Metric Card

Single KPI display with optional trend indicator.

**Use for:** Key metrics that need at-a-glance visibility.

**Configuration:**

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | Widget title |
| metric_key | string | yes | Key for the metric value |
| format | string | no | Display format (number, percent, duration) |
| show_trend | boolean | no | Show trend indicator |
| trend_threshold | number | no | Threshold for trend significance |

**Example:**

```json
{
  "widget_type": "metric_card",
  "config": {
    "title": "Avg Completion",
    "metric_key": "avg_completion_rate",
    "format": "percent",
    "show_trend": true,
    "trend_threshold": 5
  }
}
```

---

### 2. Trend Chart

Time-series visualization.

**Use for:** Showing metric changes over time.

**Configuration:**

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | Widget title |
| chart_type | string | no | line, bar, area (default: line) |
| time_range | string | no | 1w, 2w, 4w, 8w (default: 4w) |
| metrics | array | yes | Metrics to display |
| show_legend | boolean | no | Show chart legend |

**Example:**

```json
{
  "widget_type": "trend_chart",
  "config": {
    "title": "Performance Trend",
    "chart_type": "line",
    "time_range": "4w",
    "metrics": ["retention", "completion"],
    "show_legend": true
  }
}
```

---

### 3. Ranking Table

Sorted list of items with scores.

**Use for:** Top/bottom performers, leaderboards.

**Configuration:**

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | Widget title |
| limit | number | no | Max rows to display (default: 10) |
| columns | array | yes | Columns to display |
| sort_by | string | no | Sort column |
| sort_order | string | no | asc or desc (default: desc) |

**Example:**

```json
{
  "widget_type": "ranking_table",
  "config": {
    "title": "Top Verticals",
    "limit": 5,
    "columns": ["rank", "name", "score", "trend"],
    "sort_by": "score",
    "sort_order": "desc"
  }
}
```

---

### 4. Health Indicator

System health status display.

**Use for:** Overall system status, data freshness, alerts.

**Configuration:**

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | yes | Widget title |
| show_details | boolean | no | Show detailed status |
| checks | array | no | Specific health checks to display |

**Example:**

```json
{
  "widget_type": "health_indicator",
  "config": {
    "title": "System Health",
    "show_details": true,
    "checks": ["data_freshness", "api_status", "drift_flags"]
  }
}
```

---

## Layout system

### Grid-based layout

The dashboard uses a responsive grid system:

- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 3 columns (or custom)

Widget positioning uses `row` and `col` with optional `width` and `height` for spanning.

### Responsive behavior

Widgets automatically reflow on smaller screens while maintaining relative order.

---

## Theming

### Available themes

| Theme | Description |
| --- | --- |
| light | Light background, dark text |
| dark | Dark background, light text |
| system | Follow system preference |

### Color palette

All themes use the same semantic color tokens:

- `--color-primary`: Primary accent
- `--color-success`: Positive indicators
- `--color-warning`: Caution indicators
- `--color-danger`: Negative indicators
- `--color-muted`: Secondary text
