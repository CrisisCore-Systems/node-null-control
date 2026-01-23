# Automation Wiring (Ops-Grade)

This document defines how automation connects the system end-to-end **without** breaking governance, identity isolation, or platform policies.

Hard boundaries: [docs/01_rules.md](../docs/01_rules.md)
Workflow reference: [docs/02_workflow.md](../docs/02_workflow.md)
Analytics rules: [analytics/schema.md](../analytics/schema.md)

---

## 0) Non-negotiables

- **Policy compliance only:** automate only via official platform APIs, approved partners, or platform-native scheduling tools.
- **No enforcement evasion:** no account cycling, no ban evasion, no shadow techniques.
- **No artificial engagement:** no bots for likes/follows/comments, no purchased traffic, no fake signals.
- **Identity isolation:** separate credentials, storage, and logs per account/network.
- **Auditability:** every automated action must be attributable to a run ID and logged.

---

## 1) System boundaries (what automation may and may not do)

### Allowed automation

- Create standardized artifacts (script files, caption files, template instantiations) from approved templates.
- Validate artifacts against governance constraints (linting, forbidden-phrase checks, metadata completeness).
- Schedule/queue posts **only** through compliant methods (platform scheduling or approved tools).
- Capture metrics from official analytics endpoints (or manual export + ingest) and write to the tracker.
- Produce weekly summaries and decision drafts (human-approved).
- Trigger freeze conditions and incident workflows.

### Forbidden automation

- Automated posting via unofficial endpoints or reverse-engineered APIs.
- Automated engagement behavior (commenting/liking/following/sharing) intended to manipulate distribution.
- Automated scraping that violates Terms or privacy expectations.
- Storing credentials in plaintext or committing secrets into the repo.

---

## 2) Component map (logical services)

This repo is documentation-first; implementation can be done with any stack. The wiring assumes these logical components:

1. **Artifact Generator**
   - Input: templates + hook library + controls
   - Output: script/caption instances with metadata

2. **Governance Linter**
   - Checks: forbidden topics/phrasing, metadata completeness, versioning compliance
   - Output: `passed | blocked` with reasons

3. **Scheduler Connector (Compliant)**
   - Integrates with: platform-native scheduling or approved tools
   - Output: publish confirmation IDs/URLs

4. **Metrics Collector (Compliant)**
   - Pulls: 1h/24h windows and engagement fields
   - Output: normalized metric rows + raw snapshots

5. **Tracker Writer**
   - Writes to: the single source of truth (e.g., Google Sheet)
   - Ensures: one post = one row, invalid handling

6. **Decision Engine**
   - Applies: [analytics/schema.md](../analytics/schema.md)
   - Output: ranking tables, triggers, and draft decisions

7. **Incident Orchestrator**
   - Monitors: warnings/restrictions, toxic comment signals
   - Output: freezes, alerts, audit trails

---

## 3) Data flow (end-to-end)

### Flow A — Build artifacts

1. Operator selects:
   - `block_id`, `experiment_id`, `control` set
2. Artifact Generator produces:
   - script instance (based on [ops/templates/short_script_template.md](../ops/templates/short_script_template.md))
   - caption instance (based on [ops/templates/caption_template.md](../ops/templates/caption_template.md))
3. Governance Linter validates:
   - required metadata present
   - forbidden constructs absent
   - one-variable discipline declared
4. Output:
   - `READY` (pass) or `BLOCKED` (fail)

### Flow B — Publish (compliant)

1. Scheduler Connector receives `READY` artifacts.
2. Schedules/publishes through compliant tooling.
3. Returns:
   - platform post ID/URL
   - scheduled time / actual publish time
4. Tracker Writer immediately logs the row.

### Flow C — Measure

1. Metrics Collector runs on schedule:
   - at 1h after publish
   - at 24h after publish
2. Collector stores:
   - raw snapshots (immutable)
   - parsed fields into tracker
3. Tracker Writer updates the corresponding post row.

### Flow D — Decide

1. Decision Engine aggregates by:
   - hook type
   - vertical
   - block
2. Produces:
   - top/bottom patterns
   - win rates
   - kill/iterate/scale triggers
3. Weekly checklist consumes outputs: [ops/checklists/weekly.md](../ops/checklists/weekly.md)

---

## 4) Identity isolation model

### Isolation targets

- Per-platform account
- Per “network” (group of accounts)
- Per phase (Harvest/Extract/Forge) if risk profile changes

### Required isolation controls

- Separate credentials per account.
- Separate storage buckets/folders per account.
- Separate run IDs and logs per account.
- No cross-account cookie/session reuse.

### Practical directory/log conventions

- `run_id`: `RUN-YYYY-MM-DD-<short>`
- `account_id`: opaque ID (not a real-world identity)

---

## 5) Secrets and security (ops-grade)

### Rules

- Do not store secrets in this repo.
- Use a secrets manager (Vault, 1Password, Azure Key Vault, AWS Secrets Manager, etc.).
- Enforce MFA on all platform and automation tool accounts.
- Use least-privilege API keys with scoping.

### Rotation

- Rotate API keys on a fixed cadence (monthly or upon suspicion).
- Revoke immediately on any incident.

### Access

- Separate roles:
  - Operator (publish)
  - Analyst (read metrics)
  - Governor (approvals)

---

## 6) Auditability requirements

Every automated action must produce an audit record containing:

- `run_id`
- timestamp (UTC)
- actor (service name + operator ID if human-triggered)
- target (platform/account/post ID)
- action type (generate, lint, schedule, publish, fetch_metrics, write_tracker)
- input hashes (artifact hash)
- outcome (success/failure)
- error details (if any)

**Rule:** raw snapshots are immutable.

---

## 7) Governance wiring (where the rules are enforced)

### Mandatory gates

- Gate 1: Pre-generation constraints
  - only allowed verticals/hooks
  - template versions locked
- Gate 2: Pre-publish lint
  - forbidden phrases/topics
  - CTA/hashtag policy compliance
  - one-variable discipline declared
- Gate 3: Post-publish logging
  - create row immediately
- Gate 4: Measurement validity
  - invalid reasons applied consistently

If any gate fails: do not proceed automatically.

---

## 8) Invalid handling wiring

If a post becomes invalid (boosted, edited post-publish, missing metrics):

- Tracker Writer sets Decision = `invalid`
- Notes include `INVALID_REASON: ...`
- Decision Engine excludes invalid samples from aggregation

---

## 9) Rate limits, retries, and failure handling

### Rate limits

- Respect platform/tool/API rate limits.
- Use backoff and jitter.

### Retry policy

- Retry only idempotent operations (metric fetch, tracker read).
- Do not retry publishes blindly.

### Failure modes

- If tracker write fails: queue a retry and alert.
- If metrics fetch fails: mark missing metrics and retry within the window.
- If linter fails: block and require manual correction.

---

## 10) Monitoring and alerting

Alerts to implement:

- Platform incident detected (warning/strike/restriction)
- Invalid rate > threshold (e.g., 20% in a block)
- Missing metrics rate > threshold
- Drift suspicion (global metric shift)
- Unauthorized access attempt / secret leak suspicion

Notification channels:

- Email
- Slack/Discord
- Pager (for serious incidents)

---

## 11) Scaling model (safe expansion)

Scale only after meeting scale conditions (see [analytics/schema.md](../analytics/schema.md) + [docs/02_workflow.md](../docs/02_workflow.md)).

Scaling axes (in safe order):

1. Increase volume for the same winner within one platform.
2. Replicate to adjacent verticals (same template + controls).
3. Expand platforms using compliant schedulers/APIs.

Scaling requirements:

- Per-account isolation preserved.
- Audit logs preserved.
- Governance gates enforced.

---

## 12) Implementation notes (repo-friendly)

If/when you implement this wiring, keep the implementation modular:

- A CLI for artifact generation + linting.
- A scheduler integration layer with a strict interface.
- A metrics layer that supports multiple platforms.
- A tracker adapter (Google Sheets / CSV / database).

Do not couple strategy logic to platform-specific quirks; keep policy rules centralized.
