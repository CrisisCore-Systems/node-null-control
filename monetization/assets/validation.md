# Asset Validation Checklist

Prevents: unapproved assets going `active`, routing violations, telemetry mismatches, incentive bleed, governance drift.

Hard rule:

- FAIL = asset cannot be marked `active`.
- FAIL = asset cannot be routed or referenced in monetization packaging.

References:

- Registry (SSOT): [monetization/assets/registry.md](registry.md)
- Asset schema: [monetization/assets/schema.md](schema.md)
- Hybrid router + kill switches: [monetization/architecture.md](../architecture.md)
- Product doctrine: [monetization/product_engine.md](../product_engine.md)
- Governance constitution: [docs/01_rules.md](../../docs/01_rules.md)

---

## 0) Validation record (required)

Create a small record in the asset’s registry entry notes (or Notes log) for every validation run.

Minimal log format:

```yaml
validation_run_id: YYYY-MM-DD_<asset_id>_<asset_version>
timestamp:
asset_id:
asset_version:
validator: governor
result: pass | fail
fail_reasons: []
notes:
```

---

## 0.1) Integrity anchor (`integrity.entry_hash_sha256`)

Purpose: create a stable, comparable fingerprint of an asset entry to detect registry drift and support change control.

Hard scope rule:

- Hash ONLY the YAML block of the asset entry (not surrounding prose).

### Canonicalization rules

- Extract the asset YAML block text exactly as it appears in [monetization/assets/registry.md](registry.md).
- Exclude these volatile fields from the hashed text:
  - `validation.last_check_utc`
  - `validation.run_id`
  - `validation.notes`
  - `integrity.entry_hash_sha256` (hash must not include itself)
  - any `last_updated` / `updated_at` style timestamps if added later
- Preserve all identity, routing, governance, and commercial fields (do hash them), including:
  - `asset_id`, `asset_slug`, `asset_version`
  - `surface_type`, `value_type`, `risk_level`, `monetization_fit`
  - pricing model fields
  - governance approval fields
- Normalize whitespace:
  - LF line endings (`\n`)
  - no trailing spaces
  - keep indentation as spaces (no tabs)

### Hash procedure

- Save the canonicalized text into a file (example): `asset_canonical.txt`.
- Compute SHA-256 of that file.
- Store the result as lowercase hex in `integrity.entry_hash_sha256` in the asset entry.

### Windows PowerShell example

```powershell
# 1) Save canonical text to .\asset_canonical.txt
# 2) Compute SHA-256 and output lowercase hex
(Get-FileHash .\asset_canonical.txt -Algorithm SHA256).Hash.ToLower()
```

---

## 1) Identity & traceability gate

PASS only if all are true:

- `asset_id` exists, is unique, and matches convention (`NNASSET-<asset_slug>`).
- `asset_slug` is stable and URL-safe.
- `asset_name` is stable (no silent renames).
- `asset_version` is recorded and correct.
- `deliverable_format` is in enum.
- Source traceability declared:
  - `source_signal_ids` and `source_pattern_ids` are present (or explicit empty arrays).
- Lifecycle is coherent:
  - If setting `lifecycle_status: active`, `lifecycle_effective_date` is set.

FAIL conditions:

- Any missing identity field.
- Any reused/changed `asset_id` for the same promise.

---

## 2) Governance gate (hard stop)

PASS only if all are true:

- Risk flags complete:
  - `risk_level` set (`low | medium | high`)
  - `policy_risk_notes` present (even if “none”)
- Forbidden claims check passed:
  - no guaranteed outcomes
  - no medical/financial advice framing
  - no deception / urgency / scarcity tactics
  - no “secret formula” positioning
- Copyright check passed (if relevant):
  - no unlicensed third-party IP embedded in deliverable
- Incentive distortion assessed:
  - explicit answer: “Could selling this change hooks/content strategy?”
  - if yes: mitigation defined or asset is quarantined
- Approval recorded:
  - `governance_review_status: approved`
  - `governance_review_date` set

FAIL conditions:

- `lifecycle_status: active` while governance is not `approved`.
- Any claim that violates [docs/01_rules.md](../../docs/01_rules.md).

---

## 3) Routing gate

PASS only if all are true:

- `surface_type` is correct (`product | data | service | platform`).
- Routing tags are internally consistent:
  - `monetization_fit` matches intent
  - `value_type` matches asset class
- Hybrid v1 constraints enforced:
  - Service + Platform are disabled by default.
  - If `surface_type` is `service` or `platform`, asset MUST NOT be set `active` unless hybrid phase explicitly enables it.
- Revenue mix sanity (if already generating revenue):
  - no surface is exceeding the >50% cap without a throttle plan

Dry check:

- For the chosen route, confirm it does not require CTAs that would alter experiment design.

FAIL conditions:

- Any route to a disabled surface.
- Any packaging plan that would require changing hooks/content incentives to sell.

---

## 4) Telemetry gate

PASS only if all are true:

- `telemetry_enabled` is explicitly `true` or `false` (no ambiguity).
- `telemetry_namespace` is explicitly set (`hybrid | product | data | service | platform`).
- Attribution confidence is declared as a field in the telemetry plan (even if weak).
- Separation confirmed:
  - monetization telemetry is stored separately from content analytics inputs in [analytics/schema.md](../../analytics/schema.md)

Dry check:

- A sample event can be written with:
  - `asset_id`, `surface_type`, `conversion_type`, `revenue/cost/margin`, `confidence`

FAIL conditions:

- Any attempt to add revenue fields into the content decision engine.

---

## 5) Activation test (preflight)

PASS only if all are true:

- A dry-run route is defined:
  - surface
  - destination (SKU/page/access method)
  - event emitted (what telemetry row is written)
- Rollback plan exists:
  - how to pause routing
  - how to set lifecycle to `deprecated`/`retired`
  - how to fulfill existing commitments (if any)
- Kill switch triggers are defined for this asset:
  - incentive distortion
  - policy risk increase
  - analytics contamination risk
  - routing drift

FAIL conditions:

- No rollback path.
- No asset-specific kill triggers.

---

## 6) Status gate (enforcement)

To set `lifecycle_status: active`, all gates (1–5) must pass.

If any gate fails:

- keep asset in `draft` or `review`
- set `telemetry_enabled: false` until fixed
- document `fail_reasons` in the validation record
