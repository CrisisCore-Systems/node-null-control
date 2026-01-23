# Monetization Asset Schema

This schema defines **asset identity**, **lifecycle**, and **routing compatibility** for the Hybrid Monetization Engine.

Scope:

- Assets are monetizable outputs (products, datasets, services, platforms).
- Assets are downstream of signal trust.
- Asset telemetry is separate from content analytics.

Related:

- Hybrid router: [monetization/architecture.md](../architecture.md)
- Product surface doctrine: [monetization/product_engine.md](../product_engine.md)
- Registry (single source of truth): [monetization/assets/registry.md](registry.md)
- Signal analytics (inputs): [analytics/schema.md](../../analytics/schema.md)

---

## 0) Definitions

- **Asset**: a sellable/licensable unit produced by the system.
- **Surface**: the monetization execution channel (`product`, `data`, `service`, `platform`).
- **Routing compatibility**: tags that determine where an asset can be routed by the Hybrid Router.

---

## 1) Identity

### 1.1 Required identity fields

- `asset_id` (string, stable)
- `asset_slug` (string, stable)
- `asset_version` (string, version)

Rules:

- `asset_id` MUST be unique and never reused.
- `asset_slug` MUST be URL-safe and stable.
- `asset_version` MUST be bumped when buyer expectation changes.

Recommended `asset_id` pattern:

- `NNASSET-<asset_slug>`

### 1.2 Optional aliases

These fields are allowed if a surface expects legacy naming:

- `product_id` (alias of `asset_id`)
- `dataset_id` (alias of `asset_id`)
- `service_id` (alias of `asset_id`)
- `platform_id` (alias of `asset_id`)

Rule: if aliases exist, they MUST equal `asset_id`.

---

## 2) Routing compatibility

### 2.1 Required routing tags

- `surface_type`: `product | data | service | platform`
- `value_type`: `attention | pattern | data | system | infrastructure`
- `risk_level`: `low | medium | high`
- `monetization_fit`: `product | data | service | platform | none`

Constraints:

- `monetization_fit: none` means the output is not monetizable and must not be routed.
- `surface_type` and `monetization_fit` should generally match.
- Assets with `risk_level: high` require explicit governance approval and can be disabled by default.

### 2.2 Surface compatibility matrix

- Product surface: `value_type` is usually `system` (sometimes `pattern` if packaged as a product)
- Data surface: `value_type` is usually `data` or `pattern`
- Service surface: `value_type` is usually `system` (trust-scarce)
- Platform surface: `value_type` is usually `infrastructure`

---

## 3) Lifecycle

### 3.1 Allowed statuses

- `draft`: idea exists; not routable; not sellable
- `review`: governance + ops review in progress
- `active`: routable + sellable
- `deprecated`: not promoted; may be fulfilled for existing buyers
- `retired`: must not be sold, routed, or referenced

### 3.2 State transitions (default)

```text
draft → review → active → deprecated → retired
```

Rules:

- Only `active` assets can appear in routing outputs.
- Any governance violation forces immediate transition to `deprecated` or `retired`.

---

## 4) Governance requirements

Each asset MUST declare governance review fields:

- `governance_review_status`: `pending | approved | rejected`
- `governance_review_date`
- `policy_risk_notes`

Rules:

- `active` assets MUST have `governance_review_status: approved`.
- Any asset that pressures content incentives must be quarantined (see Hybrid kill switches).

---

## 5) Telemetry requirements

### 5.1 Separation rule

Monetization telemetry MUST NOT be mixed with content analytics inputs (see [analytics/schema.md](../../analytics/schema.md)).

### 5.2 Required telemetry linkage

Every monetization event should reference:

- `asset_id`
- `surface_type`
- `conversion_type`
- `revenue`, `cost`, `margin` (where applicable)
- attribution `confidence`

Recommended alignment with Hybrid telemetry:

```yaml
hybrid_event_id:
timestamp:

surface_type:
asset_id:

source_signal_id:
source_pattern_id:

conversion_type:
revenue:
cost:
margin:

confidence:
```

---

## 6) Minimal machine-readable schema (YAML)

This is the canonical field set used by the registry.

```yaml
asset_id: string
asset_slug: string
asset_version: string

asset_name: string
one_sentence_promise: string

deliverable_format: pdf | dashboard | api | dataset | report | workshop | deployment

audience_icp: string

surface_type: product | data | service | platform
value_type: attention | pattern | data | system | infrastructure
risk_level: low | medium | high
monetization_fit: product | data | service | platform | none

lifecycle_status: draft | review | active | deprecated | retired
lifecycle_effective_date: YYYY-MM-DD

source_signal_ids: string[]
source_pattern_ids: string[]

pricing_model: one_time | subscription | license | usage
price_band: string
currency: string

delivery_channel: string

telemetry_enabled: boolean
telemetry_namespace: hybrid | product | data | service | platform

owner: string
runbook_link: string

governance_review_status: pending | approved | rejected
governance_review_date: YYYY-MM-DD | TBD
policy_risk_notes: string

kill_switch_ready: boolean
kill_switch_notes: string
```

---

## 7) Validation checks (ops-grade)

An asset entry fails validation if:

- `asset_id` is missing, duplicated, or changed retroactively
- `lifecycle_status: active` but `governance_review_status != approved`
- `monetization_fit: none` but `telemetry_enabled: true`
- `surface_type` conflicts with `monetization_fit` without explicit notes
- `risk_level: high` is set without explicit approval notes

---

## 8) Compatibility notes (v1)

For Hybrid v1 (Product + Data enabled):

- `surface_type: product` and `surface_type: data` assets may be moved to `review`/`active` once governance approves.
- `surface_type: service` and `surface_type: platform` assets should remain `draft` by default until explicitly enabled by the Hybrid phase plan.
