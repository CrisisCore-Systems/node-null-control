# Service Automation Wiring

Service delivery automation for fixed-scope engagements.

Extends the core automation wiring: [wiring.md](wiring.md)

Hard boundaries:

- Governance: [docs/01_rules.md](../docs/01_rules.md)
- Workflow: [docs/02_workflow.md](../docs/02_workflow.md)
- Monetization: [monetization/architecture.md](../monetization/architecture.md)
- Product engine: [monetization/product_engine.md](../monetization/product_engine.md)

---

## 0) Service Automation Principles

- **Async-first:** No synchronous communication required
- **System-enforced:** Rules enforced by automation, not humans
- **Auditable:** Every action logged with timestamps
- **Fixed-scope:** No scope creep, no exceptions
- **Conditional refunds:** Pre-start only, system-enforced

The automation is the bouncer.

---

## 1) Stack (Locked)

| Component | Tool | Purpose |
| --- | --- | --- |
| Payments | Stripe | Checkout, refunds, webhooks |
| Automation | Make (Integromat) | Workflow orchestration |
| Forms | Tally.so | Intake, receipt confirmation |
| Docs | Google Docs | Artifact creation |
| Storage | Google Drive | Workspace, delivery |
| Tracking | Notion | Status, tasks |
| Email | Gmail (via Make) | Client communication |

Optional upgrade: n8n (self-hosted) for sovereignty.

---

## 2) Global Engagement Rules

These rules are enforced by the automation system:

| Rule | Enforcement Point |
| --- | --- |
| Async-only | No call scheduling unless add-on purchased |
| Fixed scope | Scope locked at workspace creation |
| Written deliverables only | All outputs are documents |
| Conditional refunds only | Refund API blocked after sprint start |
| No scope creep | No mechanism to add scope mid-sprint |
| No "quick calls" | Call requires separate purchase |

---

## 3) Conditional Refund Policy

### Refunds Allowed If:

- Intake rejected due to missing/incompatible inputs
- Client cannot provide required access
- Scope mismatch discovered before sprint start

### Refunds NOT Allowed If:

- Sprint has started (workspace created)
- Client fails to complete intake
- Client unresponsive after sprint start

### Sprint Start Definition:

Sprint starts when workspace + documents are created. This is the refund lock point.

---

## 4) End-to-End Automation Scenarios

### Scenario 1 — Payment → Intake Gate

**Trigger:** `Stripe → checkout.session.completed`

**Steps:**

1. **Stripe: Retrieve session**
   - Capture: client email, product, call add-on (yes/no), payment ID

2. **Make: Generate intake token**
   - UUID for engagement tracking

3. **Tally: Generate unique intake link**
   - Prefill: email, token, purchase ID

4. **Gmail: Send "Sprint Intake Required" email**
   - Subject: `Collapse-Ready Sprint — Intake Required (48h)`
   - Body: intake link, deadline, refund policy, constraint reminder

5. **Notion: Create client record**
   - Fields: client name, email, Stripe payment ID
   - Intake status: `Pending`
   - Sprint status: `Not Started`

```mermaid
flowchart LR
    Stripe[Stripe Webhook] --> Make[Make Scenario 1]
    Make --> Token[Generate Token]
    Token --> Tally[Generate Intake Link]
    Tally --> Gmail[Send Intake Email]
    Gmail --> Notion[Create Client Record]
```

---

### Scenario 2 — Intake Submission → Validation

**Trigger:** `Tally → Form Submitted`

**Steps:**

1. **Make: Validate required fields**
   - Repo/system access present?
   - Third-party services listed?
   - Success criteria defined?
   - Constraints acknowledged (checkbox)?

2. **Router**
   - If ❌ invalid → Scenario 2A
   - If ✅ valid → Scenario 3

```mermaid
flowchart TD
    Tally[Tally Submission] --> Validate[Validate Fields]
    Validate -->|Invalid| S2A[Scenario 2A]
    Validate -->|Valid| S3[Scenario 3]
```

---

### Scenario 2A — Intake Failed

**Steps:**

1. **Gmail: Send "Intake Incomplete" email**
   - List missing items
   - 72h deadline

2. **Notion: Update intake status**
   - Status: `Incomplete`

3. **If deadline expires (optional):**
   - Stripe: Partial refund
   - Close record
   - End automation

---

### Scenario 3 — Workspace Creation (Sprint Start)

**⚠️ This moment locks refunds**

**Steps:**

1. **Google Drive: Create client folder**
   ```
   /Collapse-Ready-Sprints/
     /Client-<Token>/
       /01-Threat-Model/
       /02-Data-Flows/
       /03-Findings/
       /04-Hardening/
       /05-Executive-Summary/
       /06-Scope-Lock/
       /07-Client-Provided/
       /08-Delivery/
   ```

2. **Google Docs: Copy templates**
   - Threat Model
   - Data Flow Map
   - Findings Register
   - Pass/Fail Gates
   - Executive Summary
   - Scope Lock

3. **Google Docs: Auto-populate**
   - Client name
   - Scope summary
   - Assumptions
   - Dates

4. **Google Docs: Generate scope lock**
   - In scope
   - Out of scope
   - Constraints
   - Success criteria

5. **Gmail: Send "Sprint Activated" email**
   - Confirms sprint start
   - Restates no-refund point
   - Shares delivery date

6. **Notion: Update status**
   - Intake: `Accepted`
   - Sprint: `Active`

```mermaid
flowchart TD
    Valid[Valid Intake] --> Drive[Create Drive Folder]
    Drive --> Templates[Copy Templates]
    Templates --> Populate[Auto-Populate]
    Populate --> Scope[Generate Scope Lock]
    Scope --> Email[Sprint Activated Email]
    Email --> Notion[Update Notion: Active]
```

---

### Scenario 4 — Internal Execution Support

**No client touch. Internal only.**

**Steps (optional, recommended):**

1. **Notion: Auto-create tasks**
   - Threat model
   - Flow enumeration
   - Findings
   - Hardening
   - Summary

2. **Make: Deadline reminder**
   - Ping at day 10 if not marked complete

No client notifications in this scenario.

---

### Scenario 5 — Delivery Package Generation

**Trigger:** Manual toggle in Notion: `Sprint = Ready to Deliver`

**Steps:**

1. **Google Docs → Export PDFs**
   - All artifacts

2. **Make: Generate README.md**
   - Artifact list
   - Scope reminder
   - Residual risks
   - Hash notice (optional)

3. **Make: ZIP package**
   - PDFs + README

4. **Google Drive: Upload to /Delivery/**
   - Generate view-only link

```mermaid
flowchart LR
    Ready[Ready to Deliver] --> Export[Export PDFs]
    Export --> README[Generate README]
    README --> ZIP[Create ZIP]
    ZIP --> Upload[Upload to Delivery]
    Upload --> Link[Generate Share Link]
```

---

### Scenario 6 — Delivery & Closure

**Steps:**

1. **Gmail: Send delivery email**
   - Subject: `Collapse-Ready Sprint — Delivery Package`
   - Includes: secure link, executive summary excerpt
   - Optional: call upsell (if not purchased)

2. **Tally: Send receipt confirmation form**
   - One checkbox: "I confirm receipt of the delivery package."

3. **On submission:**
   - Notion: Sprint = `Closed`
   - Archive folder permissions locked
   - Timestamp logged

```mermaid
flowchart TD
    Delivery[Send Delivery Email] --> Form[Receipt Confirmation Form]
    Form --> Submit[Client Submits]
    Submit --> Close[Close Notion Record]
    Close --> Archive[Lock Permissions]
```

---

## 5) Artifact Integrity (Optional Enhancement)

Generate SHA256 hashes of delivery PDFs and include in README.

**Implementation:**

1. After PDF export, calculate SHA256 hash
2. Store hashes in Make variable
3. Include in README.md generation

**Value:**

- Demonstrates seriousness
- Enables integrity verification
- Professional-grade delivery

---

## 6) Data Flow (End-to-End)

```mermaid
flowchart TD
    Payment[Stripe Payment] --> S1[Scenario 1: Intake Gate]
    S1 --> Intake[Tally Intake Form]
    Intake --> S2[Scenario 2: Validation]
    S2 -->|Invalid| S2A[Scenario 2A: Failed]
    S2 -->|Valid| S3[Scenario 3: Sprint Start]
    S3 --> S4[Scenario 4: Internal Execution]
    S4 --> S5[Scenario 5: Package Generation]
    S5 --> S6[Scenario 6: Delivery & Closure]
    
    S2A -->|Retry| Intake
    S2A -->|Timeout| Refund[Refund & Close]
```

---

## 7) Notion Database Schema

### Client Records Table

| Field | Type | Values |
| --- | --- | --- |
| Client Name | Text | |
| Email | Email | |
| Intake Token | Text (UUID) | |
| Stripe Payment ID | Text | |
| Intake Status | Select | Pending, Incomplete, Accepted, Rejected |
| Sprint Status | Select | Not Started, Active, Ready to Deliver, Closed |
| Sprint Start Date | Date | |
| Delivery Date | Date | |
| Call Add-On | Checkbox | |
| System Name | Text | |
| Drive Folder URL | URL | |
| Delivery Link | URL | |
| Notes | Long Text | |

### Tasks Table (Optional)

| Field | Type | Values |
| --- | --- | --- |
| Task Name | Text | |
| Client | Relation | Client Records |
| Status | Select | To Do, In Progress, Done |
| Due Date | Date | |

---

## 8) Error Handling

### Stripe Webhook Failures

- Retry webhook delivery (Stripe handles)
- Log failed webhooks
- Alert on repeated failures

### Intake Validation Failures

- Send incomplete email
- Set deadline timer
- Auto-close on timeout

### Google API Failures

- Retry with exponential backoff
- Alert on repeated failures
- Do not proceed without workspace confirmation

### Email Delivery Failures

- Retry once
- Log failure
- Manual intervention required

---

## 9) Security Considerations

- No credentials in automation logs
- Stripe webhooks verified via signature
- Google OAuth tokens refreshed automatically
- Notion API key scoped to databases
- Email sent via authenticated Gmail
- All links use HTTPS

---

## 10) Monitoring and Alerts

| Event | Alert Method |
| --- | --- |
| Payment received | Notion record created |
| Intake deadline approaching | Email to operator |
| Intake expired | Notification + auto-action |
| Sprint deadline approaching | Email to operator |
| Delivery ready | Notification |
| Receipt not confirmed (48h) | Reminder sent |

---

## 11) What You Do Not Have to Do

The system handles:

- Chasing clients
- Scheduling calls
- Re-explaining scope
- Justifying credentials
- Managing files manually
- Arguing about refunds
- Defending boundaries verbally

The automation is the bouncer.

---

## 12) Future Upgrades

| Upgrade | When | Benefit |
| --- | --- | --- |
| Markdown + Git | High volume | Version control |
| Self-host n8n | Revenue justifies | Sovereignty |
| Case study request | Post-close | Marketing |
| Pre-audit upsell | Established flow | Revenue |
