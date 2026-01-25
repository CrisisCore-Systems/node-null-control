# Analytics Schema (Decision Engine)

The tracker is the **decision engine**: metric definitions, formulas, thresholds, normalization, aggregation, and decision triggers.

Governance trumps analytics: [docs/01_rules.md](../docs/01_rules.md)

---

## 0) Scope + non-negotiables

- **Organic-only dataset:** boosted/paid posts are not comparable; mark `INVALID`.
- **No retroactive rewriting:** do not change historic labels to fit a narrative. If taxonomy changes, map old → new.
- **One post = one row:** each upload event gets its own row.
- **Comparability first:** only compare samples within the same experiment block unless explicitly normalized.

---

## 1) Core tracker fields (Posts tab)

These align with README’s minimum columns.

### Identity + classification

- **Date**: publish date (local time). Use ISO `YYYY-MM-DD`.
- **Platform**: `tiktok | yt_shorts | ig_reels | fb_reels | other`.
- **Vertical**: topic bucket (string; must come from the current vertical list).
- **Hook Type**: hook mechanism label (string; must come from the current hook list).
- **First line / Hook text**: the actual first on-screen line or first spoken line (string).
- **Duration (sec)**: integer seconds (or 1 decimal if needed).
- **Visual Style**: stable label (e.g., `dystopian_loop_v1`).
- **Voice Style**: stable label (e.g., `neutral_tts_v1`).

### Raw performance (captured at defined windows)

Capture each of these at the same windows for all samples in a block.

- **Views 1h**: total views at $t=1\,\text{hour}$.
- **Views 24h**: total views at $t=24\,\text{hours}$.
- **Avg view duration**: average watch time per view in seconds (platform-reported).
- **Completion %**: percent of views that reached 100% (platform-reported).
- **Loop %**: percent of views with a replay/rewatch or average loops; use the platform’s closest available measure.
- **Shares**: total shares at the capture window.
- **Saves**: total saves/bookmarks/favorites.
- **Comments**: total comments.

### Governance + notes

- **Notes**: free text; must include drift/incident annotations when relevant.
- **Decision**: `keep | iterate | kill | scale | invalid`.

---

## 2) Derived metrics (computed fields)

Define derived metrics explicitly so rankings are stable.

### 2.1 Retention ratio

Primary retention proxy:

$$\text{RetentionRatio} = \min\left(1, \frac{\text{AvgViewDuration}}{\text{DurationSec}}\right)$$

- Clamp to 1.0 to avoid platform quirks (e.g., autoplay loops inflating average).

### 2.2 Engagement rates (per view)

Use 24h as the default denominator for cross-post comparability.

$$\text{ShareRate} = \frac{\text{Shares}_{24h}}{\max(1,\text{Views}_{24h})}$$
$$\text{SaveRate} = \frac{\text{Saves}_{24h}}{\max(1,\text{Views}_{24h})}$$
$$\text{CommentRate} = \frac{\text{Comments}_{24h}}{\max(1,\text{Views}_{24h})}$$

### 2.3 Velocity (growth between windows)

$$\text{Velocity} = \frac{\text{Views}_{24h} - \text{Views}_{1h}}{23}$$

Units: views per hour (between hour 1 and hour 24).

### 2.4 Composite signal score (for ranking)

We rank by a composite score to avoid single-metric chasing.

First normalize each component within the comparison set (see §4), then combine:

$$\text{Score} = w_r R + w_c C + w_l L + w_s S$$

Where:

- $R$ = normalized RetentionRatio (or Completion% where RetentionRatio unavailable)
- $C$ = normalized Completion%
- $L$ = normalized Loop%
- $S$ = normalized Saves+Shares rate (a combined “distribution intent” measure)

Default weights (tunable, but versioned):

- $w_r = 0.35$
- $w_c = 0.25$
- $w_l = 0.20$
- $w_s = 0.20$

**Rule:** If weights change, start a new experiment block and annotate.

---

## 3) Signal hierarchy (what outranks what)

When metrics disagree, use this priority order for decisions:

1. **Completion / retention** (people stayed)
2. **Loop** (rewatch demand)
3. **Saves + shares** (distribution intent)
4. **Comments** (interpret cautiously; can be negative/toxic)
5. **Raw views** (affected heavily by platform variance)

Rationale: views can spike from distribution noise; completion/loop/saves/shares are closer to true demand.

---

## 4) Normalization + cross-platform comparability

Because platforms differ, comparisons must be normalized.

### 4.1 Comparison set

Default comparison set is:

- Same platform
- Same duration band (see below)
- Same template version / block
- Same time-slot category (if tracked)

If cross-platform comparison is required, use a platform-normalized index.

### 4.2 Duration bands

To reduce length bias:

- **Band A:** 15–19s
- **Band B:** 20–27s
- **Band C:** 28–35s

Only compare within the same band unless explicitly adjusted.

### 4.3 Robust normalization (recommended)

For each metric $x$ in a comparison set:

- Compute median $m$ and MAD (median absolute deviation) $d$.
- Robust z-score:

$$z = \frac{x - m}{\max(\epsilon, 1.4826\,d)}$$

Then squash to 0–1 for combination (logistic):

$$n = \frac{1}{1 + e^{-z}}$$

Use $\epsilon = 10^{-9}$.

### 4.4 Platform-normalized index (optional)

To compare across platforms, compute normalized metrics **within each platform** first, then compare the normalized scores.

**Rule:** never compare raw Views across platforms.

---

## 5) Invalid handling logic

A row is `INVALID` if any of the invalid conditions in [docs/01_rules.md](../docs/01_rules.md) apply.

Invalid rows:

- Are excluded from rankings, win rates, and decision triggers.
- Remain in the dataset for auditing with an explicit invalid reason.

Recommended fields to record in Notes:

- `INVALID_REASON: boosted | edited_after_publish | missing_metrics | restriction_state | reupload | other`

---

## 6) Thresholds (win / neutral / loss)

Thresholds are defined **relative to the baseline** of the current experiment block.

### 6.1 Baseline definition

Baseline set = control template + control vertical/hook during the same week/time-slot band.

### 6.2 Outcome labels

Compute percent lift vs baseline for primary metrics.

Example lift for completion:

$$\text{Lift}_C = \frac{C_{variant} - C_{baseline}}{\max(\epsilon, C_{baseline})}$$

Default label rules (tunable, versioned):

- **WIN** if:
  - Completion% lift ≥ +10% **and**
  - SaveRate+ShareRate lift ≥ +10% (combined) **and**
  - No safety/policy risk flags

- **NEUTRAL** if:
  - Completion lift between -5% and +10% and
  - Save+Share lift between -5% and +10%

- **LOSS** if:
  - Completion lift ≤ -5% **or**
  - Save+Share lift ≤ -5%

**Rule:** If a post triggers platform risk, it is not a win regardless of metrics.

---

## 7) Aggregation rules

### 7.1 Per-hook aggregation

For each Hook Type within a block:

- Sample count (valid only)
- Median Completion%
- Median RetentionRatio
- Median Loop%
- Median SaveRate+ShareRate
- Composite Score median

Prefer medians over means (resistant to outliers).

### 7.2 Per-vertical aggregation

Same as per-hook, but grouped by Vertical.

### 7.3 Win rate

$$\text{WinRate} = \frac{\#WIN}{\#WIN + \#NEUTRAL + \#LOSS}$$

Exclude invalids.

---

## 8) Weekly summary logic

Weekly summary must answer:

- What improved (and by how much)?
- What degraded (and by how much)?
- What drifted (and why)?
- What is being killed, scaled, or iterated next?

Recommended weekly sections:

1. **Dataset health**: sample count, invalid rate, missing metric rate.
2. **Top patterns**: top 3 hooks, top 3 verticals (with medians + win rates).
3. **Bottom patterns**: bottom 3 hooks, bottom 3 verticals.
4. **Decisions**: kill/iterate/scale with reasons.
5. **Change log**: what changed (templates/weights/cadence).
6. **Incidents**: warnings/strikes/restrictions.

---

## 9) Decision triggers (kill / iterate / scale)

### 9.1 Minimum sample size

Do not make structural decisions below a minimum valid sample count.

Default minimums:

- **Hook Type:** 6 valid samples per hook
- **Vertical:** 10 valid samples per vertical

(Adjust based on posting volume; version changes.)

### 9.2 Kill triggers

Kill a pattern if all are true:

- Below-baseline completion/retention and below-baseline save+share across the sample minimum, and
- No improvement after 2 iterations, and
- No evidence drift explains the change

Also kill immediately on governance kill conditions.

### 9.3 Iterate triggers

Iterate when:

- Completion is strong but saves/shares are weak (distribution intent missing), or
- Saves/shares are strong but completion is weak (packaging mismatch), or
- A pattern is volatile (inconsistent performance) without clear drift

Iterate by changing exactly one variable.

### 9.4 Scale triggers

Scale a pattern when:

- It is top-quartile by composite score within its comparison set, and
- Win rate ≥ 0.60 over the minimum sample size, and
- It survives a confirmatory replication block, and
- No policy/monetization risk flags appear

Scaling order is defined in [docs/02_workflow.md](../docs/02_workflow.md).

---

## 10) Auditability requirements

Any weekly decision must be traceable to:

- The exact rows used (date range + block ID if present)
- The formulas in this document
- The thresholds and weights version

If traceability fails, the decision is downgraded to “hypothesis” until repaired.
