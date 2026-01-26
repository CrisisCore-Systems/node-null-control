# Hooks (Controlled Library)

**Hook taxonomy** and controlled structures for clean experiments.

- Governance hard-stop rules: [docs/01_rules.md](../../docs/01_rules.md)
- Workflow context: [docs/02_workflow.md](../../docs/02_workflow.md)
- Analytics definitions + Hook Type usage: [analytics/schema.md](../../analytics/schema.md)
- Script packaging template: [ops/templates/short_script_template.md](../templates/short_script_template.md)

---

## 0) Purpose

Hooks are the highest-leverage variable. Ad hoc hooks corrupt the dataset.

This doc turns hooks into:

- **Taxonomy** (stable labels)
- **Structures** (repeatable patterns)
- **Variation knobs** (testable, one-variable changes)
- **Libraries** (prebuilt candidates)
- **Analytics mapping** (so tracker fields are consistent)

---

## 1) Versioning rules

- Current hook library version: `hooks_v1`
- Any change to:
  - taxonomy IDs (H1/H2/...)
  - allowed/forbidden constructions
  - default variation knobs

…requires:

- incrementing the version, and
- starting a new experiment block, and
- documenting the change in the weekly change log.

---

## 2) Hook Type field mapping (tracker + templates)

**Tracker field:** `Hook Type`

**Template field:** `hook_type: H<id>_<name>`

Rules:

- Hook Type must be one of the IDs below.
- Never rename an ID mid-block.
- If a hook does not fit, create a new ID in the next version (do not “shoehorn” it).

---

## 3) Global hook constraints (apply to every type)

### 3.1 Timing + length

- Hook occupies ~0.0–1.5s.
- Spoken first line should be **under 10 words**.
- Prefer 1–2 sentences max.

### 3.2 Language constraints

- Plain English.
- Declarative.
- No complex clauses.
- Avoid rhetorical questions unless explicitly testing them.

### 3.3 Forbidden constructions (hard bans)

These invalidate the hook for this system:

- Medical or financial advice/claims.
- Political targeting/persuasion.
- Hate/harassment/protected-class targeting.
- Violence/incitement or wrongdoing instructions.
- Deceptive framing (“real leaked footage”) unless verifiably true and policy-safe.
- Engagement begging (“like/follow/comment”).
- Identity-story hooks (“my story”, “I used to…”, personal confessions).

If any appear: block the script.

### 3.4 Allowed cognitive triggers (safe set)

- Contradiction
- Mechanism reveal
- Hidden constraint
- Pattern recognition
- System tension
- Consequence framing (non-violent, non-inciting)

---

## 4) Taxonomy (Hook Types)

Each Hook Type has:

- **Name** (stable)
- **Core structure** (linguistic skeleton)
- **Pattern family** (what it’s doing)
- **Test knobs** (what you can vary)

### H1 — Contradiction

**Family:** contradiction / reversal.

**Core structures:**

- “Everyone thinks X. It’s actually Y.”
- “X looks like the answer. X is the trap.”

**Cognitive trigger:** expectation break.

**Test knobs (one at a time):**

- Swap `X` topic framing only.
- Swap certainty level: “everyone” → “most people”.
- Swap punch word: “trap” → “constraint”.

---

### H2 — Mechanism

**Family:** mechanism / causality.

**Core structures:**

- “This isn’t about X. It’s about the mechanism behind X.”
- “X happens because the system rewards Y.”

**Cognitive trigger:** explanatory power.

**Test knobs:**

- Mechanism noun: “mechanism” → “incentive” → “feedback loop”.
- Specificity: abstract mechanism → one concrete mechanism.

---

### H3 — Threat Framing (Structural)

**Family:** structural risk.

**Core structures:**

- “The risk isn’t obvious. It’s structural.”
- “The danger isn’t X. It’s the hidden constraint.”

**Cognitive trigger:** vigilance / tension.

**Test knobs:**

- Replace “risk” with “failure mode”.
- Change abstraction level (high-level vs specific constraint).

---

### H4 — Pattern Reveal

**Family:** pattern recognition.

**Core structures:**

- “Watch what happens when Y appears.”
- “Every time Y happens, the same outcome follows.”

**Cognitive trigger:** curiosity + prediction.

**Test knobs:**

- Change the pattern cue (Y) only.
- Change temporal framing: “every time” → “eventually”.

---

### H5 — Hidden Rule

**Family:** hidden rule / boundary.

**Core structures:**

- “There’s one rule that explains all of this.”
- “The system runs on one rule nobody says out loud.”

**Cognitive trigger:** forbidden knowledge (without policy risk).

**Test knobs:**

- “rule” → “constraint” → “tradeoff”.
- Add/remove “nobody says out loud”.

---

### H6 — False Choice

**Family:** false binary / reframing.

**Core structures:**

- “It’s not X vs Y. It’s Z.”
- “Both sides miss the same variable.”

**Cognitive trigger:** reframing + superiority impulse.

**Test knobs:**

- Replace “both sides” with “most people”.
- Swap the single variable in Z.

---

### H7 — Constraint Cliff

**Family:** constraint cliff / limit.

**Core structures:**

- “This works… until one variable flips.”
- “It’s stable until the constraint shows up.”

**Cognitive trigger:** instability + anticipation.

**Test knobs:**

- Swap “variable” → “constraint” → “threshold”.
- Name the variable (generic vs specific).

---

### H8 — Cost Reveal

**Family:** cost / tradeoff.

**Core structures:**

- “The cost isn’t money. It’s attention.”
- “The price of X is always Y.”

**Cognitive trigger:** moral accounting without moralizing.

**Test knobs:**

- Swap the cost type (attention/time/optionality).
- Tighten language (“always” → “usually”).

---

## 5) Allowed constructions (building blocks)

Use these as the hook’s atoms.

### 5.1 Phrase primitives

- “Everyone thinks…” / “Most people think…”
- “This isn’t about…”
- “It’s not X. It’s Y.”
- “The real variable is…”
- “The hidden constraint is…”
- “Watch what happens when…”
- “It only works until…”

### 5.2 Safe nouns (preferred)

- system, incentive, constraint, feedback loop, mechanism, pattern, signal, tradeoff, threshold

### 5.3 Safe verbs (preferred)

- rewards, selects, amplifies, compresses, repeats, drifts, collapses, stabilizes

---

## 6) Forbidden constructions (examples)

These patterns are disallowed even if the topic seems “safe”:

- “Doctors don’t want you to know…” (medical claim framing)
- “This will make you rich…” (financial claim framing)
- “Vote/Support/Join…” (political targeting)
- “Real leaked footage…” (deception risk)
- “Like/follow/comment…” (engagement begging)
- “As a [identity]…” (identity anchoring)

---

## 7) Testable variations (one-variable knobs)

When running A/B tests, only change one knob.

### 7.1 Hook-only knobs (preferred)

- **Topic swap:** change X/Y subject only.
- **Certainty:** “always” ↔ “usually” ↔ “often”.
- **Authority distance:** “everyone” ↔ “most people”.
- **Punch word:** “trap/constraint/threshold”.
- **Syntax:** one sentence ↔ two short sentences.

### 7.2 Prohibited variation knobs

Do not use these as “tests”:

- Adding policy-risk content for shock.
- Adding engagement begging.
- Adding misinformation.

---

## 8) Experimental grouping (clean blocks)

### 8.1 Block structure

A block should hold constant:

- platform
- duration band
- template version
- voice style
- visual style
- caption/hashtag policy

The block changes exactly one variable:

- Hook Type, or
- hook text within a Hook Type, or
- one mid-line, or
- end loop line

### 8.2 Recommended grouping strategy

- Week N: test Hook Types across the same vertical (type comparison).
- Week N+1: test best Hook Type’s text variations (within-type optimization).
- Week N+2: replicate the winning hook in an adjacent vertical (portability).

---

## 9) Hook library (starter set)

These are neutral, system-level candidates designed to be safe and reusable.

### H1 (Contradiction) — candidates

- “Everyone optimizes for speed. Speed breaks the signal.”
- “More content isn’t leverage. Consistency is leverage.”
- “The problem isn’t effort. It’s uncontrolled variables.”

### H2 (Mechanism) — candidates

- “This isn’t about luck. It’s about feedback loops.”
- “Virality isn’t random. It rewards one behavior.”
- “Most systems fail because incentives drift.”

### H3 (Threat framing) — candidates

- “The risk isn’t obvious. It’s structural.”
- “The failure mode isn’t noise. It’s drift.”
- “The danger is subtle: you stop measuring.”

### H4 (Pattern reveal) — candidates

- “Watch what happens when one metric becomes the goal.”
- “Every time the rules loosen, the signal collapses.”
- “When the template changes, comparisons break.”

### H5 (Hidden rule) — candidates

- “There’s one rule that decides everything.”
- “The system runs on one constraint you can’t ignore.”
- “One hidden rule explains the whole pattern.”

### H6 (False choice) — candidates

- “It’s not content vs distribution. It’s measurement.”
- “It’s not creativity vs discipline. It’s control.”
- “Both sides miss the same variable.”

### H7 (Constraint cliff) — candidates

- “This works… until one variable flips.”
- “It’s stable until the constraint shows up.”
- “It only works until the loop breaks.”

### H8 (Cost reveal) — candidates

- “The cost isn’t money. It’s attention.”
- “The price of speed is distortion.”
- “The real cost is losing comparability.”

---

## 10) Logging requirements (so analytics stays clean)

Whenever you use a hook from this library:

- Record the Hook Type ID (H1/H2/…)
- Copy the exact first spoken line into `First line / Hook text`
- Record the hook candidate label in Notes (recommended)

Recommended Notes pattern:

- `HOOK_LIB: hooks_v1/H2/02`

---

## 11) Maintenance rules

- Add new candidates only after a weekly review.
- Retire candidates that repeatedly underperform.
- Never delete candidates retroactively; mark as `RETIRED` with date.
- Keep the library conservative: clarity > cleverness.
