# Intake Form Specification

Document: Collapse-Ready Sprint — Tally.so Intake Form Specification

Version: v01

---

## Form Overview

| Attribute | Value |
| --- | --- |
| Platform | Tally.so |
| Purpose | Client intake validation |
| Deadline | 48 hours from payment |
| Prefilled Fields | Email, Token, Purchase ID |

---

## Prefilled Fields (via Make)

These fields are auto-populated from Stripe checkout:

| Field | Source | Example |
| --- | --- | --- |
| `email` | Stripe session | client@example.com |
| `intake_token` | Make-generated UUID | 550e8400-e29b-41d4-a716-446655440000 |
| `purchase_id` | Stripe payment ID | pi_3ABC123xyz |

---

## Form Sections

### Section 1: Engagement Confirmation

**Header:** Collapse-Ready Sprint — Intake Form

**Subtext:** Complete this form within 48 hours to begin your sprint. Missing or incomplete information may delay or cancel your engagement.

---

### Section 2: Contact Information

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| Full Name | Text | Yes | Min 2 chars |
| Email | Email (prefilled) | Yes | Valid email |
| Organization | Text | No | - |
| Role/Title | Text | No | - |

---

### Section 3: System Information

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| System Name | Text | Yes | Min 3 chars |
| System Description | Long Text | Yes | Min 50 chars |
| System URL(s) | Text | No | - |
| Tech Stack | Long Text | Yes | Min 20 chars |

**Help Text:** Describe the system we will assess. Include primary technologies, frameworks, and hosting environment.

---

### Section 4: Access Information

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| Documentation Access | Radio | Yes | See options |
| Repository Access | Radio | Yes | See options |
| System Access | Radio | Yes | See options |
| Third-Party Services | Long Text | Yes | Min 10 chars |

**Documentation Access Options:**
- Google Drive link (preferred)
- Confluence/Notion link
- Will email separately
- No documentation available

**Repository Access Options:**
- GitHub/GitLab read-only access
- Will provide separately
- Not applicable
- Cannot provide

**System Access Options:**
- Read-only dashboard access
- API documentation only
- Staging environment
- Production logs only
- Not applicable

**Third-Party Services Help Text:** List all third-party services, APIs, and integrations used by the system.

---

### Section 5: Scope Definition

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| Primary Concerns | Checkboxes | Yes | Min 1 |
| Success Criteria | Long Text | Yes | Min 30 chars |
| Known Exclusions | Long Text | No | - |

**Primary Concerns Options:**
- [ ] Authentication & Authorization
- [ ] Data Protection & Privacy
- [ ] Infrastructure Security
- [ ] API Security
- [ ] Third-Party Risk
- [ ] Compliance Requirements
- [ ] Incident Response Readiness
- [ ] Other (specify below)

**Success Criteria Help Text:** What must be true for this engagement to be successful? Be specific about expected outcomes.

---

### Section 6: Compliance Context

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| Regulatory Requirements | Checkboxes | No | - |
| Previous Assessments | Radio | Yes | - |
| Outstanding Issues | Long Text | No | - |

**Regulatory Requirements Options:**
- [ ] GDPR
- [ ] CCPA
- [ ] HIPAA
- [ ] PCI-DSS
- [ ] SOC 2
- [ ] ISO 27001
- [ ] None / Unknown
- [ ] Other

**Previous Assessments Options:**
- Yes, within last 12 months
- Yes, more than 12 months ago
- No previous assessments
- Unknown

---

### Section 7: Constraints Acknowledgment

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| Async Communication | Checkbox | Yes | Must be checked |
| Fixed Scope | Checkbox | Yes | Must be checked |
| No Refunds Post-Start | Checkbox | Yes | Must be checked |
| Written Deliverables Only | Checkbox | Yes | Must be checked |

**Checkbox Text:**

- [ ] I understand communication is async-only (no calls unless purchased separately)
- [ ] I understand scope is fixed once the sprint starts
- [ ] I understand refunds are not available after the sprint starts (workspace created)
- [ ] I understand deliverables are written documents only

---

### Section 8: Hidden Fields

| Field | Type | Source |
| --- | --- | --- |
| intake_token | Hidden | Prefilled from URL |
| purchase_id | Hidden | Prefilled from URL |
| submission_timestamp | Hidden | Auto-captured |

---

## Validation Rules (Make Scenario 2)

### Required for Acceptance

| Check | Requirement |
| --- | --- |
| Access present | At least one access method provided |
| Third-party services listed | Field not empty |
| Success criteria defined | Min 30 chars |
| Constraints acknowledged | All 4 checkboxes checked |

### Rejection Triggers

Intake is rejected if:

- Any required field is empty
- Any constraint checkbox is unchecked
- System description < 50 chars
- Tech stack < 20 chars
- Success criteria < 30 chars

---

## Email Triggers

### On Valid Submission

→ Proceed to Scenario 3 (Workspace Creation)

### On Invalid Submission

→ Trigger Scenario 2A (Intake Incomplete email)

Email includes:
- List of missing/invalid fields
- 72-hour deadline to complete
- Link to edit submission

---

## Form Completion Flow

```
Payment Complete
     ↓
Intake Link Sent (48h deadline)
     ↓
Form Opened
     ↓
Prefilled Fields Loaded
     ↓
Client Completes Form
     ↓
Submit
     ↓
Validation (Make)
     ↓
    ├─→ Valid → Scenario 3 (Sprint Start)
    └─→ Invalid → Scenario 2A (Incomplete Email)
```

---

## Notes

- Form should be mobile-responsive
- Progress indicator recommended
- Save progress feature if Tally supports
- Clear error messages for validation failures
