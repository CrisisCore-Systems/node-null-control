# Pass/Fail Gates Template

Document: Collapse-Ready Sprint — Pass/Fail Gates

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

## 1. Gate Overview

Pass/fail gates represent binary assessment criteria. Each gate either passes or fails based on objective evidence.

### 1.1 Gate Summary

| Gate ID | Gate Name | Result | Evidence |
| --- | --- | --- | --- |
| G-001 | | ⬜ PASS / ⬜ FAIL | |
| G-002 | | ⬜ PASS / ⬜ FAIL | |
| G-003 | | ⬜ PASS / ⬜ FAIL | |
| G-004 | | ⬜ PASS / ⬜ FAIL | |
| G-005 | | ⬜ PASS / ⬜ FAIL | |

### 1.2 Overall Result

| Metric | Value |
| --- | --- |
| Total Gates | |
| Passed | |
| Failed | |
| Pass Rate | % |

---

## 2. Authentication Gates

### G-AUTH-001: Password Policy Enforcement

| Attribute | Value |
| --- | --- |
| **Requirement** | Password policy meets minimum standards (12+ chars, complexity) |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-AUTH-002: Multi-Factor Authentication

| Attribute | Value |
| --- | --- |
| **Requirement** | MFA available and enforced for privileged accounts |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-AUTH-003: Session Management

| Attribute | Value |
| --- | --- |
| **Requirement** | Sessions expire appropriately, secure tokens |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 3. Authorization Gates

### G-AUTHZ-001: Principle of Least Privilege

| Attribute | Value |
| --- | --- |
| **Requirement** | Access controls follow least privilege |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-AUTHZ-002: Role-Based Access Control

| Attribute | Value |
| --- | --- |
| **Requirement** | RBAC implemented and documented |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 4. Data Protection Gates

### G-DATA-001: Encryption at Rest

| Attribute | Value |
| --- | --- |
| **Requirement** | Sensitive data encrypted at rest |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-DATA-002: Encryption in Transit

| Attribute | Value |
| --- | --- |
| **Requirement** | TLS 1.2+ for all external communications |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-DATA-003: Key Management

| Attribute | Value |
| --- | --- |
| **Requirement** | Encryption keys properly managed and rotated |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 5. Infrastructure Gates

### G-INFRA-001: Patch Management

| Attribute | Value |
| --- | --- |
| **Requirement** | Critical patches applied within SLA |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-INFRA-002: Network Segmentation

| Attribute | Value |
| --- | --- |
| **Requirement** | Critical systems segmented appropriately |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-INFRA-003: Backup and Recovery

| Attribute | Value |
| --- | --- |
| **Requirement** | Backups exist, tested, and recoverable |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 6. Logging and Monitoring Gates

### G-LOG-001: Audit Logging

| Attribute | Value |
| --- | --- |
| **Requirement** | Security-relevant events logged |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

### G-LOG-002: Log Retention

| Attribute | Value |
| --- | --- |
| **Requirement** | Logs retained per compliance requirements |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 7. Compliance Gates

### G-COMP-001: Regulatory Requirements

| Attribute | Value |
| --- | --- |
| **Requirement** | Applicable regulations identified and addressed |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 8. Custom Gates

_Add engagement-specific gates as needed._

### G-CUSTOM-001: {{gate_name}}

| Attribute | Value |
| --- | --- |
| **Requirement** | |
| **Result** | ⬜ PASS / ⬜ FAIL |
| **Evidence** | |
| **Notes** | |

---

## 9. Gate Failure Remediation

| Gate | Failure Reason | Remediation | Priority |
| --- | --- | --- | --- |
| | | | |

---

## 10. Assumptions and Limitations

- Gates assessed based on available evidence
- Point-in-time assessment
- Client responsible for ongoing compliance
- {{additional_assumptions}}

---

## Document History

| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| v01 | {{sprint_start_date}} | System | Initial creation |

---

_This document is part of the Collapse-Ready Sprint delivery package._
