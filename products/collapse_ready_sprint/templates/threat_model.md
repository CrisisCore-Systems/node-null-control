# Threat Model Template

Document: Collapse-Ready Sprint — Threat Model

Version: v01

---

## Document Metadata

| Field | Value |
| --- | --- |
| Client | `{{client_name}}` |
| Engagement Token | `{{intake_token}}` |
| Sprint Start Date | `{{sprint_start_date}}` |
| Target Delivery Date | `{{delivery_date}}` |

---

## 1. System Overview

### 1.1 System Description

_Brief description of the system under audit._

```
{{system_description}}
```

### 1.2 System Boundaries

_What is in scope and out of scope._

**In Scope:**
- {{in_scope_items}}

**Out of Scope:**
- {{out_of_scope_items}}

### 1.3 Assets

_Critical assets that need protection._

| Asset | Type | Criticality |
| --- | --- | --- |
| | | |

---

## 2. Threat Actors

### 2.1 Actor Categories

| Actor | Motivation | Capability | Likelihood |
| --- | --- | --- | --- |
| External Attacker | Financial gain, disruption | Medium-High | Medium |
| Malicious Insider | Data theft, sabotage | High (access) | Low |
| Automated Systems | Credential stuffing, scraping | High (volume) | High |
| Nation State | Espionage, disruption | Very High | Low |

### 2.2 Prioritized Actors

_Based on system context, prioritize threat actors._

1. 
2. 
3. 

---

## 3. Attack Surface Analysis

### 3.1 Entry Points

| Entry Point | Type | Exposure |
| --- | --- | --- |
| | | |

### 3.2 Trust Boundaries

_Where trust levels change in the system._

```
{{trust_boundary_diagram}}
```

---

## 4. Threat Scenarios

### 4.1 STRIDE Analysis

| Component | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

### 4.2 Prioritized Threats

| ID | Threat | Impact | Likelihood | Risk Score |
| --- | --- | --- | --- | --- |
| T-001 | | | | |
| T-002 | | | | |
| T-003 | | | | |

---

## 5. Existing Controls

| Control | Threat Mitigated | Effectiveness |
| --- | --- | --- |
| | | |

---

## 6. Recommendations

_High-level recommendations. Detailed findings in Findings Register._

| Priority | Recommendation | Effort | Impact |
| --- | --- | --- | --- |
| P1 | | | |
| P2 | | | |
| P3 | | | |

---

## 7. Assumptions and Limitations

### 7.1 Assumptions

- {{assumptions}}

### 7.2 Limitations

- This assessment is point-in-time
- Based on information provided
- Does not constitute penetration testing
- {{additional_limitations}}

---

## Document History

| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| v01 | {{sprint_start_date}} | System | Initial creation |

---

_This document is part of the Collapse-Ready Sprint delivery package._
