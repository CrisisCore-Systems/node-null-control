# Caption Template (Experiment-Safe Packaging)

This template controls captions so packaging does not drift and corrupt comparisons.

Hard boundaries: [docs/01_rules.md](../../docs/01_rules.md)
Workflow reference: [docs/02_workflow.md](../../docs/02_workflow.md)
Analytics definitions: [analytics/schema.md](../../analytics/schema.md)
Hook taxonomy (if referenced): [ops/prompts/hooks.md](../prompts/hooks.md)

---

## 0) Principles

- Captions are a **variable**. Treat them like hooks: controlled, labeled, and comparable.
- If you are not explicitly testing captions, captions must be **held constant** within the experiment block.
- Captions must be **engagement-neutral**: no begging, no manipulative CTAs, no policy-risk bait.

---

## 1) Metadata (required)

Use this block exactly. Keep keys stable.

```yaml
caption_id: CAP-YYYY-MM-DD-<short>
caption_version: caption_v1
platform: tiktok | yt_shorts | ig_reels | fb_reels | other
phase: harvest | extract | forge
block_id: BLK-YYYYWww-<shortname>
experiment_id: EXP-<name>
variant_id: V<id>
control: true | false

caption_style: minimal | narrative | none
length_band: short | medium | long
hashtag_policy: none | fixed_set | platform_default
cta_policy: none | soft | prohibited

semantic_density: low | medium | high
risk_review: pending | passed | blocked
risk_notes: <short>

variable_changed: <caption_text|hashtags|cta|format|other>
controls_held: <comma-separated list>
analytics_notes_tag: CAP_LIB: caption_v1/<band>/<id>
```

---

## 2) Length bands (lock these)

Choose exactly one band.

- **short:** 0–80 characters
- **medium:** 81–160 characters
- **long:** 161–300 characters

Rules:

- Do not exceed platform limits.
- Do not mix bands within the same block unless the band is the tested variable.

---

## 3) Syntax structure (stable patterns)

Pick one structure and keep it constant unless explicitly testing.

### S1 — Minimal (default)

- 1 sentence.
- No line breaks.

Pattern:

- `<mechanism claim>. <open-loop fragment>.`

### S2 — Two-line (only if stable in block)

- 2 short lines.
- 1 line break.

Pattern:

- Line 1: `<mechanism claim>`
- Line 2: `<open-loop fragment>`

### S3 — Tag line (optional)

- Add a final short tag line only if it’s held constant.

Pattern:

- `<mechanism claim>. <open-loop fragment>. <tag>`

---

## 4) CTA policy (engagement neutrality)

### Allowed

- **none (recommended):** no CTA.
- **soft (rare):** a neutral statement that does not beg.

Examples:

- “Unresolved for a reason.”
- “Same pattern. Different surface.”

### Forbidden

These are not allowed in this system:

- “Like/follow/comment/share/save” requests.
- “Follow for part 2” (or any equivalent) unless you have verified it is policy-safe on the platform and you are explicitly testing it.
- Comment bait (“Comment YES”, “Which one are you?”).
- Manipulative urgency (“Before it’s deleted”, “They don’t want you to see this”).

If any appear: set `risk_review: blocked`.

---

## 5) Hashtag policy

Hashtags are a packaging variable.

### Allowed policies

- **none (recommended for clean tests):** no hashtags.
- **fixed_set:** a stable, pre-defined set (same order) used for all posts in the block.
- **platform_default:** only if you accept that it injects noise; annotate.

### Fixed set rules

- Maximum 3–5 hashtags.
- No trending-chasing unless that is the variable.
- No policy-sensitive tags.

---

## 6) Monetization safety rules (caption-specific)

Hard bans in captions:

- Medical claims (diagnosis/treatment/cures).
- Financial advice/guarantees.
- Impersonation or deceptive framing.
- Copyright claims you cannot support.
- Defamation or targeted harassment.

Captions must not increase risk beyond the content itself.

---

## 7) Allowed constructions (safe building blocks)

Use system-level language.

Preferred nouns:

- system, incentive, constraint, signal, pattern, tradeoff, threshold

Preferred verbs:

- rewards, selects, amplifies, repeats, drifts, collapses

Preferred fragments:

- “The mechanism is simple.”
- “The constraint stays hidden.”
- “Watch the pattern repeat.”
- “It only works until it doesn’t.”

---

## 8) Forbidden constructions (examples)

- “Doctors don’t want you to know…”
- “Guaranteed results…”
- “Real leaked footage…”
- “Before it’s deleted…”
- “Like/follow/comment…”
- “My story…”

---

## 9) Experiment-safe variations (one-variable knobs)

If you are testing captions, change **one** knob only:

- **Band:** short ↔ medium ↔ long
- **Structure:** S1 ↔ S2
- **Punch word:** “constraint” ↔ “threshold”
- **Certainty:** “always” ↔ “usually”
- **Hashtags:** none ↔ fixed_set (not both content + hashtags)

If multiple knobs change, mark as multi-factor and do not compare as a clean test.

---

## 10) Platform variants (controlled)

Use identical caption text across platforms by default.

Only allow platform variants if the platform requires it (length limits or formatting) and record it:

- `PLATFORM_VARIANT: true`
- `PLATFORM_VARIANT_REASON: limit|format|other`

---

## 11) Caption fill-in (copy/paste)

### Caption text

Choose your band + structure and write the caption here:

```text
<CAPTION_TEXT>
```

### Hashtags (if fixed_set)

```text
<HASHTAGS>
```

---

## 12) Logging requirements (analytics mapping)

To keep analytics clean:

- Record the chosen `caption_style`, `length_band`, `hashtag_policy`, and `cta_policy` in your Notes (or dedicated columns if you add them).
- If you are testing captions, set `variable_changed: caption_text` (or the precise knob).
- Include the library tag (recommended):
  - `CAP_LIB: caption_v1/<band>/<id>`

If you cannot trace a caption variant to a labeled knob, treat the sample as noisy.
