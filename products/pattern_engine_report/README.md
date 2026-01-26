# Pattern Engine Report v01

Asset: `NNASSET-0002-pattern-engine-report`

Deep-dive analysis deliverable system:

- PDF report (what buyers get)
- Raw data appendix (optional add-on / pro tier)

Principles:

- Templates are stable.
- Runs are immutable snapshots.
- Outputs can be hashed later (optional).
- Monetization outputs are downstream of analytics and must not contaminate signal.

Hard rule (immutability):

- `runs/<period>/inputs/*` is the frozen snapshot of what you used.
- `runs/<period>/outputs/*` is generated from those inputs.
- No edits after publish. Amendments become a new run folder.

Outputs policy (repo hygiene):

- `runs/**/outputs/**` are generated artifacts and must not be committed.
- Outputs belong in GitHub Releases, an external artifact store, or a private delivery bucket.
- The repo keeps: templates, `run.json`, inputs, schemas/allowlists, and a `.gitkeep` to preserve the folder.

---

## Folder structure

```text
products/
  pattern_engine_report/
    README.md
    templates/
      pattern_report_template.md
      pattern_report_template.html
      pattern_report_styles.css
      pattern_report_variables.md
      data_appendix_schema.md
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

- `templates/` contains stable, versioned templates (including the variable allowlist).
- `runs/YYYY-Www/` contains an immutable analysis run:
  - `inputs/` are the frozen data exports used to generate outputs.
  - `outputs/` are the generated deliverables.
  - `run.json` is the audit spine tying inputs → outputs → governance versions.

---

## Naming conventions

PDF:

- `NNASSET-0002_pattern-engine-report_YYYY-Www_v01.pdf`

Data appendix:

- `NNASSET-0002_pattern-engine-report_YYYY-Www_v01_data.json`

---

## Generation notes (doc-first)

This repo is documentation-first; it does not ship a build toolchain by default.

Recommended generation paths:

- Markdown → PDF via your preferred renderer (Pandoc, Typst, Google Docs export).
- HTML + CSS → PDF via your preferred renderer (Chrome print-to-PDF, wkhtmltopdf).

---

## Inputs (minimum contract)

A pattern report run must include these files:

- `patterns_export.json` (raw pattern data with metrics)
- `attention_metrics.json` (aggregated attention distribution data)
- `structural_analysis.json` (platform mechanics analysis)
- `distribution_rules.json` (derived distribution rules)
- `dataset_health.json` (counts + validity + drift flags)

---

## Report sections

The Pattern Engine Report covers:

1. **Executive Summary** — Key pattern insights and shifts
2. **Attention Mechanics** — How attention flows and distributes
3. **Structural Patterns** — System-level content structures
4. **Distribution Rules** — Platform-agnostic distribution principles
5. **Pattern Rankings** — Ranked patterns by performance
6. **Trend Analysis** — Pattern trajectory and momentum
7. **Recommendations** — Actionable pattern-based recommendations

---

## Governance

- No urgency/scarcity tactics.
- No guaranteed outcomes.
- No identity dependence.
- No manipulative framing.
- Analysis only, not exploitation strategies.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate.

---

## Monetization telemetry (minimal)

When you publish the report, log exactly one `product_event` row:

```yaml
timestamp: 2026-01-26T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0002-pattern-engine-report
period_id: 2026-W04
confidence_score: 0.3
```

This belongs to product telemetry (not content analytics inputs).
