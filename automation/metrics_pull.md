# Metrics Pull (Telemetry)

The instrumentation layer: pull, validate, normalize, store, and reconcile metrics **compliantly** and **auditably**.

Hard boundaries: [docs/01_rules.md](../docs/01_rules.md)
Workflow reference: [docs/02_workflow.md](../docs/02_workflow.md)
Analytics definitions: [analytics/schema.md](../analytics/schema.md)
Automation wiring: [automation/wiring.md](wiring.md)

---

## 0) Non-negotiables

- **Compliant access:** official APIs, approved partners, or manual exports per Terms.
- **Privacy:** no personal data beyond aggregate analytics. Separate accounts.
- **Immutability:** raw snapshots are immutable.
- **Traceability:** every metric traces to a snapshot (run_id + source).

---

## 1) What this system measures (contract)

The tracker is the decision engine. The telemetry layer exists to reliably populate these fields (see schema):

- Views 1h
- Views 24h
- Avg view duration
- Completion %
- Loop %
- Shares
- Saves
- Comments

If a platform cannot provide a metric:

- Store `null` for that metric.
- Record `METRIC_GAP` annotation.
- Do not fake a substitute unless it is explicitly defined as a proxy in this document.

---

## 2) Platform adapter model

### 2.1 Adapter interface (logical)

Each platform adapter must support:

- `resolve_post(platform_post_id | url) -> canonical_post_id`
- `fetch_metrics(canonical_post_id, window) -> MetricsSnapshot`
- `list_recent_posts(account_id, since) -> [canonical_post_id]` (optional)

Where `window` is one of the polling windows in §4.

### 2.2 Supported acquisition modes

Adapters may implement one of these modes:

- **API mode:** official API endpoints.
- **Partner mode:** approved vendor/partner analytics APIs.
- **Export mode:** platform-native analytics export + ingest.
- **Manual mode:** operator-exported CSV + ingest.

**Rule:** if you cannot acquire metrics compliantly, you do not automate that platform.

---

## 3) Snapshot schema (immutable source of truth)

### 3.1 Snapshot identity

Every stored snapshot must include:

- `run_id` (e.g., `RUN-YYYY-MM-DD-<short>`)
- `captured_at_utc`
- `platform`
- `account_id` (opaque)
- `canonical_post_id`
- `post_url` (if available)
- `publish_time_utc` (if available)
- `window` (`W1H` | `W24H` | other)
- `adapter_version`
- `source_mode` (`api|partner|export|manual`)

### 3.2 Snapshot payload

Store both:

- `raw` (verbatim response or export row)
- `parsed` (normalized fields mapped into the analytics schema)

### 3.3 Minimal parsed fields

The parsed payload should include (nullable):

- `views`
- `avg_view_duration_sec`
- `completion_pct`
- `loop_pct`
- `shares`
- `saves`
- `comments`

And quality flags:

- `missing_fields: [..]`
- `warnings: [..]`
- `errors: [..]`

---

## 4) Polling windows + scheduling

### 4.1 Windows (default)

- `W1H`: 1 hour after publish
- `W24H`: 24 hours after publish

These are the canonical windows used in [analytics/schema.md](../analytics/schema.md).

### 4.2 Grace periods

Platforms may delay metric propagation.

- `W1H` grace: +30 minutes
- `W24H` grace: +2 hours

Meaning: if the scheduled pull misses, it may run within the grace and still be accepted as that window.

### 4.3 Re-poll strategy

For each window, attempt up to 3 pulls:

- Attempt 1: at target window time
- Attempt 2: +10 minutes (W1H) / +30 minutes (W24H)
- Attempt 3: end of grace period

**Rule:** never keep polling indefinitely; that creates data drift.

---

## 5) Normalization + mapping rules

### 5.1 Field mapping

Each adapter must map platform-specific fields into the tracker fields.

Examples (conceptual):

- Platform “avgWatchTime” → `Avg view duration`
- Platform “completionRate” → `Completion %`
- Platform “replays” or “rewatches” → `Loop %` (only if defined clearly)

If a platform provides a different loop definition:

- Store it as `loop_pct` but add a warning: `LOOP_DEFINITION_DIFF`.

### 5.2 Unit normalization

- Durations in seconds.
- Percent fields in 0–100 scale.
- Counts as integers.

### 5.3 Cross-platform comparability

The telemetry layer does not invent comparability; it enforces consistent capture.

- Raw views remain platform-specific.
- Comparability happens after normalization in the analytics layer (see schema §4).

---

## 6) Ingestion validation (reject bad data)

Before writing any metric into the tracker, validate:

- Metrics are non-negative.
- Duration fields are within plausible range.
- Percent fields are within 0–100.
- Window timestamp falls within the allowed grace period.
- The snapshot refers to the correct canonical post.

If validation fails:

- Do not overwrite the tracker.
- Store the snapshot with an error flag.
- Alert operator.

---

## 7) Missing-data handling

### 7.1 Missing metric within a snapshot

- Keep the snapshot.
- Mark the field as null.
- Add `missing_fields` annotation.

### 7.2 Missing window (no snapshot)

- Mark the tracker row as missing that window.
- Retry within grace period.

### 7.3 Threshold for invalidation

A post becomes `INVALID` for analytics decision-making if:

- Required fields for the decision engine are missing at `W24H`, or
- Publish time cannot be determined reliably, or
- The post cannot be reconciled to a canonical ID.

Record as:

- Decision = `invalid`
- Notes include `INVALID_REASON: missing_metrics`

---

## 8) Invalid detection (beyond missing data)

The telemetry layer flags invalidity signals for governance/analytics to act on:

- `BOOSTED_DETECTED` (if API/export indicates paid promotion)
- `EDITED_AFTER_PUBLISH` (if platform indicates content changes or repost)
- `REUPLOAD_DETECTED` (new post ID for same asset/name)
- `RESTRICTION_STATE` (if account status indicates limits)

**Rule:** invalid detection produces flags; governance decides actions.

---

## 9) Drift flags (telemetry-level)

Drift flags are warnings that comparability may be compromised.

Telemetry should emit a drift flag when any occur:

- System-wide metric discontinuity (e.g., completion/loop drops across all posts).
- API field definition changes (platform updates).
- Adapter version changes mid-week.
- A large mismatch between repeated pulls at the same window (see reconciliation).

Flag examples:

- `DRIFT_SUSPECT_SYSTEM`
- `DRIFT_SUSPECT_SCHEMA`
- `DRIFT_SUSPECT_ADAPTER_CHANGE`

---

## 10) Tracker sync logic

### 10.1 Write policy

- Only write tracker fields from **validated** parsed snapshots.
- Do not overwrite with older windows.
- If a newer pull corrects a prior number, apply reconciliation rules.

### 10.2 Field mapping to tracker columns

- `views` @ W1H → `Views 1h`
- `views` @ W24H → `Views 24h`
- `avg_view_duration_sec` @ W24H → `Avg view duration`
- `completion_pct` @ W24H → `Completion %`
- `loop_pct` @ W24H → `Loop %`
- `shares/saves/comments` @ W24H → corresponding fields

**Rule:** Use W24H as the canonical decision window unless explicitly running a different experiment.

---

## 11) Reconciliation (self-correcting without chaos)

Platform metrics can change after the window due to spam cleanup or late aggregation.

### 11.1 Reconciliation rule

- The tracker stores the best-known value at the defined window.
- If a later pull differs, store it as an **amendment**, not a silent overwrite.

### 11.2 Amendment threshold

If a metric changes by more than a threshold (example):

- Views change > 2%
- Completion/loop change > 1 percentage point

Then:

- Record an amendment note (run_id + before/after + reason if known).
- Emit `RECONCILIATION_DELTA` warning.

### 11.3 When to repoll beyond grace

Repoll beyond grace only for diagnostics, not as the decision input:

- platform incidents
- suspected API outages
- suspected export corruption

Do not replace the canonical W1H/W24H values with late pulls.

---

## 12) Schema evolution

Platforms change. Your schema must evolve without breaking history.

Rules:

- Never delete snapshot fields.
- When a platform field changes meaning, bump `adapter_version` and add a mapping note.
- If you introduce a new metric, add it as optional first.
- If you deprecate a metric, keep writing null + add `METRIC_DEPRECATED`.

Any schema evolution requires:

- documentation update here
- weekly change log entry
- new experiment block if comparability is affected

---

## 13) Operational checklists (integration points)

- Daily discipline: [ops/checklists/daily.md](../ops/checklists/daily.md)
- Weekly direction: [ops/checklists/weekly.md](../ops/checklists/weekly.md)

Telemetry integrity depends on disciplined logging and consistent windows.
