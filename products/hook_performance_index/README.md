# Hook Performance Index v01 (Deliverable System)

Asset: `NNASSET-hook-performance-index` (see [monetization/assets/registry.md](../../monetization/assets/registry.md))

This product is a weekly, machine-generated index of which **hook types** are performing best (by a composite score and supporting medians).

Principles:

- Templates are stable.
- Runs are immutable snapshots.
- This is downstream of analytics; it must not contaminate signal.

## Folder structure

```text
products/
  hook_performance_index/
    README.md
    templates/
      hook_index_template.md
      hook_index_template.html
      hook_index_styles.css
      hook_index_variables.md
    runs/
      YYYY-Www/
        inputs/
        outputs/
        run.json
```

## Inputs (minimum contract)

A weekly run must include:

- `inputs/hooks_rollup.csv`
- `inputs/dataset_health.json` (optional but recommended for confidence notes)

You can generate `hooks_rollup.csv` via:

- `python scripts/aggregate_weekly_inputs.py --run-json products/weekly_signal_brief/runs/YYYY-Www/run.json`

Then copy the resulting rollups into this product run’s `inputs/` folder.

## Build

- `python scripts/build_hook_performance_index.py --run-json products/hook_performance_index/runs/YYYY-Www/run.json`

Outputs write to `build/hook_performance_index/YYYY-Www/` (local/CI artifacts).
