---
type: adversarial_scenario
domain: [security | business | legal | product | operations | platform | content | analytics]
confidence: [high | medium | low]
last_updated: YYYY-MM-DD
---

# Adversarial Scenario: [SYSTEM] vs [ADVERSARY TYPE]

Use this template when **designing systems that must survive scrutiny**. Maps directly to how you think about audits, platforms, and institutions.

---

## System Being Tested

**System:** [Name/description of the system under test]

**Purpose:** [What the system is meant to do]

**Current defenses:** [Existing protections]

---

## Adversary Type

**Adversary:** [Who/what is attacking]

**Motivation:** [Why they would attack]

**Capabilities:**

- [Capability 1]
- [Capability 2]
- [Capability 3]

**Constraints:** [What limits them]

---

## Attack Vector

**Primary attack method:**

[How the adversary would attempt to compromise/exploit the system]

**Entry point:** [Where the attack begins]

**Attack sequence:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Likely Exploit

**Vulnerability exploited:**

[The specific weakness being targeted]

**Why it works:**

[What makes this vulnerability exploitable]

**Probability of success:** High / Medium / Low

---

## System Response

**Current response:**

[How the system would currently respond to this attack]

**Detection capability:**

- [ ] Would detect before damage
- [ ] Would detect during attack
- [ ] Would detect after damage
- [ ] Would not detect

**Response time:** [How long before response activates]

---

## Failure Outcome

**If attack succeeds:**

[What happens to the system/data/users]

**Blast radius:**

- [Impact area 1]
- [Impact area 2]
- [Impact area 3]

**Recovery difficulty:** Easy / Moderate / Hard / Impossible

---

## Hardening Required

**Immediate fixes:**

| Fix | Effort | Impact |
|-----|--------|--------|
| [Fix 1] | Low/Med/High | [What it prevents] |
| [Fix 2] | Low/Med/High | [What it prevents] |
| [Fix 3] | Low/Med/High | [What it prevents] |

**Architectural changes:**

- [Change 1] — [Why needed]
- [Change 2] — [Why needed]

---

## Residual Risk

**After hardening, what remains:**

[Risks that cannot be fully eliminated]

**Acceptable because:**

[Why remaining risk is tolerable]

**Monitoring required:**

- [What to watch for 1]
- [What to watch for 2]

---

## Related Scenarios

- [Scenario name] — [Different adversary or vector]
- [Scenario name] — [Escalation of this scenario]
