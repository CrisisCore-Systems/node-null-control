# 01 — Rules (Constitution)

Hard boundary layer for **node-null-control**.

If a rule conflicts with a workflow, the **rule wins**.

---

## 1) Purpose

**Goal:** a repeatable, policy-safe short-form publishing system that produces **clean signal** (comparable data) without corrupting the dataset.

**Non-goals:** personas, identity stories, political persuasion, medical/financial claims, deception, policy evasion.

---

## 2) Definitions

- **Post**: one upload event on one platform.
- **Sample**: a post that meets the validity requirements in §5.
- **Vertical**: topic bucket (e.g., “systems/incentives”, “AI threat framing”).
- **Hook Type**: the opening mechanism (first 1–2 seconds).
- **Variant**: a controlled change to exactly one variable.
- **Experiment**: a set of variants run under the same conditions.
- **Decision**: keep / iterate / kill / scale, recorded with reason.

---

## 3) System principles

- **Truth of operation:** optimize *patterns*, not personalities.
- **Constraint-first:** rules → stability → learnable signal.
- **Single source of truth:** one tracker controls analytics.
- **Reproducibility:** all claims auditable to raw metrics.
- **Safety-first:** no tactic is worth a ban or demonetization.

---

## 4) Content constraints (allowed / forbidden)

### Allowed

- Systems, incentives, mechanisms, pattern recognition.
- Fictional or abstract dystopian narratives.
- Neutral synthetic voice; no personal identity story.
- Visuals that do not require a face or a real person.

### Forbidden (hard bans)

- Political targeting or persuasion content.
- Medical claims, diagnosis, treatment guidance.
- Financial advice, “get rich” promises, investment claims.
- Hate, harassment, slurs, dehumanization, protected-class targeting.
- Sexual content involving minors; any exploitative sexual content.
- Instructions for wrongdoing, fraud, violence, or self-harm.
- Deceptive engagement tactics (buying views/likes, bots, artificial amplification).
- Copyright infringement (unlicensed music/video, reuploads, watermarked rips).

### Platform compliance clause

If a platform policy is stricter than these rules, adopt the stricter policy.

---

## 5) Data integrity (invalid samples)

A **sample is invalid** if any of the following are true:

- The post is paid/boosted/promoted (organic-only datasets).
- The post was mass-reposted by automation that changes timing/metadata inconsistently.
- The post is materially edited after publication in a way that affects distribution (caption rewrite, thumbnail swap, audio swap) without resetting it as a new sample.
- The post is removed/re-uploaded and treated as the same row.
- Metrics are captured outside a defined window or with missing required fields.
- The account is under known restriction (age gate, warning, limited eligibility) during the experiment window.

**Rule:** if it’s invalid, it does not enter the decision set. Mark it `INVALID` and record the reason.

---

## 6) Governance logic

- **Change control:** any change to templates, publishing cadence, or scoring must be versioned and dated.
- **One-variable discipline:** change *one* variable per variant unless explicitly running a multi-factor experiment.
- **Decision transparency:** every kill/scale decision must cite the metric threshold and the sample set used.
- **No retroactive rewriting:** do not “massage” categories to make a narrative look better. If taxonomy changes, map old → new.

---

## 7) Signal quality protection

### Keep experiments isolated

- Do not mix different verticals/hook tests in the same time slot if you’re trying to compare them.
- Avoid running multiple major changes simultaneously (new template + new vertical + new cadence).

### Keep inputs stable

- Use consistent length bands and structure (per README format spec).
- Keep voice and visual style stable within an experiment.

### Keep metadata stable

- Use consistent caption style conventions and hashtag policy (either fixed set or none).
- Avoid trending-audio “lottery” if the goal is to measure hook mechanics.

---

## 8) Drift rules

Drift is any shift that makes performance non-comparable across time.

Common causes:

- Template changes without versioning.
- Algorithm seasonality (holidays, major events) not annotated.
- Account state changes (restrictions, eligibility, audience region shifts).
- Switching content sources (visual library, voice model, editing style).

**Rule:** whenever drift is suspected, start a new experiment block and annotate the transition.

---

## 9) Monetization safety

Hard protections:

- No copyrighted assets unless licensed and traceable.
- No deceptive claims (before/after promises, fake testimonials, “guaranteed results”).
- No impersonation, deepfake of real people, or misrepresentation.
- No engagement bait that violates platform policies (spammy CTAs, comment bait, “follow for part 2” if prohibited).

**Rule:** monetization safety overrides short-term engagement.

---

## 10) Identity isolation rules

- Do not store personal data (names, emails, phone numbers, addresses) in the repo or tracker.
- Do not build “founder lore” content; the system is the product.
- Keep credentials out of this repo (use a password manager / secrets vault).
- Avoid linking accounts to real-world identity unless intentionally entering the Forge/brand phase.

---

## 11) Anti-bias rules

- Do not target or profile protected classes.
- Do not use stereotyping, coded hate, or dehumanizing frames.
- Prefer neutral, systems-level language over blame and scapegoating.
- When analyzing comments, separate *engagement volume* from *harmful sentiment*.

---

## 12) Platform risk controls

- Maintain strict compliance with platform Terms, Community Guidelines, and monetization eligibility rules.
- Do not attempt to evade enforcement actions or reconstitute banned behavior.
- Keep publishing cadence within normal human-operable bounds.
- Security hygiene: use MFA, unique passwords, and least-privilege access.

---

## 13) Kill conditions (stop immediately)

Trigger a kill condition if any occur:

- Policy violation warning/strike related to the content pattern.
- Evidence the vertical reliably attracts disallowed content (hate, harassment, self-harm) in comments.
- Strong negative monetization signal (limited ads, ineligible, demonetization) tied to the pattern.
- Dataset corruption: uncontrolled variables, missing metrics, or invalid samples exceed 20% of the block.

Action:

- Freeze the pattern.
- Record incident + hypothesis.
- Resume only with a revised, policy-safe variant.

---

## 14) Scale conditions (when expansion is permitted)

Scale only when all are true:

- Pattern wins across multiple posts (not a single spike).
- High completion + loop + shares/saves relative to baseline.
- No policy warnings and no monetization risk flags.
- The pattern remains stable under minor variations (voice/visual swaps).

Scaling actions (in order):

1. Increase output for the same pattern.
2. Replicate to an adjacent vertical.
3. Expand platforms only after cross-post consistency.

---

## 15) Repository rules (what lives here)

Allowed in repo:

- Templates, scripts, analytics schemas, decision logs, documentation.

Forbidden in repo:

- Raw clips, renders, CapCut projects, audio libraries, thumbnails.
- Credentials, API keys, tokens, cookies.
- Personal data.

(Keep raw assets in Drive per README.)
