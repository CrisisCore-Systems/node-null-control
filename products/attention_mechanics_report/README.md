# Attention Mechanics Report v01

Asset: `NNASSET-0005-attention-mechanics-report`

Structural analysis deliverable system:

- PDF report (what buyers get)
- Data appendix (optional add-on)

Principles:

- Templates are stable.
- Runs are immutable snapshots.
- Analysis only, not exploitation strategies.
- Monetization outputs are downstream of analytics and must not contaminate signal.

Hard rule (no manipulation):

- Report must not include manipulation tactics.
- No exploitation strategies or dark patterns.
- Analysis is educational and informational only.

Outputs policy (repo hygiene):

- `runs/**/outputs/**` are generated artifacts and must not be committed.
- Outputs belong in GitHub Releases, an external artifact store, or a private delivery bucket.
- The repo keeps: templates, `run.json`, inputs, schemas, and a `.gitkeep` to preserve the folder.

---

## Folder structure

```text
products/
  attention_mechanics_report/
    README.md
    templates/
      attention_report_template.md
      attention_report_variables.md
      attention_report_styles.css
      mechanics_glossary.md
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

- `templates/` contains stable, versioned templates.
- `runs/YYYY-Www/` contains an immutable analysis run.

---

## Naming conventions

PDF:

- `NNASSET-0005_attention-mechanics-report_YYYY-Www_v01.pdf`

Data appendix:

- `NNASSET-0005_attention-mechanics-report_YYYY-Www_v01_data.json`

---

## Inputs (minimum contract)

An attention mechanics report run must include:

- `attention_flow.json` (attention distribution data)
- `platform_mechanics.json` (platform-specific mechanics analysis)
- `behavioral_patterns.json` (behavioral pattern data)
- `dataset_health.json` (counts + validity + drift flags)

---

## Report sections

The Attention Mechanics Report covers:

1. **Executive Summary** — Key insights on attention mechanics
2. **Attention Flow Analysis** — How attention distributes across content
3. **Platform Mechanics** — Platform-specific attention algorithms and behaviors
4. **Behavioral Patterns** — User behavior patterns and responses
5. **Structural Analysis** — Content structure impact on attention
6. **Trend Analysis** — Changes in attention mechanics over time
7. **Implications** — What these mechanics mean (not how to exploit them)

---

## Ethical guidelines

This report follows strict ethical guidelines:

### What we include:
- Objective analysis of attention distribution
- Platform mechanic descriptions
- Behavioral pattern observations
- Structural correlations

### What we exclude:
- Manipulation tactics
- Exploitation strategies
- Dark pattern recommendations
- Addiction-inducing techniques
- Psychological manipulation methods

---

## Governance

- No manipulation tactics in content.
- No exploitation strategies.
- Analysis only, not weaponization.
- No identity dependence.
- Educational and informational purpose only.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate.

---

## Monetization telemetry (minimal)

When you publish the report, log exactly one `product_event` row:

```yaml
timestamp: 2026-01-26T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0005-attention-mechanics-report
period_id: 2026-W04
confidence_score: 0.3
```

This belongs to product telemetry (not content analytics inputs).
