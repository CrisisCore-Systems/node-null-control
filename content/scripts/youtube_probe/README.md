# YouTube Probe Scripts — Test Matrix

**Phase:** Ghost Network (Harvest)  
**Platform:** YouTube Shorts  
**Purpose:** Test CrisisCore Systems brand emergence via controlled content vertical testing

---

## Test Matrix Structure

**3 Verticals × 3 Hooks = 9 Scripts**

### Verticals
1. **AI Displacement** — Labor market disruption mechanisms
2. **Social Credit** — Distributed reputation/scoring systems
3. **Attention Economy** — Infrastructure of modern attention capture

### Hook Types
- **H1 (Question)** — Open-ended question hook (curiosity)
- **H2 (Statement)** — Bold declarative statement (tension)
- **H3 (Contrast)** — "Not X. Actually Y." (pattern interrupt)

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
- Completion %
- Average view duration
- Loop/replay rate
- Saves + Shares (distribution intent)

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
