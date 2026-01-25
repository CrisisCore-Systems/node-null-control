# Weekly Signal Brief v01

Asset: `NNASSET-0001-weekly-signal-brief`

Repeatable weekly deliverable system:

- PDF brief (what buyers get)
- CSV appendix (optional add-on / pro tier / internal import)

Principles:

- Templates are stable.
- Runs are immutable snapshots.
- Outputs can be hashed later (optional).
- Monetization outputs are downstream of analytics and must not contaminate signal.

Hard rule (immutability):

- `runs/<week>/inputs/*` is the frozen snapshot of what you used.
- `runs/<week>/outputs/*` is generated from those inputs.
- No edits after publish. Amendments become a new run folder (e.g., `runs/2026-W04-amend1/`).

Outputs policy (repo hygiene):

- `runs/**/outputs/**` are generated artifacts and must not be committed.
- Outputs belong in GitHub Releases (by `week_id` / run id), an external artifact store (S3/R2/Drive), or a private delivery bucket (Gumroad/LemonSqueezy upload).
- The repo keeps: templates, `run.json`, inputs (exports/rollups), schemas/allowlists, and a `.gitkeep` to preserve the folder.

---

## Folder structure

```text
products/
  weekly_signal_brief/
    README.md
    templates/
      weekly_brief_template.md
      weekly_brief_template.html
      weekly_brief_styles.css
      weekly_brief_variables.md
      csv_appendix_schema.csv
      csv_appendix_schema.md
    runs/
      YYYY-Www/
        inputs/
        outputs/
        run.json
```

- `templates/` contains stable, versioned templates (including the variable allowlist).
- `runs/YYYY-Www/` contains an immutable weekly run:
  - `inputs/` are the frozen rollups/exports used to generate outputs.
  - `outputs/` are the generated deliverables.
  - `run.json` is the audit spine tying inputs → outputs → governance versions.

Starter run scaffold:

- `runs/2026-W04/`

---

## Naming conventions

PDF:

- `NNASSET-0001_weekly-signal-brief_YYYY-Www_v01.pdf`

CSV appendix:

- `NNASSET-0001_weekly-signal-brief_YYYY-Www_v01_appendix.csv`

Week id format:

- `YYYY-Www` (ISO-like)

---

## Generation notes (doc-first)

This repo is documentation-first; it does not ship a build toolchain by default.

Recommended generation paths (choose one):

- Markdown → PDF via your preferred renderer (Pandoc, Typst, Google Docs export).
- HTML + CSS → PDF via your preferred renderer (Chrome print-to-PDF, wkhtmltopdf).

The templates are written to be deterministic and repeatable.

Repo hygiene:

- `build/` is local-only (or CI-only) build output and must not be committed.
- Manifests (`*.manifest.json`) are artifacts by default; only commit them if you are intentionally creating test fixtures.

---

## Inputs (minimum contract)

A weekly run must include these files (exact filenames, stable schema):

- `posts_export.csv` (raw post rows for the week; includes invalids)
- `hooks_rollup.csv` (aggregated by Hook Type; valid-only)
- `verticals_rollup.csv` (aggregated by Vertical; valid-only)
- `decisions.csv` (kill/iterate/scale actions with evidence)
- `dataset_health.json` (counts + invalid rate + drift flags)

Contract notes:

- Invalid rows remain in `posts_export.csv` for auditability (see [analytics/schema.md](../../analytics/schema.md)); they are excluded from rollups.
- `run.json` must point to the exact input files used.

Recommended minimal schemas:

- `dataset_health.json` keys: `counts` (total/valid/invalid), `rates` (invalid/missing-metrics), `top_invalid_reasons`, `drift_flags`, `incident_flags`, `computed_at_utc`.
- `hooks_rollup.csv` and `verticals_rollup.csv` should be computed from valid-only rows, and should include `week_id`, `platform`, `duration_band`, `block_id`, sample counts, and median metrics.

---

## Aggregation (low-infra)

If you do not have an automated data warehouse, you can still generate the required rollups deterministically from a small weekly export.

Workflow:

1) Populate `inputs/posts_export.csv` (one row per post; keep invalid rows for auditability).
2) Run the aggregator to produce `hooks_rollup.csv`, `verticals_rollup.csv`, and `dataset_health.json`.

Command:

- `python scripts/aggregate_weekly_inputs.py --run-json products/weekly_signal_brief/runs/YYYY-Www/run.json`

Notes:

- Rollups are computed from **valid-only** rows.
- If `valid_posts` is below the default threshold (10), the script adds a `low_sample_size` drift flag and writes a clear low-confidence note into `dataset_health.json`.

---

## Governance

- No urgency/scarcity tactics.
- No guaranteed outcomes.
- No identity dependence.
- Routing CTAs stay disabled outside Forge.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate + integrity hash procedure.

---

## Monetization telemetry (minimal)

When you publish the brief, log exactly one `product_event` row for the purchase (no attribution cosplay):

```yaml
timestamp: 2026-01-23T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0001-weekly-signal-brief
week_id: 2026-W04
block_id: "TBD" # or a delimited list of included blocks
source_platform: mixed
confidence_score: 0.3
```

This belongs to product telemetry (not content analytics inputs).
