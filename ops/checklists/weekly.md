# Weekly Ops Checklist (Direction)

This is the weekly direction-setting ritual: audit dataset health, rank patterns, make kill/scale decisions, plan next experiments, and detect drift.

Hard boundaries: [docs/01_rules.md](../../docs/01_rules.md)
Workflow reference: [docs/02_workflow.md](../../docs/02_workflow.md)
Metric definitions + triggers: [analytics/schema.md](../../analytics/schema.md)

Target time: **45–60 minutes**.

---

## 0) Inputs and required outputs

### Inputs

- The last 7 days of Posts rows (valid + invalid, with notes)
- Current experiment block definition (controls, changed variable, block_id)
- Any platform incidents (warnings/strikes/restrictions)

### Outputs (must exist by end)

- Dataset health summary (counts, invalid rate, missing metrics)
- Top patterns (hooks, verticals) with medians + win rates
- Bottom patterns with reasons
- Decisions: kill / iterate / scale (with thresholds cited)
- Next-week experiment plan (hypotheses + sample plan)
- Change log (what changed, what stayed fixed)

---

## 1) Dataset health audit (10–15 minutes)

### 1.1 Count and quality

- Total posts shipped (last 7 days)
- Valid sample count
- Invalid sample count
- Invalid rate
- Missing-metrics rate

If invalid rate is high:

- Identify the top invalid reasons.
- Fix process before changing content strategy.

### 1.2 Validate comparability

Confirm the week did not mix uncontrolled variables:

- Template version stayed fixed within each block
- Duration bands were not accidentally mixed in comparisons
- Time-slot changes were recorded
- Multi-factor samples are clearly labeled and excluded from clean A/B comparisons

If comparability fails:

- Mark the week as “noisy”.
- Reduce scope next week (controls-only) until stability returns.

---

## 2) Incident + governance review (5–10 minutes)

### 2.1 Platform incident review

For any warning/strike/restriction:

- Identify which pattern(s) were active.
- Classify the likely policy domain (copyright, harassment, misinfo, etc.).
- Decide if any patterns must be frozen.

### 2.2 Comment ecosystem risk check

- Scan a sample of comments from the top-performing posts.
- Look for persistent:
  - hate/harassment
  - self-harm content
  - policy-sensitive escalation

If a pattern reliably attracts disallowed content:

- Freeze it regardless of performance.

---

## 3) Drift detection (5–10 minutes)

Drift = performance becomes non-comparable across time.

Check for:

- Sudden shifts across all verticals/hooks
- Account state changes (restriction/eligibility)
- Template or packaging changes (caption/hashtags/audio policy)
- Major external events affecting distribution

If drift is suspected:

- Start a new experiment block next week.
- Run a baseline reconfirmation block on the prior winner.

---

## 4) Pattern ranking ritual (15–20 minutes)

Use the analytics schema’s hierarchy and aggregation rules.

### 4.1 Build the comparison set

Rank within:

- Same platform
- Same duration band
- Same experiment block

Do not mix platforms using raw views.

### 4.2 Rank hooks

For each Hook Type (valid samples only):

- Sample count
- Median Completion%
- Median RetentionRatio (or proxy)
- Median Loop%
- Median SaveRate+ShareRate
- Composite score median (if used)

### 4.3 Rank verticals

Repeat the same aggregation by Vertical.

### 4.4 Identify the week’s winners and losers

- Top 3 hooks
- Top 3 verticals
- Bottom 3 hooks
- Bottom 3 verticals

For each top/bottom item, write one sentence:

- What it is
- What it beat/lost to
- Why (metric evidence)

---

## 5) Decision ritual (10–15 minutes)

### 5.1 Apply minimum sample sizes

Do not make structural decisions below minimum sample sizes defined in the schema.

If sample sizes are insufficient:

- Default to iterate, not kill or scale.

### 5.2 Kill decisions

Kill when:

- Below-baseline completion/retention AND below-baseline saves+shares across minimum samples, and
- No improvement after 2 iterations, and
- No drift explanation

Also kill immediately on governance kill conditions.

Write for each kill:

- Pattern (hook/vertical)
- Block/week range
- Evidence (medians, win rate)
- Next action (what replaces it)

### 5.3 Scale decisions

Scale when:

- Top-quartile by composite score within its set, and
- Win rate meets the schema threshold, and
- It survives replication, and
- No policy/monetization risk

Write for each scale:

- Pattern definition (what stays fixed)
- Allowed variation range (what may change)
- Scaling action (increase output, adjacent vertical, platform expansion)

### 5.4 Iterate decisions

Iterate when metrics disagree:

- Strong completion but weak saves/shares
- Strong saves/shares but weak completion
- Volatile results without clear drift

Write for each iterate:

- Hypothesis
- Exact variable changed
- Controls held

---

## 6) Next-week experiment planning (10–15 minutes)

### 6.1 Lock controls first

Choose the control set for next week:

- Template version
- Duration band
- Voice style
- Visual style
- Caption/hashtag policy
- Posting cadence/time slots

### 6.2 Define experiment blocks

For each experiment block, define:

- block_id
- primary hypothesis
- primary metric (and secondary metrics)
- variable changed (one-variable discipline)
- sample plan (count + schedule)
- stop conditions (freeze/kill triggers)

### 6.3 Production plan

- How many posts per day
- Which patterns are controls
- Which patterns are variants
- Which days run replication vs exploration

---

## 7) System evolution (5 minutes)

Only change one “system layer” per week:

- template version, or
- scoring weights/thresholds, or
- cadence/time-slot policy, or
- vertical taxonomy

If a system layer changes:

- Version it.
- Start a new experiment block.
- Document the change and expected effect.

---

## 8) Phase transition signals (Harvest → Extract → Forge)

### 8.1 Signals to move Harvest → Extract

- Winner repeats across multiple posts (not a spike)
- Clean dataset (low invalid rate)
- No drift / stable distribution
- No policy/monetization risk flags

### 8.2 Signals to move Extract → Forge

- Winning spec remains dominant under controlled variation
- Portability confirmed (at least one adjacent test)
- Operations stable (process compliance)

### 8.3 Signals to delay transition

- Rising invalid rate
- Unresolved platform incidents
- Drift not understood
- Winner depends on a risky tactic

---

## 9) Weekly close (2 minutes)

Write a short weekly note (for the Weekly Summary tab or notes log):

- What stayed fixed
- What changed
- What won
- What died
- What ships next week

---

## 10) Monetization asset audit (5–10 minutes)

Purpose: prevent unapproved assets from going live and prevent routing drift.

References:

- Registry (SSOT): [monetization/assets/registry.md](../../monetization/assets/registry.md)
- Validation gate: [monetization/assets/validation.md](../../monetization/assets/validation.md)
- Hybrid router: [monetization/architecture.md](../../monetization/architecture.md)

Do weekly:

- Audit the “active assets” list in the registry
- Confirm every `active` asset has a recent PASS validation record
- Check revenue mix drift vs the hybrid target (no surface > 50%)
- Review kill switch triggers and quarantine anything contaminating signal
- Deprecate or retire any asset causing incentive distortion
