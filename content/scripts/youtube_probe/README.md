# YouTube Probe Scripts — Test Matrix

**Phase:** Ghost Network (Harvest)  
**Platform:** YouTube Shorts  
**Purpose:** Test CrisisCore Systems brand emergence via controlled content vertical testing

---

## Test Matrix Structure

**3 Verticals × 3 Hook Types = 9 Scripts**

### Verticals
1. **AI Displacement** — Labor market disruption mechanisms
2. **Social Credit** — Distributed reputation/scoring systems
3. **Attention Economy** — Infrastructure of modern attention capture

### Hook Types (Threat-First Strategy)

Based on analytics feedback showing that threat-first framing dramatically improves stayed-to-watch rates:

- **H1 (Consequence)** — Open with an immediate consequence ("Your job doesn't disappear. It gets cheaper.")
- **H2 (Trap)** — Open with a trap the viewer is already in ("The ladder is being pulled up.")
- **H3 (Loss)** — Open with something already lost ("You still have a job. You just lost your leverage.")

### Hook Rules (Mandatory)

- First sentence must be **under 10 words**
- **No questions** as hooks (questions don't stop thumbs)
- **No corrections** ("Why X is wrong", "People misunderstand...")
- **No academic language** ("mechanism", "paradigm", "metric")
- First frame must **change visually in <0.5s** with one brutal sentence
- Open with **consequence/trap/loss/timeline** — corrections come later

### Anti-Patterns (Kill These)

❌ "Why X is the wrong metric"  
❌ "People misunderstand..."  
❌ "The real issue is..."  
❌ "What if..." (rhetorical questions)  
❌ Calm framing in first 0.8 seconds  
❌ Analytical language that requires effort to process

---

## Script Naming Convention

`{NN}_{vertical}_{hook}.md`

Examples:
- `01_ai_displacement_h1.md`
- `04_social_credit_h1.md`
- `07_attention_economy_h1.md`

---

## Test Objectives

### Primary Metrics (per docs/02_workflow.md)
- **Stayed to watch:** ≥35% (critical)
- **Avg view duration:** ≥15s on ~30s video
- **Loop/replay rate**
- **Saves + Shares** (distribution intent)

### Secondary Signals
- Impressions (YouTube Studio metric)
- CTR on thumbnail
- Comment quality/toxicity
- Pinned comment → landing page click rate

### Kill Criteria
- <100 views per video after 48h (3 consecutive videos)
- Email signup rate <1% of views
- Platform flags content
- Comments indicate brand confusion

### Scale Criteria
- >40% avg view duration
- >5% signup rate (views → emails)
- >1% email → product conversion
- No platform risk flags

---

## Publishing Cadence

**Week 1:** AI Displacement vertical (scripts 01-03)  
**Week 2:** Social Credit vertical (scripts 04-06)  
**Week 3:** Attention Economy vertical (scripts 07-09)

**Publishing schedule:** 1 video every 2-3 days  
**Capture windows:** 2h, 24h, 48h

---

## On-Screen Text Requirements

Each script includes mandatory first-frame text:

| Script | First Frame Text |
| :--- | :--- |
| 01 | WAGES COLLAPSE FIRST |
| 02 | THE LADDER IS GONE |
| 03 | LEVERAGE DESTROYED |
| 04 | ACCESS DENIED |
| 05 | YOU'RE BEING SCORED |
| 06 | BANNED WITHOUT APPEAL |
| 07 | YOU'RE THE INVENTORY |
| 08 | ENGINEERED COMPULSION |
| 09 | RAGE GETS REWARDED |

---

## Compliance

All scripts follow governance rules in `docs/01_rules.md`:

✅ Systems/mechanisms framing (no personal advice)  
✅ No political targeting  
✅ No medical claims  
✅ No financial advice  
✅ No incitement/violence  
✅ Procedural language only  

---

## Pinned Comment Template

Each video includes a pinned comment directing to the landing page:

```
Pattern documentation: [landing page URL]

CrisisCore Systems analyzes displacement mechanisms, distributed credit systems, and attention infrastructure. Field notes delivered weekly.
```

---

## Integration Points

- **Analytics:** `analytics/tracker_youtube_extension.md`
- **Platform Incidents:** `analytics/decisions/platform_incidents.md`
- **Decision Logs:** `analytics/decisions/killlog.md`, `analytics/decisions/scalelog.md`
- **Platform Pivot Log:** `docs/platform_decisions.md`
- **Email Funnel:** `automation/email_automation.md`
- **Product Conversion:** `products/displacement_risk_atlas/README.md`

---

## Status

- Phase: **Testing (Week 1)**
- Videos Published: 0/9
- Next Action: Upload scripts 01-03 (AI Displacement vertical)
