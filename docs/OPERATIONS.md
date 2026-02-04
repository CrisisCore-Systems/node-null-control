# Operations Manual

Complete operational workflow:
**Tracker → Weekly Run → Aggregation → Build Brief → Publish → Decision Logs**

Rules: [01_rules.md](01_rules.md)
Workflow: [02_workflow.md](02_workflow.md)

---

## 1) Operational Overview

Weekly cycle with daily checkpoints:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WEEKLY OPERATIONS CYCLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [TRACKER]          [DAILY OPS]           [WEEKLY RUN]                     │
│       │                   │                     │                           │
│       │    Publish &      │                     │                           │
│       │    Capture   ─────┤                     │                           │
│       │    Metrics        │                     │                           │
│       │         │         │                     │                           │
│       ▼         ▼         │                     │                           │
│   ┌───────────────────┐   │                     │                           │
│   │ posts_export.csv  │───┼─────────────────────┤                           │
│   │ decisions.csv     │   │                     │                           │
│   └───────────────────┘   │                     │                           │
│                           │                     ▼                           │
│                           │            [AGGREGATION]                        │
│                           │                     │                           │
│                           │    aggregate_weekly_inputs.py                   │
│                           │                     │                           │
│                           │                     ▼                           │
│                           │            ┌─────────────────┐                  │
│                           │            │ hooks_rollup    │                  │
│                           │            │ verticals_rollup│                  │
│                           │            │ dataset_health  │                  │
│                           │            └─────────────────┘                  │
│                           │                     │                           │
│                           │                     ▼                           │
│                           │            [BUILD BRIEF]                        │
│                           │                     │                           │
│                           │    build_weekly_signal_brief.py                 │
│                           │                     │                           │
│                           │                     ▼                           │
│                           │            ┌─────────────────┐                  │
│                           │            │ Weekly Signal   │                  │
│                           │            │ Brief (.md/.html│                  │
│                           │            │ /PDF)           │                  │
│                           │            └─────────────────┘                  │
│                           │                     │                           │
│                           │                     ▼                           │
│                           │              [PUBLISH]                          │
│                           │                     │                           │
│                           │            ┌─────────────────┐                  │
│                           │            │ Forge / Assets  │                  │
│                           │            │ Distribution    │                  │
│                           │            └─────────────────┘                  │
│                           │                     │                           │
│                           │                     ▼                           │
│                           │            [DECISION LOGS]                      │
│                           │                     │                           │
│                           │            ┌─────────────────┐                  │
│                           │            │ killlog.md      │                  │
│   [NEXT WEEK] ◄───────────┼────────────│ scalelog.md     │                  │
│                           │            └─────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2) Tracker (Single Source of Truth)

**Location**: Google Sheet named `NODE_NULL_TRACKER`

### Required Tabs

| Tab | Purpose |
|-----|---------|
| Posts | Every upload = one row with all metrics |
| Hooks | Hook type performance aggregation |
| Verticals | Topic performance aggregation |
| Weekly Summary | Week-over-week comparison |
| Kill/Scale Decisions | Decision audit trail |

### Minimum Posts Columns

See [analytics/schema.md](../analytics/schema.md) for full field definitions.

Core fields:
- Date, Platform, Vertical, Hook Type
- Duration (sec), Visual Style, Voice Style
- Views 1h, Views 24h
- Avg view duration, Completion %, Loop %
- Shares, Saves, Comments
- Notes, Decision (keep/iterate/kill/scale/invalid)

### Export Process

At the start of each weekly run:

1. Export the Posts tab as `posts_export.csv`
   - In Google Sheets: File → Download → Comma Separated Values (.csv)
   - Ensure UTF-8 encoding (default for Google Sheets)
   - Keep header row intact
   - Filter to the relevant date range before exporting
2. Export decisions as `decisions.csv`
   - Same process as Posts export
3. Place both in `products/weekly_signal_brief/runs/<WEEK_ID>/inputs/`

**Export requirements:**
- Column order must match schema (see [analytics/schema.md](../analytics/schema.md))
- Use ISO date format: `YYYY-MM-DD`
- Empty cells for missing metrics (not "N/A" or "-")

---

## 3) Weekly Run Setup

### Directory Structure

```
products/weekly_signal_brief/runs/<WEEK_ID>/
├── run.json           # Run configuration (week_id, inputs, outputs)
├── inputs/
│   ├── posts_export.csv
│   ├── decisions.csv
│   ├── hooks_rollup.csv      # Generated by aggregation
│   ├── verticals_rollup.csv  # Generated by aggregation
│   ├── dataset_health.json   # Generated by aggregation
│   └── template_context.json # Manual: commentary + annotations
└── outputs/
    └── .gitkeep              # Outputs are generated, not tracked
```

### run.json Schema

```json
{
  "week_id": "2026-W04",
  "inputs": {
    "posts_source": "NODE_NULL_TRACKER",
    "posts_range": "2026-01-20..2026-01-26",
    "files": {
      "posts_export": "inputs/posts_export.csv",
      "decisions": "inputs/decisions.csv",
      "hooks_rollup": "inputs/hooks_rollup.csv",
      "verticals_rollup": "inputs/verticals_rollup.csv",
      "dataset_health": "inputs/dataset_health.json",
      "template_context": "inputs/template_context.json"
    }
  },
  "outputs": {
    "brief_md": "outputs/weekly_signal_brief.md",
    "brief_html": "outputs/weekly_signal_brief.html"
  }
}
```

---

## 4) Aggregation

**Script**: `scripts/aggregate_weekly_inputs.py`

### Purpose

Converts raw `posts_export.csv` into normalized rollups for analysis.

### Run Command

```bash
python scripts/aggregate_weekly_inputs.py \
  --run-json products/weekly_signal_brief/runs/<WEEK_ID>/run.json
```

### Outputs

| File | Contents |
|------|----------|
| `hooks_rollup.csv` | Per-hook metrics: samples, win rate, medians |
| `verticals_rollup.csv` | Per-vertical metrics: samples, win rate, medians |
| `dataset_health.json` | Valid/invalid counts, missing metrics rate, drift flags |

### Validation

The script automatically:
- Excludes rows marked `INVALID`
- Flags low sample sizes
- Computes composite scores per comparison set
- Records drift indicators

---

## 5) Build Brief

**Script**: `scripts/build_weekly_signal_brief.py`

### Purpose

Renders the Weekly Signal Brief from templates and aggregated data.

### Run Command

```bash
python scripts/build_weekly_signal_brief.py \
  --run products/weekly_signal_brief/runs/<WEEK_ID>/run.json \
  --outdir build/weekly_signal_brief/<WEEK_ID> \
  --strict-context \
  --strict-csv-headers
```

### Templates

Located in `products/weekly_signal_brief/templates/`:

| File | Purpose |
|------|---------|
| `weekly_brief_template.md` | Markdown template |
| `weekly_brief_template.html` | HTML template |
| `weekly_brief_styles.css` | Styling for HTML output |
| `weekly_brief_variables.md` | Variable reference |
| `csv_appendix_schema.csv` | Schema for appendix tables |

### Outputs

Generated in `build/weekly_signal_brief/<WEEK_ID>/`:
- `weekly_signal_brief.md`
- `weekly_signal_brief.html`
- Appendix CSVs

---

## 6) Publish

### Internal Publishing

Artifacts are uploaded via GitHub Actions:

1. Push changes to trigger `.github/workflows/weekly_signal_brief_build.yml`
2. Artifacts are stored with 21-day retention
3. Download from GitHub Actions artifacts tab

### Forge Distribution

For public/customer-facing distribution:

1. Run the Forge bundle script (see [Forge Deployment](#8-forge-deployment))
2. Deploy to static host (GitHub Pages, Vercel, Cloudflare Pages)
3. Update asset registry in `monetization/assets/`

### Asset Registry

Published briefs are registered in `monetization/assets/assets.json`:

```json
{
  "assets": [
    {
      "id": "weekly_signal_brief_2026_w04",
      "type": "weekly_brief",
      "status": "published",
      "url": "..."
    }
  ]
}
```

---

## 7) Decision Logs

### Location

- `analytics/decisions/killlog.md` — Patterns/verticals that were killed
- `analytics/decisions/scalelog.md` — Patterns/verticals that were scaled

### Kill Log Format

```markdown
## 2026-W04

### Killed: [Vertical/Hook Name]

- **Reason**: Below-baseline completion + save/share after 2 iterations
- **Samples**: 8 valid samples
- **Metrics**: Completion 42% (baseline 58%), Save+Share 0.8% (baseline 1.2%)
- **Decision date**: 2026-01-26
```

### Scale Log Format

```markdown
## 2026-W04

### Scaled: [Vertical/Hook Name]

- **Reason**: Top-quartile composite score, 65% win rate, confirmed replication
- **Samples**: 12 valid samples
- **Metrics**: Completion 72%, Loop 45%, Save+Share 2.1%
- **Action**: Increase output 2x, test adjacent vertical
- **Decision date**: 2026-01-26
```

### Decision Criteria

Decisions must follow the thresholds in [analytics/schema.md](../analytics/schema.md):

| Decision | Criteria |
|----------|----------|
| **KILL** | Below-baseline completion AND save/share, no improvement after 2 iterations |
| **ITERATE** | Mixed signals (strong retention, weak distribution OR vice versa) |
| **SCALE** | Top-quartile score, ≥60% win rate, confirmed replication, no risk flags |

---

## 8) Forge Deployment

### Purpose

Forge is the public conversion interface. It must be deployed as a minimal
bundle to prevent accidentally publishing internal documentation.

### Bundle Script

Use the bundle script to create a safe deployment:

```bash
./scripts/bundle_forge.sh
```

This creates `site/` containing only:
- `forge/` directory (index.html, app.js, config.js, styles.css)
- `monetization/assets/assets.json` (if needed for asset loading)
- `api/` (if deploying to Vercel with serverless functions)

### GitHub Pages Deployment

1. Run the bundle script: `./scripts/bundle_forge.sh`
2. Configure GitHub Pages to serve from `site/` directory
3. Or use a separate `gh-pages` branch with only bundled content

### Vercel Deployment

The repository includes `vercel.json` and automatic deployment via GitHub Actions.

**Automatic deployment** (recommended):
1. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for setup instructions
2. Configure GitHub Secrets (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)
3. Push to any branch to trigger automatic deployment
4. Main branch deploys to production, other branches create preview deployments

**Manual deployment**:
1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel` (preview) or `vercel --prod` (production)

The rewrite rules in `vercel.json` route `/` to `/forge/`.

**Warning**: Direct Vercel deployment exposes the entire repository.
For production, consider using the bundle script output instead.

---

## 9) Automation (CI/CD)

### GitHub Actions Workflow

`.github/workflows/weekly_signal_brief_build.yml`:

- Triggers on push and manual dispatch
- Sets up Python 3.13 with pinned dependencies
- Runs guardrails to prevent artifact tracking
- Builds fixture artifacts for validation
- Uploads artifacts with 21-day retention

### Manual Workflow

For non-automated runs:

1. Export tracker data to `inputs/`
2. Create `run.json` with correct paths
3. Run aggregation: `python scripts/aggregate_weekly_inputs.py --run-json ...`
4. Add commentary to `template_context.json`
5. Build brief: `python scripts/build_weekly_signal_brief.py --run ...`
6. Review outputs in `build/`
7. Log decisions in `analytics/decisions/`
8. Publish via preferred channel

---

## 10) Quick Reference

### Weekly Checklist

- [ ] Export Posts tab → `posts_export.csv`
- [ ] Export decisions → `decisions.csv`
- [ ] Create/update `run.json` for the week
- [ ] Run aggregation script
- [ ] Review `dataset_health.json` for issues
- [ ] Write commentary in `template_context.json`
- [ ] Build brief
- [ ] Review outputs
- [ ] Log kill/scale decisions
- [ ] Publish brief
- [ ] Plan next week's experiments

### Key Commands

```bash
# Aggregation
python scripts/aggregate_weekly_inputs.py \
  --run-json products/weekly_signal_brief/runs/2026-W04/run.json

# Build
python scripts/build_weekly_signal_brief.py \
  --run products/weekly_signal_brief/runs/2026-W04/run.json \
  --outdir build/weekly_signal_brief/2026-W04

# Bundle Forge
./scripts/bundle_forge.sh

# Package kit for distribution
python scripts/package_weekly_signal_brief_kit.py \
  --out dist/gumroad/weekly_signal_brief_core_kit_v01.zip \
  --tier personal
```

### File Locations

| Purpose | Location |
|---------|----------|
| Rules (constitution) | `docs/01_rules.md` |
| Workflow details | `docs/02_workflow.md` |
| Analytics schema | `analytics/schema.md` |
| Run configurations | `products/weekly_signal_brief/runs/<WEEK>/` |
| Templates | `products/weekly_signal_brief/templates/` |
| Build outputs | `build/weekly_signal_brief/<WEEK>/` |
| Decision logs | `analytics/decisions/` |
| Forge interface | `forge/` |
