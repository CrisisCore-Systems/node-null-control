# Platform Incidents — Decision Log

**Purpose:** Document platform restrictions, warnings, strikes, and pivot decisions.  
**Governance:** All incidents must be logged here with classification and remediation.

---

## Incident Log

### Incident 001 — TikTok Performance Below Threshold

**Date:** 2026-W05  
**Platform:** TikTok  
**Classification:** Performance failure (non-violation)  
**Status:** CLOSED (pivoted to YouTube)

#### Summary

Ghost network content on TikTok consistently underperformed across multiple verticals and hook types after 4-week controlled test.

#### Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Avg completion % | >40% | 32% | ❌ Below |
| Loop rate | >15% | 12-45% (volatile) | ⚠️ Inconsistent |
| Views @ 24h | >500 | 180-800 | ⚠️ Volatile |
| Shares+Saves rate | >3% | 1.8% | ❌ Below |

#### Root Cause Analysis

1. **Content-platform mismatch:**
   - Systems/mechanism content requires more cognitive processing
   - TikTok optimizes for immediate emotional response
   - Analytical content punished by algorithm

2. **Shadow restriction suspected:**
   - Sudden view drops without explanation
   - No warnings/strikes issued
   - Inconsistent reach across identical content types

3. **Format constraints:**
   - 30s limit insufficient for complex framing
   - Fast-paced culture incompatible with analytical tone

#### Decision

**Pivot to YouTube Shorts as primary distribution surface.**

See: [docs/platform_decisions.md](../docs/platform_decisions.md)

#### Remediation

- TikTok account remains active (secondary distribution)
- No policy violations; no account restrictions
- Preserve content for cross-posting if YouTube succeeds

---

### Incident 002 — YouTube Probe Week 1

**Date:** TBD (2026-W06)  
**Platform:** YouTube Shorts  
**Classification:** Pending  
**Status:** MONITORING

#### Summary

First week of YouTube Shorts test (videos 01-03: AI Displacement vertical).

#### Metrics (to be captured)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Avg view duration % | >40% | — | Pending |
| Views @ 48h | >100 | — | Pending |
| Email signup rate | >5% | — | Pending |
| Platform flags | 0 | — | Pending |

#### Next Review

**Date:** 2026-W06 + 48h after video 03 publish  
**Trigger:** All Week 1 metrics captured  
**Action:** Update this log with results

---

### Incident 003 — YouTube Probe Week 2

**Date:** TBD (2026-W07)  
**Platform:** YouTube Shorts  
**Classification:** Pending  
**Status:** MONITORING

#### Summary

Second week of YouTube Shorts test (videos 04-06: Social Credit vertical).

#### Next Review

**Date:** 2026-W07 + 48h after video 06 publish  
**Trigger:** All Week 2 metrics captured  
**Action:** Update this log with results

---

### Incident 004 — YouTube Probe Week 3

**Date:** TBD (2026-W08)  
**Platform:** YouTube Shorts  
**Classification:** Pending  
**Status:** MONITORING

#### Summary

Third week of YouTube Shorts test (videos 07-09: Attention Economy vertical).

#### Next Review

**Date:** 2026-W08 + 48h after video 09 publish  
**Trigger:** All Week 3 metrics captured  
**Action:** Update this log with results

---

## Incident Classification System

### Severity Levels

1. **CRITICAL** — Account suspended, content removed, monetization blocked
2. **HIGH** — Warning/strike issued, content restricted/demonetized
3. **MEDIUM** — Shadow restriction suspected, reach limited
4. **LOW** — Performance below threshold, no violation

### Response Matrix

| Severity | Response | Timeline |
|----------|----------|----------|
| CRITICAL | Immediate freeze, audit all content, escalate to legal if needed | <24h |
| HIGH | Freeze affected pattern, audit similar content, file appeal if appropriate | <48h |
| MEDIUM | Investigate, run baseline test, adjust if confirmed | 1 week |
| LOW | Document, iterate, pivot if persistent | 2-4 weeks |

---

## Platform Risk Indicators

### Red Flags (immediate freeze)

- Content removal without appeal option
- Account restriction without explanation
- Pattern of shadow restrictions
- Strike issued
- Monetization eligibility threatened

### Yellow Flags (monitor closely)

- Sudden reach drop (>50%) without algorithm changes
- Inconsistent performance across identical content
- Comment toxicity spike
- Increased "not interested" feedback

### Green Flags (continue)

- Stable performance
- Predictable variance
- No warnings/restrictions
- Positive comment sentiment
- Organic growth

---

## Escalation Protocol

### Level 1 — Operator

- Log incident
- Classify severity
- Implement immediate response (freeze if needed)
- Document evidence

### Level 2 — Governor

- Review incident classification
- Approve remediation plan
- Authorize pivot if needed
- Update decision logs

### Level 3 — Legal (if applicable)

- Review platform TOS compliance
- File appeals if warranted
- Assess liability exposure
- Document for potential dispute

---

## Audit Trail Requirements

Every incident entry must include:

- **Date/time** (UTC)
- **Platform**
- **Post ID(s)** affected
- **Classification** (severity + type)
- **Root cause** (if known)
- **Metrics** (before/after)
- **Remediation** (actions taken)
- **Outcome** (resolved/ongoing/escalated)
- **Evidence** (screenshots, emails, analytics snapshots)

---

## Next Review

**Quarterly platform health audit**  
**Next scheduled:** 2026-Q2  
**Trigger:** End of quarter or 5+ incidents logged
