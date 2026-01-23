# Short Script Template (Machine-Consistent)

This template standardizes short-form scripts so experiments stay comparable.

Governance hard-stop rules: [docs/01_rules.md](../../docs/01_rules.md)
Workflow context: [docs/02_workflow.md](../../docs/02_workflow.md)
Analytics definitions: [analytics/schema.md](../../analytics/schema.md)

---

## 0) How to use

- Copy this file for every new script.
- Fill all metadata fields.
- Do not change structure unless you increment `template_version` and start a new experiment block.

---

## 1) Metadata (required)

Use this block exactly. Keep keys stable.

```yaml
script_id: YYYY-MM-DD_platform_vertical_hookstyle_vNN
created_at: YYYY-MM-DD
platform: tiktok | yt_shorts | ig_reels | fb_reels | other
phase: harvest | extract | forge
block_id: BLK-YYYYWww-<shortname>
experiment_id: EXP-<name>
vertical: <string>
hook_type: H<id>_<name>
variant_id: V<id>
control: true | false

template_version: short_script_v1
language: en
voice_style: neutral_tts_v1
visual_style: <label>
duration_target_sec: 20-35

risk_review: pending | passed | blocked
risk_notes: <short>

primary_hypothesis: <one sentence>
variable_changed: <exactly one variable>
controls_held: <comma-separated list>

forbidden_topics_checked: true
copyright_check: true
```

---

## 2) Format requirements (non-negotiable)

### Timing + pacing

- Target duration: **20–35s**.
- Sentence count: **8–13** total.
- Sentence length: **6–12 words** each (avoid long clauses).
- Voice cadence: short, flat, neutral.

### Language constraints

- Use plain English.
- Use declarative sentences.
- Avoid rhetorical questions unless explicitly testing them.
- Avoid intensifiers (“literally”, “insanely”, “unbelievably”) unless they are the variable being tested.
- Avoid filler (“you know”, “like”, “basically”, “just”).

### Syntax rules

- One idea per sentence.
- No parentheses in spoken lines.
- No emojis.
- No hashtags inside the script.
- No self-reference (no “I”, no personal story).

### Consistency rules

- If `variant_id` changes, **only one** of the following may change:
  - hook line, or
  - one sentence in the middle, or
  - last line loop, or
  - one stylistic variable (voice/visual), or
  - caption (if captions are tracked)

If more than one changes, mark as multi-factor and do not compare as a clean A/B.

---

## 3) Forbidden phrasing (hard bans)

Do not include:

- Medical advice/claims: diagnosis, cures, “this treats…”, “doctor-approved”.
- Financial advice/claims: “buy this”, “invest in…”, “guaranteed returns”.
- Political targeting: “vote”, “party”, calls for political action.
- Violence/incitement: threats, instructions, praise of harm.
- Hate/harassment: slurs, protected-class targeting, dehumanization.
- Deception: “this is real footage” if it’s not; impersonation.
- Begging CTAs: “please like”, “smash follow”, “comment YES”.
- Identity hooks: “my story”, “as someone who…”, “I used to…”.

If any appear, set `risk_review: blocked` and stop.

---

## 4) Hook structure (0.0–1.5s)

Choose exactly one hook pattern (unless explicitly testing combos).

- **H1 (Contradiction):** “Everyone believes X. X is backwards.”
- **H2 (Mechanism):** “This isn’t about X. It’s about the mechanism behind X.”
- **H3 (Threat framing):** “The risk isn’t obvious. It’s structural.”
- **H4 (Pattern reveal):** “Watch what happens when Y appears.”

Hook rules:

- First line must be under **10 words**.
- No proper nouns unless the experiment tests them.

---

## 5) Body structure (1.5–22s)

### Segment A — Threat framing (1.5–5s)

- Define the tension.
- No moralizing.

### Segment B — Disturbing insight (5–13s)

- Deliver one crisp mechanism.
- Prefer “because” clauses once, not repeatedly.

### Segment C — Escalation (13–22s)

- Increase stakes without policy risk.
- No calls to action.

---

## 6) Open-loop mechanics (22–28s)

Goal: end with unresolved tension that invites reflection without policy risk.

Allowed loop endings:

- Unanswered implication: “And that’s why the pattern keeps repeating.”
- Constraint cliff: “The system only works until one variable flips.”
- Boundary tease: “There’s one rule they never explain.”

Forbidden loop endings:

- “Follow for part 2” if prohibited by platform policy.
- Direct engagement baiting.
- Claims designed to mislead.

---

## 7) Script (fill-in)

### On-screen text (optional)

- Line 1 (hook): <10 words>
- Line 2: <6–10 words>

### Voice script (required)

[01] <Hook line>
[02] <Threat framing>
[03] <Threat framing>
[04] <Insight>
[05] <Insight>
[06] <Escalation>
[07] <Escalation>
[08] <Open loop>

---

## 8) Variant markers (for clean experiments)

Declare what changed in machine-readable form:

```text
VARIANT_CHANGE:
- changed: <hook|mid_line|end_line|caption|voice_style|visual_style|other>
- from: <control value>
- to: <variant value>
```

---

## 9) Packaging metadata (optional but recommended)

```yaml
caption_style: minimal | none | narrative
hashtag_policy: none | fixed_set | platform_default
audio_policy: original | licensed | platform_library
subtitle_style: template_v1
```

---

## 10) QC checklist (must pass before publish)

- Matches the structure and sentence constraints
- One-variable change confirmed (or explicitly multi-factor)
- Forbidden phrasing check passed
- No policy-sensitive claims
- Template/variant IDs filled
- `risk_review: passed`
