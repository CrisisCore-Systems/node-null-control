# Daily Ops Checklist

Daily operator runbook.

Hard boundaries: [docs/01_rules.md](../../docs/01_rules.md)
Workflow reference: [docs/02_workflow.md](../../docs/02_workflow.md)
Metric definitions + decisions: [analytics/schema.md](../../analytics/schema.md)

Target time: **15–25 minutes** (not including production/editing time).

---

## 0) Pre-flight (2 minutes)

- Confirm you’re operating inside the current **experiment block** (same template + same controls).
- Confirm there is no unresolved platform incident (warning/strike/restriction) from yesterday.
- Confirm today’s plan does **not** introduce multi-factor changes.

If anything is unclear, stop and resolve it before publishing.

---

## 1) Publish discipline (5–10 minutes)

### 1.1 Select what ships today

- Choose the exact posts scheduled for today (per queue/backlog).
- For each post, confirm:
  - Vertical + Hook Type are labeled.
  - Variant is defined (control vs variant).
  - Only one variable changed vs the control (or explicitly multi-factor).

### 1.2 Pre-publish governance gate (hard stop)

For each post, confirm it passes governance:

- No political targeting or persuasion.
- No medical claims or treatment guidance.
- No financial advice or “guaranteed outcome” claims.
- No hate/harassment/protected-class targeting.
- No violence/incitement or wrongdoing instructions.
- No deception/impersonation.
- No engagement begging.
- No copyright risk (unlicensed audio/video).

If any fail: do not publish. Revise or block.

### 1.3 Publish

- Publish or schedule at the intended time slot.
- Immediately capture the published URL/ID if available.

---

## 2) Logging discipline (2–4 minutes)

Immediately after publish (no batching later):

- Create/confirm the tracker row for each post.
- Fill identity fields:
  - Date, Platform, Vertical, Hook Type
  - First line / Hook text
  - Duration (sec), Visual Style, Voice Style
- Record experiment identifiers:
  - Block ID, Experiment ID, Variant ID, Control flag

Rule: one post = one row.

---

## 3) Data discipline (5–8 minutes)

### 3.1 Capture yesterday’s metrics at defined windows

For each post that reached the capture window(s):

- Views 1h
- Views 24h
- Avg view duration
- Completion %
- Loop %
- Shares
- Saves
- Comments

If a metric is unavailable on a platform:

- Record the closest equivalent.
- Note the difference explicitly in Notes.

### 3.2 No partial rows

- If required metrics are missing, mark the row `INVALID` until repaired.

---

## 4) Validation discipline (2–4 minutes)

For each row updated today, validate:

- Organic-only (not boosted/promoted)
- No material edit after publishing that changes distribution
- No reupload treated as the same sample
- No known restriction state during the measurement window
- Required metrics present

If invalid:

- Set Decision = `invalid`
- Add `INVALID_REASON: boosted | edited_after_publish | missing_metrics | restriction_state | reupload | other`
- Exclude it from decisions

---

## 5) Experiment discipline (2–4 minutes)

For today’s shipped posts:

- Confirm **one-variable** discipline:
  - Changed variable is stated explicitly (e.g., hook line only).
  - Controls are listed (template version, duration band, voice/visual style).
- Confirm comparability:
  - Same duration band
  - Same template version
  - Comparable time slot

If you accidentally shipped multi-factor:

- Mark it clearly as multi-factor.
- Do not compare it as a clean A/B.

---

## 6) Governance discipline (1–2 minutes)

- Scan the last 24 hours of comments for:
  - Hate/harassment signals
  - Self-harm content
  - Policy-sensitive escalation

If the pattern attracts disallowed content reliably:

- Freeze the pattern.
- Document the incident.

---

## 7) Decision discipline (2–4 minutes)

### 7.1 Tag outcomes (lightweight)

Using the schema’s signal hierarchy:

- Tag each post as provisional: `winner | neutral | loser`.
- Do not label a post a win if there is any policy/monetization risk.

### 7.2 Queue the next step

- If winner: queue 1–2 confirmatory variants (replication).
- If neutral: queue one controlled iteration.
- If loser: queue one iteration or prepare for kill at weekly review.

---

## 8) Incident protocol (as needed)

If any warning/strike/restriction occurs:

- Freeze affected patterns immediately.
- Classify the incident (copyright, harassment, misinfo, etc.).
- Audit recent posts for the same risk signature.
- Resume only with a safer variant and explicit controls.

Do not attempt enforcement evasion.

---

## 9) End-of-day closure (1–2 minutes)

- Confirm all shipped posts are logged.
- Confirm all due capture windows were filled.
- Confirm invalids are marked and excluded.
- Write one sentence in Notes:
  - What changed today (if anything)
  - Any drift suspicion
  - Any platform incident

If fatigue is high: stop changes. Ship controls only.

---

## 10) Monetization asset gate (as needed)

If you ship or modify any monetizable artifact today:

- Update the registry entry: [monetization/assets/registry.md](../../monetization/assets/registry.md)
- Run the activation gate checklist: [monetization/assets/validation.md](../../monetization/assets/validation.md)
- Log the validation result (pass/fail) in Notes

Hard rule: FAIL = cannot mark asset `active`.
