# Platform Decisions — YouTube Probe Launch

**Phase:** Ghost Network → Brand Emergence Transition  
**Context:** CrisisCore Systems platform pivot from TikTok → YouTube Shorts  
**Decision Date:** 2026-W06

---

## Decision Summary

**Pivot from TikTok to YouTube Shorts as primary distribution surface for CrisisCore Systems brand emergence.**

### Rationale

1. **TikTok performance below threshold:**
   - Avg completion rate: 32% (target: >40%)
   - Loop rate: inconsistent (12-45% variance)
   - Platform inconsistency (shadow restrictions suspected)
   - See: `analytics/decisions/platform_incidents.md`

2. **YouTube Shorts advantages:**
   - Longer content window (60s vs 30s) allows more complex framing
   - More stable analytics infrastructure
   - Better integration with email capture via pinned comments
   - Lower platform risk for systems/mechanism content
   - Native title field allows clearer framing

3. **Monetization architecture alignment:**
   - YouTube → Email → Product funnel better suited to CrisisCore positioning
   - Displacement Risk Atlas product requires audience sophistication
   - YouTube audience demographics better match target buyer profile

### Decision Type

**Strategic Pivot** (not abandonment—TikTok remains secondary distribution option)

---

## Test Parameters

### 3x3 Test Matrix

**3 Verticals:**
1. AI Displacement
2. Social Credit Systems
3. Attention Economy

**3 Hook Types:**
- H1 (Question)
- H2 (Statement)
- H3 (Contrast)

**Total:** 9 videos across 3 weeks

### Success Criteria (Scale)

- >40% avg view duration
- >5% signup rate (views → emails)
- >1% email → product conversion
- No platform risk flags

### Kill Criteria (Abandon YouTube probe)

- <100 views per video after 48h (3 consecutive videos)
- Email signup rate <1% of views
- Platform flags content
- Comments indicate brand confusion

### Iterate Criteria (Adjust but continue)

- Moderate views (100-1k) but low signups → improve CTA
- Good signups but low opens → improve subject lines
- Good opens but low conversions → improve product positioning

---

## Implementation Timeline

### Week 1 (2026-W06)
- Upload videos 01-03 (AI Displacement vertical)
- Publish schedule: 1 video every 2-3 days
- Capture windows: 2h, 24h, 48h

### Week 2 (2026-W07)
- Upload videos 04-06 (Social Credit vertical)
- Launch email capture form (forge/index.html)
- Begin email sequence automation

### Week 3 (2026-W08)
- Upload videos 07-09 (Attention Economy vertical)
- Launch Displacement Risk Atlas product (Gumroad)
- Send first product offer email to Week 1 signups

### Week 4 (2026-W09)
- Decision gate: Kill / Scale / Iterate
- Review against decision criteria
- Document results in platform_incidents.md

---

## Risk Assessment

### Platform Risk: **LOW**

- Content is procedural/analytical (no advice claims)
- No political targeting
- No medical/financial claims
- Factual mechanism analysis only

### Monetization Risk: **LOW**

- Email-based funnel (platform-agnostic)
- Product hosted off-platform (Gumroad)
- No platform monetization dependency

### Brand Risk: **MEDIUM**

- First branded emergence from Ghost network
- Comments may reveal brand confusion
- Mitigation: clear "no hype, no predictions" framing in all materials

### Execution Risk: **LOW**

- Scripts already written
- Templates established
- Automation wiring documented

---

## Rollback Plan

If YouTube probe fails (kill criteria met):

1. **Preserve Ghost network operations** (continue anonymous pattern harvesting)
2. **Delay brand emergence** (return to Extract phase)
3. **Alternative paths:**
   - Long-form YouTube (15-30 min deep dives)
   - Blog/newsletter primary (no video)
   - LinkedIn thought leadership (text-based)
   - Substack + Twitter combo

---

## Governance Alignment

This decision aligns with:

- [docs/01_rules.md](01_rules.md) — No policy violations, no identity exposure risks
- [docs/02_workflow.md](02_workflow.md) — Extract → Forge transition criteria met
- [analytics/schema.md](../analytics/schema.md) — YouTube metrics schema added
- [monetization/product_engine.md](../monetization/product_engine.md) — Product-engine readiness confirmed

---

## Approval Trail

- **Proposed by:** CrisisCore Systems operator
- **Reviewed by:** Governance layer (01_rules.md compliance)
- **Approved on:** 2026-02-03
- **Status:** APPROVED — Execute Week 1 uploads

---

## Next Review

**Date:** 2026-W09 (post-Week 3 completion)  
**Trigger:** All 9 videos published + 48h capture complete  
**Outcome:** Kill / Scale / Iterate decision based on criteria above
