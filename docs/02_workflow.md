# 02 — Workflow (Operations)

This document turns the rules into motion.

- If a workflow step conflicts with the constitution, the constitution wins: [docs/01_rules.md](01_rules.md)

---

## 0) Workflow intent

**Primary outcome:** consistent publishing + consistent measurement → clean signal → correct kill/scale decisions.

**Failure modes this workflow prevents:** noisy datasets, uncontrolled changes, platform risk, monetization breaks, and drift.

---

## 1) Lifecycle stages

### Stage A — Harvest (Ghost Network)

**Objective:** generate *comparable* samples to discover what patterns win.

**Inputs:** defined verticals, hook types, stable templates, stable cadence.

**Outputs:** ranked patterns, kill list, scale list, a short list of candidate “winners”.

**Exit criteria (move to Extract):**

- A vertical + hook family repeatedly wins across multiple posts, and
- Signal is stable (no major drift), and
- No platform/monetization risk flags.

### Stage B — Extract (Pattern Dominance)

**Objective:** compress uncertainty: prove the winner is real, repeatable, and portable.

**Actions:**

- Narrow to fewer variables.
- Run confirmatory experiments (replication).
- Test portability (adjacent vertical, alternate voice/visual variant) without breaking comparability.

**Outputs:** a “winning spec” (pattern definition) and an operating baseline.

**Exit criteria (move to Forge):**

- The winning spec stays dominant under controlled variation, and
- It holds across platforms or at least two distribution surfaces.

### Stage C — Forge (Brand Emergence)

**Objective:** convert a proven pattern into a coherent product/brand surface without losing signal integrity.

**Constraints:** Forge does not override safety, policy, monetization, or identity isolation rules unless explicitly re-scoped.

**Outputs:** brand system, content series architecture, and monetization pathways.

---

## 2) Daily operational loop (15–25 minutes + production time)

### 2.1 Daily checklist

1. **Publish / schedule** today’s posts (from the queue).
2. **Capture metrics** for yesterday’s posts at the defined windows.
3. **Validate samples** (mark invalids immediately).
4. **Tag outcomes** (winner/neutral/loser) based on thresholds.
5. **Queue next variants** (only one-variable changes).

### 2.2 Daily “one-variable” rule

Daily output should prioritize comparability:

- If you change the hook, keep the template stable.
- If you change the template, keep the vertical + hook stable.
- If you change cadence/time slot, keep everything else stable.

If you must change multiple variables, label it explicitly as a multi-factor experiment.

---

## 3) Publishing flow (end-to-end)

### 3.1 Flow map

**Backlog → Script → Voice → Visuals → Edit → QC → Schedule/Publish → Log → Measure → Decide**

### 3.2 Required gates

- **Pre-script gate:** confirm the concept is allowed under [docs/01_rules.md](01_rules.md).
- **Pre-publish gate:** confirm policy-safe phrasing, no prohibited claims, no prohibited targeting.
- **Post-publish gate:** log the post immediately as a new row (no “I’ll do it later”).

### 3.3 Versioning

Every published post must have a stable identifier (per README naming conventions) so you can trace:

- Which template version produced it
- Which hook type it used
- Which experiment block it belongs to

---

## 4) Data capture flow (single source of truth)

### 4.1 Data is captured on purpose

Treat the tracker as the database.

- One post = one row.
- No merging rows across reuploads.
- No editing history that changes what the sample “was” without recording it as a new sample.

### 4.2 Minimum capture windows

Capture at consistent windows (example):

- **1h**: early distribution signal
- **24h**: stabilized distribution signal

If you add additional windows (e.g., 48h/7d), do it consistently for *all* samples in a block.

### 4.3 Validation step (fast)

For each row, confirm:

- Organic (not boosted)
- No material edits after publish
- No account restriction state known during the window
- Required metrics present

If any fail, mark `INVALID` and record the reason.

---

## 5) Weekly optimization loop (45–60 minutes)

### 5.1 Weekly review agenda

1. **Audit the dataset**
   - Invalid rate
   - Missing metrics rate
   - Drift indicators
2. **Rank**
   - Verticals
   - Hook types
   - Template variants
3. **Decide**
   - Kill underperformers
   - Scale winners
   - Define next week’s experiment blocks
4. **Document**
   - Decisions and reasons
   - What changed (versioning)
   - What stayed fixed (controls)

### 5.2 Decision outputs

Every week must produce:

- A **Kill list** (what stops)
- A **Scale list** (what expands)
- A **Control set** (what stays frozen to preserve comparability)
- A **Next experiments** list (explicit hypotheses)

---

## 6) Experiment lifecycle (clean, repeatable)

### 6.1 Experiment charter (required)

Before running an experiment, define:

- **Hypothesis:** what you expect and why
- **Primary metric:** what defines “better”
- **Secondary metrics:** loop/shares/saves etc.
- **Variable changed:** exactly what changes
- **Controls:** what is held constant
- **Sample plan:** how many posts / how long
- **Stop conditions:** kill/freeze triggers

### 6.2 Execution

- Run variants in comparable slots.
- Avoid mixing unrelated tests in the same time window.
- Log every post as it ships (no memory-based reconstruction).

### 6.3 Analysis and decision

- Compare within the same experiment block.
- If drift is detected, do not force conclusions—start a new block.
- Record the decision and the reasoning in the decision log.

---

## 7) Governance checkpoints (where rules are enforced)

### 7.1 Pre-production compliance check

Confirm:

- No prohibited claims (medical/financial)
- No political targeting
- No hate/harassment/protected-class targeting
- No deceptive practices
- No copyrighted assets unless licensed

### 7.2 Weekly governance review

Confirm:

- Change control has been respected
- Invalid samples are excluded from decisions
- No uncontrolled variable explosions
- No platform risk escalation ignored

---

## 8) Escalation paths (who decides what)

Use a simple escalation ladder:

- **Operator:** executes daily loop, logs data, proposes experiments.
- **Reviewer:** validates compliance + data integrity weekly.
- **Governor:** approves major changes (template overhaul, cadence change, phase transition).

If you are solo, you still follow the ladder: you must explicitly “switch hats” and document approvals.

---

## 9) Freeze, reset, and drift handling

### 9.1 Freeze conditions (immediate)

Freeze a pattern/vertical if any occur:

- Platform warning/strike linked to the pattern
- Clear monetization eligibility risk linked to the pattern
- Comment ecosystem becomes reliably toxic (hate, harassment, self-harm content)
- Dataset corruption exceeds acceptable thresholds (e.g., invalids > 20% in a block)

Freeze action:

- Stop publishing that pattern immediately.
- Preserve evidence (what was posted, when, why it triggered).
- Design a revised variant that removes the risk.

### 9.2 Reset conditions

Start a new experiment block when:

- Template version changes
- Editing/voice/visual source changes materially
- Cadence/time slot changes materially
- Account state changes (restriction/eligibility)

Reset action:

- Mark the transition date.
- Define new controls.
- Do not compare across the boundary as if it were continuous.

### 9.3 Drift protocol

If metrics shift unexpectedly across everything:

1. Assume drift before assuming “creative failure”.
2. Check account state, platform events, and major template changes.
3. Run a small “baseline reconfirmation” block with the previous winner.

---

## 10) Platform incident handling

When a warning/strike/restriction occurs:

1. **Freeze** affected patterns.
2. **Classify incident:** policy domain (misinfo, harassment, copyright, etc.).
3. **Audit last N posts** for the same risk signature.
4. **Remediate:** delete/privatize if needed, revise template language, revise topic boundaries.
5. **Resume only** with a safer variant and explicit controls.

Do not attempt enforcement evasion or “workarounds”. Treat incidents as a governance signal.

---

## 11) Transition logic (Extract → Forge)

### 11.1 When to consider Forge

Forge becomes permissible when:

- A pattern remains dominant across multiple weeks and multiple samples.
- The winner is portable (repeatable across minor variations).
- The operation is stable (low invalid rate, controlled changes).

### 11.2 Forge entry plan (still controlled)

- Define the brand surface (name/visual system/tone) without creating identity exposure.
- Keep the core pattern stable while you introduce brand elements.
- Measure whether branding helps or harms distribution.

### 11.3 Forge exit criteria (optional)

If brand elements materially reduce performance or increase platform risk:

- Roll back to the previous Extract baseline.
- Reintroduce branding in smaller increments.

---

## 12) Required artifacts (repo-facing)

This workflow assumes these artifacts exist (or will exist):

- Tracker schema (single source of truth) referenced in README
- Decision logs (kill/scale)
- Templates (editing, captions, hooks)
- Automation (cross-posting, scheduling, metric pulls)

Next build steps will define these as concrete files.
