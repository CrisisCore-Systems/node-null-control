# Monetization Asset Registry (SSOT)

Canonical inventory of **all monetizable assets**.

If not in this registry: not routable, not sellable, not in telemetry.

Hard boundaries:

- Governance: [docs/01_rules.md](../../docs/01_rules.md)
- Workflow: [docs/02_workflow.md](../../docs/02_workflow.md)
- Analytics (signal): [analytics/schema.md](../../analytics/schema.md)
- Hybrid router: [monetization/architecture.md](../architecture.md)
- Product surface doctrine: [monetization/product_engine.md](../product_engine.md)
- Asset schema (this folder): [monetization/assets/schema.md](schema.md)

---

## 0) Rules

- This file is the **single source of truth** for asset identity.
- All monetization telemetry events must reference `asset_id` from this registry.
- No asset may be marked `active` unless the validation gate passes: [monetization/assets/validation.md](validation.md)
- Never store credentials, customer data, or personal identifiers here.
- Never mix monetization asset data into the content analytics decision engine.

---

## 1) Identity conventions

### Required identifiers

- `asset_id`: stable identifier (never reused)
- `asset_version`: version of the deliverable/promise
- `asset_slug`: human-readable stable slug

Recommended format:

- `asset_id`: `NNASSET-<asset_slug>`
- `asset_version`: `v01`, `v02`, …

Examples:

- `NNASSET-weekly-signal-brief` / `v01`
- `NNASSET-hook-performance-index` / `v01`

### Routing tags (required)

Every asset must declare the hybrid routing tags:

- `surface_type`: `product | data | service | platform`
- `value_type`: `attention | pattern | data | system | infrastructure`
- `risk_level`: `low | medium | high`
- `monetization_fit`: `product | data | service | platform | none`

---

## 2) Lifecycle model (high-level)

Asset lifecycle statuses:

- `draft` → `review` → `active` → `deprecated` → `retired`

Rules:

- Only `active` assets may be routed in packaging or sold.
- `deprecated` assets may be fulfilled for existing buyers but must not be promoted.
- `retired` assets must not be sold or referenced by routing logic.

---

## 3) Registry fields (minimum)

Each asset entry MUST include:

- Identity: `asset_id`, `asset_slug`, `asset_version`
- Surface + routing: `surface_type`, `value_type`, `risk_level`, `monetization_fit`
- Description: `asset_name`, `one_sentence_promise`, `deliverable_format`
- Source: `source_pattern_ids`, `source_signal_ids` (or explicit `none`)
- Governance: `governance_review_status`, `governance_review_date`, `policy_risk_notes`
- Commercials: `pricing_model`, `price_band`, `currency`, `delivery_channel`
- Ops: `owner`, `runbook_link`, `telemetry_enabled`, `kill_switch_ready`

Optional but recommended:

- `icp` (ideal customer profile)
- `support_load` (low/med/high)
- `cost_model` (fixed/variable)
- `margin_target`

---

## 4) Add / change process

### New asset

1. Create an entry under **Registry** using the template.
2. Ensure routing tags are consistent with [monetization/architecture.md](../architecture.md).
3. Pass governance review (must be `approved`).
4. Enable telemetry mapping (hybrid + surface-specific).
5. Only then set `lifecycle_status: active`.

### Version bump rules

Bump `asset_version` when you change:

- deliverable contents in a way that changes buyer expectation
- delivery format (PDF → dashboard)
- pricing model

Create a new `asset_id` if:

- you change the promise/category so much it’s a different product
- you change the surface type (e.g., product → platform)

---

## 5) Registry

> Keep entries small, structured, and machine-readable.

### 5.1 Entry template

```yaml
asset_id:
asset_slug:
asset_version:

asset_name:
one_sentence_promise:

deliverable_format: pdf | dashboard | api | dataset | report | workshop | deployment

audience_icp:

surface_type: product | data | service | platform
value_type: attention | pattern | data | system | infrastructure
risk_level: low | medium | high
monetization_fit: product | data | service | platform | none

lifecycle_status: draft | review | active | deprecated | retired
lifecycle_effective_date:

source_signal_ids: []
source_pattern_ids: []

pricing_model: one_time | subscription | license | usage
price_band:
currency:

delivery_channel:

telemetry_enabled: true | false
telemetry_namespace: hybrid | product | data | service | platform

owner:
runbook_link:

validation:
  last_check_utc: ""
  status: pending | pass | fail
  checked_by: operator | reviewer | governor
  run_id: "VAL-YYYY-MM-DD-<short>"
  notes: ""

integrity:
  entry_hash_sha256: ""

governance_review_status: pending | approved | rejected
governance_review_date:
policy_risk_notes:

kill_switch_ready: true | false
kill_switch_notes:
```

### 5.2 Active assets

#### Asset_0001 — Weekly Signal Brief (active)

```yaml
asset_id: NNASSET-0001-weekly-signal-brief
asset_slug: 0001-weekly-signal-brief
asset_version: v01

asset_name: Weekly Signal Brief
one_sentence_promise: Compressed weekly intelligence on what patterns are winning and why, monetized as system output (not dopamine), without changing content incentives.

deliverable_format: pdf

audience_icp: creators | analysts | operators

surface_type: data
value_type: data
risk_level: low
monetization_fit: data

lifecycle_status: active
lifecycle_effective_date: 2026-01-22

source_signal_ids: []
source_pattern_ids: []

pricing_model: license
price_band: TBD
currency: USD

delivery_channel: Gumroad | LemonSqueezy | Shopify (digital product)

telemetry_enabled: true
telemetry_namespace: hybrid

owner: governor
runbook_link: monetization/assets/validation.md

validation:
  last_check_utc: "2026-01-23T05:16:54Z"
  status: pass
  checked_by: governor
  run_id: "VAL-2026-01-23-0001"
  notes: "Dry-run event emitted; routing remains disabled outside Forge."

integrity:
  entry_hash_sha256: "5b06dfdfb3e7b16a8c9b48b4eded45aa8d7f1e02c9a84909b42f1ae1ed69d069"

governance_review_status: approved
governance_review_date: 2026-01-22
policy_risk_notes: Data-first routing. No urgency/scarcity tactics. No guarantees. No identity dependence. Routing CTAs remain disabled outside Forge.

kill_switch_ready: true
kill_switch_notes: Quarantine if it pressures content hooks/CTAs, biases experiments, or introduces analytics contamination.
```

Dry-run hybrid telemetry event template (no revenue yet; not part of entry hash):

```yaml
hybrid_event_id: DRYRUN-2026-01-22-0001
timestamp: ""

surface_type: data
asset_id: NNASSET-0001-weekly-signal-brief

source_signal_id: ""
source_pattern_id: ""
source_surface: ""

conversion_type: view
revenue: 0
cost: 0
margin: 0

confidence: low
```

### 5.3 Planned / draft assets (v1 candidates)

#### Hook Performance Index (draft)

```yaml
asset_id: NNASSET-hook-performance-index
asset_slug: hook-performance-index
asset_version: v01

asset_name: Hook Performance Index
one_sentence_promise: A licensable index of hook performance and stability signals derived from clean experiment outputs.

deliverable_format: dataset

audience_icp: analysts | marketers | operators

surface_type: data
value_type: data
risk_level: low
monetization_fit: data

lifecycle_status: draft
lifecycle_effective_date: 2026-01-22

source_signal_ids: []
source_pattern_ids: []

pricing_model: license
price_band: TBD
currency: USD

delivery_channel: TBD

telemetry_enabled: false
telemetry_namespace: hybrid

owner: TBD
runbook_link: TBD

validation:
  last_check_utc: ""
  status: pending
  checked_by: governor
  run_id: ""
  notes: ""

integrity:
  entry_hash_sha256: ""

governance_review_status: pending
governance_review_date: TBD
policy_risk_notes: Ensure no personal data; ensure dataset export rules comply with governance.

kill_switch_ready: false
kill_switch_notes: TBD
```
