# Data Flow Map Template

Document: Collapse-Ready Sprint — Data Flow Map

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

## 1. Data Inventory

### 1.1 Data Categories

| Category | Description | Sensitivity | Regulatory |
| --- | --- | --- | --- |
| PII | Personally identifiable information | High | GDPR, CCPA |
| Financial | Payment, banking data | Critical | PCI-DSS |
| Credentials | Passwords, tokens, keys | Critical | N/A |
| Business | Proprietary information | Medium-High | NDA |
| Public | Publicly available data | Low | N/A |

### 1.2 Data Assets Identified

| Asset ID | Name | Category | Location | Owner |
| --- | --- | --- | --- | --- |
| D-001 | | | | |
| D-002 | | | | |
| D-003 | | | | |

---

## 2. Data Flow Diagram

### 2.1 Level 0 — Context Diagram

```
{{context_diagram}}

External Entity ──→ [System] ──→ External Entity
                      │
                      ↓
                  Data Store
```

### 2.2 Level 1 — System Decomposition

```
{{level1_diagram}}

┌─────────────────────────────────────────────────────────────┐
│                         System                               │
│                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Process  │ ───→ │ Process  │ ───→ │ Process  │          │
│  │    A     │      │    B     │      │    C     │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│       │                 │                 │                 │
│       ↓                 ↓                 ↓                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │  Store   │      │  Store   │      │  Store   │          │
│  │    1     │      │    2     │      │    3     │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flows

### 3.1 Flow Inventory

| Flow ID | Source | Destination | Data Type | Protocol | Encryption |
| --- | --- | --- | --- | --- | --- |
| F-001 | | | | | |
| F-002 | | | | | |
| F-003 | | | | | |

### 3.2 Trust Boundary Crossings

| Flow ID | Boundary Crossed | Risk Level | Controls |
| --- | --- | --- | --- |
| | | | |

---

## 4. Data at Rest

### 4.1 Storage Locations

| Store ID | Type | Data Stored | Encryption | Backup |
| --- | --- | --- | --- | --- |
| S-001 | | | | |
| S-002 | | | | |

### 4.2 Retention Policies

| Data Category | Retention Period | Deletion Method | Compliance |
| --- | --- | --- | --- |
| | | | |

---

## 5. Data in Transit

### 5.1 Encryption Standards

| Protocol | Version | Key Size | Certificate |
| --- | --- | --- | --- |
| TLS | | | |
| | | | |

### 5.2 Internal vs External

| Flow Type | Encryption Required | Current State |
| --- | --- | --- |
| External (internet) | Yes | |
| Internal (LAN) | Recommended | |
| Internal (localhost) | Optional | |

---

## 6. Third-Party Data Sharing

### 6.1 External Parties

| Party | Data Shared | Purpose | Agreement |
| --- | --- | --- | --- |
| | | | |

### 6.2 Data Processing Agreements

| Party | DPA Status | Last Review |
| --- | --- | --- |
| | | |

---

## 7. Findings Summary

_Detailed findings in Findings Register._

| Finding ID | Description | Risk | Recommendation |
| --- | --- | --- | --- |
| | | | |

---

## 8. Assumptions and Limitations

- Data flow mapping based on documentation and interviews
- May not capture all implicit or undocumented flows
- Point-in-time assessment
- {{additional_assumptions}}

---

## Document History

| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| v01 | {{sprint_start_date}} | System | Initial creation |

---

_This document is part of the Collapse-Ready Sprint delivery package._
