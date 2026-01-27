# node-null-control
Anonymous attention-harvesting network control plane: templates, automation, analytics, and decision systems for Ghost → Brand emergence.

Start here (plain-language mental model): [docs/00_mental_model.md](docs/00_mental_model.md)

Quick start (dev + governance gates): [docs/QUICKSTART.md](docs/QUICKSTART.md)

Contributing (pre-commit, CI, conventions): [CONTRIBUTING.md](CONTRIBUTING.md)

**Rule:** raw clips, renders, CapCut projects, audio, thumbnails = Drive only.

---

## Content Rules (Non-Negotiable)

### What we do
- Systems, incentives, patterns, mechanisms
- Short, unresolved, loop-friendly narratives
- Neutral synthetic voice (no personality)
- Abstract/dystopian visuals (no face required)

### What we don’t do
- No political targeting
- No medical claims
- No financial advice
- No incitement/violence
- No “call to action” begging
- No identity story

**We are building distribution infrastructure, not a persona.**

---

## Short-Form Format Spec

**Length:** 20–35s (default)  
**Structure:**
- 0.0–1.5s: Hook
- 1.5–5s: Threat framing
- 5–13s: Disturbing insight
- 13–22s: Escalation
- 22–28s: Open loop (no resolution)

**Always end unresolved** (forces comments + rewatch + follow-up demand).

---

## Tracking (Single Source of Truth)

Use one Google Sheet (recommended) named: `NODE_NULL_TRACKER`.

Tabs:
- Posts (every upload = one row)
- Hooks (hook type performance)
- Verticals (topic performance)
- Weekly Summary
- Kill/Scale Decisions

Minimum columns for `Posts`:
- Date
- Platform
- Vertical
- Hook Type
- First line / Hook text
- Duration (sec)
- Visual Style
- Voice Style
- Views 1h
- Views 24h
- Avg view duration
- Completion %
- Loop %
- Shares
- Saves
- Comments
- Notes
- Decision (keep / iterate / kill)

---

## Operating Cadence

### Daily (15–25 min)
- Publish scheduled posts
- Record metrics for yesterday’s posts
- Tag winners/losers

### Weekly (45–60 min)
- Rank verticals by: retention, loop rate, shares/saves
- Kill ~30–50% of underperformers
- Double down on top 20%
- Document decisions in:
  - `analytics/decisions/killlog.md`
  - `analytics/decisions/scalelog.md`

### Monthly
- If a vertical dominates consistently → begin **Forge** phase (brand emergence)
- Otherwise keep harvesting patterns

---

## Kill / Scale Logic (Simple, brutal)

Kill if (after enough samples):
- weak retention + weak shares/saves
- no improvement after 2 iterations

Scale if:
- high completion + high loop + strong shares/saves
- consistent across multiple posts (not a one-off spike)

**You are not optimizing content. You are selecting a winning pattern.**

---

## Tooling Notes

Stack:
- Scripts: ChatGPT
- Voice: ElevenLabs (neutral synthetic)
- Visuals: Runway / Pika / stock loops
- Edit: CapCut templates (auto subtitles + loop cut)
- Cross-post: Repurpose.io
- Schedule: Buffer
- Automations: Make.com / Zapier

Keep credentials outside the repo.

---

## Getting Started (Checklist)

1) Create accounts (TikTok / Shorts / Reels / FB Reels)
2) Build 1 CapCut master template (subtitles + loop ending)
3) Create Drive structure + naming conventions
4) Create the Google Sheet tracker
5) Start Week 1: controlled publishing + clean data collection

---

## Naming Conventions

**Short IDs:**
`YYYY-MM-DD_platform_vertical_hookstyle_v01`

Example:
`2026-01-22_yt_AIThreat_H1_v01`

---

## License / Compliance

Templates and analytics schema only.
No copyrighted assets, personal data, or credentials in this repo.

---

## Status

- Phase: **Ghost Network (Harvest)**
- Goal: **Extract the winning vertical + hook pattern**
- Next: **Brand Emergence (Forge) only after dominance**

---

## Forge (Routing Interface)

Neutral conversion interface (no personal branding):

- Forge node: [forge/README.md](forge/README.md)
