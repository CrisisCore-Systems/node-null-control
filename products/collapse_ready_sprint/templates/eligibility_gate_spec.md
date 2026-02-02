# Eligibility Gate Specification

Document: Collapse-Ready Sprint — Pre-Purchase Eligibility Gate

Version: v01

---

## Purpose

Filter unqualified prospects **before** payment to:

- Reduce refunds
- Reduce emotional labor
- Increase perceived seriousness
- Filter "credential-seekers" and vibe buyers

This is the single highest-ROI control surface.

---

## Form Overview

| Attribute | Value |
| --- | --- |
| Platform | Tally.so |
| Purpose | Pre-purchase qualification |
| Outcome | Stripe checkout link OR polite rejection |
| No payment at this stage | True |

---

## Form Flow

```
Prospect lands on sales page
       ↓
"Check Eligibility" button
       ↓
Eligibility Gate form (Tally)
       ↓
Make.com validates responses (Scenario 0)
       ↓
    ├─→ Eligible → Generate Stripe checkout link → Email
    └─→ Not Eligible → Polite rejection email + resources
```

---

## Form Copy (Production-Ready)

**Title:** Collapse-Ready Sprint — Eligibility Check

**Subheading:** This engagement is artifact-based, async-only, and fixed-scope. Please confirm fit before proceeding.

### Form Setup (Tally.so)

| Setting | Value |
| --- | --- |
| Platform | Tally.so |
| Form URL | `https://tally.so/r/[your-form-id]` |
| Webhook | Enable webhook integration → Make |
| Webhook URL | `https://hook.make.com/[your-webhook-id]` |

**Field ID Convention:**

In Tally, field IDs are auto-generated but can be customized. Use these exact IDs in the webhook payload:

1. Go to Form Settings → Integrations → Webhooks
2. Enable "Include field IDs in webhook"
3. Test webhook to verify field names match specification

**Validation Rules (set in Tally):**

| Field | Tally Validation |
| --- | --- |
| email | Required, Email format |
| access_control | Required, Single select |
| communication_model | Required, Single select |
| scope_acknowledgement | Required, Checkbox (must be checked) |
| credential_requirement | Required, Single select |
| failure_definition | Required, Min 10 characters |
| final_acknowledgement | Required, Checkbox (must be checked) |

---

## Form Sections

### Section A — System Reality

**1. What are you asking to be reviewed?**

| Option | Eligible |
| --- | --- |
| ☐ Software handling sensitive data | ✅ |
| ☐ Evidence / documentation system under dispute or audit | ✅ |
| ☐ Other (describe) | ✅ |

**2. Do you control access to the system?**

| Option | Eligible |
| --- | --- |
| ☐ Yes (repo / configs / docs) | ✅ |
| ☐ Partial | ✅ |
| ☐ No | ❌ AUTO-DISQUALIFY |

**3. Primary risk you're trying to reduce (select up to 2):**

| Option | Eligible |
| --- | --- |
| ☐ Privacy / data exposure | ✅ |
| ☐ Legal or regulatory scrutiny | ✅ |
| ☐ Procedural failure (lost evidence, ambiguity) | ✅ |
| ☐ Release risk / regressions | ✅ |

---

### Section B — Engagement Constraints (Hard)

**4. Communication model**

| Option | Eligible |
| --- | --- |
| ☐ Async-only by default | ✅ REQUIRED |
| ☐ Written deliverables only | ✅ REQUIRED |
| Any other selection | ❌ AUTO-DISQUALIFY |

**5. Scope model**

| Option | Eligible |
| --- | --- |
| ☐ Fixed scope, no creep | ✅ REQUIRED |
| ☐ I accept that assumptions and out-of-scope items will be documented, not negotiated | ✅ REQUIRED |

**6. Evaluation standard**

| Option | Eligible |
| --- | --- |
| ☐ I will evaluate outputs by inspection/testing, not credentials | ✅ REQUIRED |
| ☐ I understand this is not a compliance certification | ✅ REQUIRED |

---

### Section C — Authority & Intent

**7. What would make this a failure for you?** (short answer; required)

_Free text field — captures client expectations for review_

**8. Do you require credentials, titles, or certifications as a condition of acceptance?**

| Option | Eligible |
| --- | --- |
| ☐ No | ✅ |
| ☐ Yes | ❌ AUTO-DISQUALIFY |

---

### Final Acknowledgement (Required)

**9. I acknowledge:**

- Async-only engagement
- Fixed scope
- Artifact-based evaluation
- Conditional refunds (pre-sprint only)
- No authority claims or certifications

| Option | Eligible |
| --- | --- |
| ☐ I agree | ✅ REQUIRED |
| Unchecked | ❌ AUTO-DISQUALIFY |

---

## Eligibility Logic (Make Router)

**Eligible IF ALL TRUE:**

| Condition | Check |
| --- | --- |
| Access control | ≠ "No" |
| Communication model | = "Async-only by default" AND "Written deliverables only" |
| Scope acknowledged | Both scope checkboxes checked |
| Evaluation standard | Both evaluation checkboxes checked |
| Credentials requirement | = "No" |
| Final acknowledgement | Checked |

**Else: REJECT**

### Automatic Disqualification (Hard No)

Reject immediately if ANY of these:

| Condition | Field | Value |
| --- | --- | --- |
| No system access control | Q2 | "No" |
| Requires synchronous communication | Q4 | Missing either checkbox |
| Requires credentials | Q8 | "Yes" |
| Final acknowledgement missing | Q9 | Unchecked |

### Warning Flags (Proceed with Caution)

Flag but allow if:

| Condition | Action |
| --- | --- |
| Partial system access | Note in lead record |
| "Other" system type | Review description before checkout |

---

## Make Scenario: CRS_00_Eligibility_Gate

**Scenario Name:** `CRS_00_Eligibility_Gate`

**Purpose:** Block bad fits before Stripe checkout exists.

---

### MODULE 1 — Trigger: Tally Form Submitted

| Setting | Value |
| --- | --- |
| App | Tally |
| Event | New form response |
| Form | Collapse-Ready Sprint — Eligibility Check |

**Fields to expose:**

| Field ID | Type | Description | How to Find in Tally |
| --- | --- | --- | --- |
| `system_type` | Multi-select | What is being reviewed | Question 1 response |
| `access_control` | Single-select | Yes / Partial / No | Question 2 response |
| `communication_model` | Single-select | Async-only by default / Other | Question 4 response |
| `scope_acknowledgement` | Checkbox | Fixed scope acceptance | Question 5 response |
| `credential_requirement` | Single-select | Yes / No | Question 8 response |
| `failure_definition` | Text | What would make this a failure | Question 7 response |
| `final_acknowledgement` | Checkbox | Final agreement | Question 9 response |
| `email` | Email | Contact email | Respondent email field |

**⚠️ Field ID Verification:**

1. Create a test submission in Tally
2. Check Make webhook history for received payload
3. Map actual field names from payload to variables above
4. If field names differ, update Make scenario to use actual names
5. Field names in Tally follow pattern: `question_[uuid]` or custom labels

---

### MODULE 2 — Normalize Inputs (Set Variables)

| Setting | Value |
| --- | --- |
| App | Make → Tools → Set variables |

**Create variables:**

| Variable | Logic |
| --- | --- |
| `has_access` | `access_control != "No"` |
| `async_only` | `communication_model = "Async-only by default"` |
| `scope_ok` | `scope_acknowledgement = true` |
| `no_credentials_required` | `credential_requirement = "No"` |
| `acknowledged` | `final_acknowledgement = true` |

---

### MODULE 3 — Router: Eligibility Decision

| Setting | Value |
| --- | --- |
| App | Make → Router |

**ROUTE A — ELIGIBLE**

Condition (ALL must be true):

```
has_access = true
AND async_only = true
AND scope_ok = true
AND no_credentials_required = true
AND acknowledged = true
```

**ROUTE B — REJECTED**

Fallback route (no conditions — catches all failures)

---

## ROUTE A — ELIGIBLE PATH

### MODULE 4A — Generate Checkout Token

| Setting | Value |
| --- | --- |
| App | Make → Tools → Generate UUID |
| Output | `checkout_token` |

**Critical:** This token becomes the single source of truth tying:
- Eligibility
- Payment
- Intake
- Sprint workspace

---

### MODULE 5A — Create Stripe Checkout Session

| Setting | Value |
| --- | --- |
| App | Stripe |
| Action | Create a Checkout Session |

**Configuration:**

| Parameter | Value |
| --- | --- |
| Mode | `payment` |
| Line Item 1 | Product: Collapse-Ready Systems Hardening™, Price: $25,000 |
| Success URL | `https://yourdomain.com/success?token={{checkout_token}}` |
| Cancel URL | `https://yourdomain.com/cancel` |

**Optional Call Add-On:**

The Single Call (60 min, $5,000) is displayed as an optional upsell on the Stripe Checkout page itself, not selected in the eligibility form. Configure in Stripe:

1. Create product "Single Call (60 min)" in Stripe Dashboard
2. In Checkout Session creation, use `line_items` array with:
   - Main product: `adjustable_quantity: false`
   - Call add-on: `adjustable_quantity: { enabled: true, minimum: 0, maximum: 1 }`

This lets the buyer add the call during checkout without adding form complexity.

**Metadata (critical for downstream scenarios):**

| Key | Value |
| --- | --- |
| `eligibility_token` | `{{checkout_token}}` |
| `source` | `eligibility_gate` |

---

### MODULE 6A — Create Lead Record (Notion)

| Setting | Value |
| --- | --- |
| App | Notion |
| Action | Create database item |
| Database | CRS Leads |

**Fields:**

| Notion Field | Value |
| --- | --- |
| Email | `{{email}}` |
| Status | `Eligible / Awaiting Payment` |
| Eligibility Token | `{{checkout_token}}` |
| Credential Required | `No` |
| Access Level | `{{access_control}}` |
| Created At | `{{now()}}` |

This provides auditability for downstream scenarios.

---

### MODULE 7A — Send "Eligible" Email

| Setting | Value |
| --- | --- |
| App | Gmail |
| Action | Send email |

**Subject:**

```
Eligible — Proceed to Collapse-Ready Sprint Checkout
```

**Body (paste verbatim):**

```
You're eligible to proceed.

This engagement is:
• Async-only
• Fixed-scope
• Evaluated by inspectable artifacts, not credentials

Checkout link (valid for 48 hours):
{{Stripe Checkout URL}}

Once payment is complete, you'll receive the intake form.

No calls. No scope negotiation. Written deliverables only.
```

---

## ROUTE B — REJECTED PATH

### MODULE 4B — Create Rejection Record (Notion)

| Setting | Value |
| --- | --- |
| App | Notion |
| Action | Create database item |
| Database | CRS Leads |

**Fields:**

| Notion Field | Value |
| --- | --- |
| Email | `{{email}}` |
| Status | `Declined (Eligibility)` |
| Rejection Reason | See diagnostic codes below |
| Access Level | `{{access_control}}` |
| Created At | `{{now()}}` |

**Diagnostic Rejection Reasons (set in Module 2):**

Build the rejection reason dynamically based on which condition(s) failed:

```
rejection_reason = 
  IF(has_access = false, "NO_ACCESS; ", "") +
  IF(async_only = false, "NEEDS_SYNC; ", "") +
  IF(scope_ok = false, "SCOPE_NOT_ACKNOWLEDGED; ", "") +
  IF(no_credentials_required = false, "NEEDS_CREDENTIALS; ", "") +
  IF(acknowledged = false, "NO_FINAL_ACK; ", "")
```

| Code | Meaning |
| --- | --- |
| `NO_ACCESS` | Selected "No" for access control |
| `NEEDS_SYNC` | Did not select async-only communication |
| `SCOPE_NOT_ACKNOWLEDGED` | Did not check scope acknowledgement |
| `NEEDS_CREDENTIALS` | Selected "Yes" for credential requirement |
| `NO_FINAL_ACK` | Did not check final acknowledgement |

This enables post-hoc analysis of why prospects are being disqualified.

---

### MODULE 5B — Send Rejection Email

| Setting | Value |
| --- | --- |
| App | Gmail |
| Action | Send email |

**Subject:**

```
Engagement Declined — Not a Fit
```

**Body (paste verbatim):**

```
Thanks for completing the eligibility check.

Based on your responses, this engagement isn't a fit.

The Collapse-Ready Sprint is:
• Async-only
• Fixed-scope
• Evaluated by inspectable artifacts, not credentials

If you require authority signaling, certification, or ongoing support, a traditional firm will serve you better.

This decision is a scope boundary, not a judgment.
```

**Note:** No reply-to. No follow-ups. No apology. No debate hook.

---

## Integration with Existing Flow

### Required Change to Scenario 1 (Payment → Intake Gate)

**Before (old flow):**

```
Stripe payment → Intake
```

**After (new flow):**

```
Eligibility → Stripe → Intake
```

### Enforcement Rule

In Scenario 1, **before generating intake link**, add validation:

1. Confirm `eligibility_token` exists in Stripe metadata
2. Confirm token matches a Notion record with:
   - Status = `Eligible / Awaiting Payment`
3. If validation fails → **abort scenario**

**Add Module to Scenario 1:**

| Module | App | Action |
| --- | --- | --- |
| New Module 1.5 | Notion | Search database |

**Search criteria:**

```
Eligibility Token = {{Stripe metadata.eligibility_token}}
AND Status = "Eligible / Awaiting Payment"
```

**If no match found:**

- Do NOT generate intake link
- Log error to Notion
- Send alert email to operator

### What This Prevents

- Manual Stripe links (bypassing eligibility)
- "But I already paid" edge cases
- Bad-faith actors sharing checkout URLs

---

## Failure Modes Eliminated

| Failure Mode | How It's Blocked |
| --- | --- |
| Credential debates | Disqualified at eligibility |
| "Can we hop on a call?" | Async-only checkbox required |
| Scope creep pre-payment | Fixed scope acknowledged |
| Refund pressure | Bad fits never pay |
| Bad-faith buyers | Explicit constraints accepted |
| Authority-seeking orgs | Credentials question disqualifies |
| Emotional labor | System handles rejection |

**Your system now selects clients.**

---

## Notion Database Schema: CRS Leads

| Field | Type | Values |
| --- | --- | --- |
| Email | Email | |
| Status | Select | `Eligible / Awaiting Payment`, `Declined (Eligibility)`, `Converted`, `Expired` |
| Eligibility Token | Text (UUID) | |
| Credential Required | Checkbox | |
| Access Level | Select | `Yes`, `Partial`, `No` |
| Rejection Reason | Text | (if declined) |
| Created At | Date | |
| Converted At | Date | (if purchased) |
| Stripe Session ID | Text | (after checkout created) |

---

## Metrics to Track

| Metric | Purpose |
| --- | --- |
| Eligibility form submissions | Volume |
| Qualification rate | % who pass |
| Disqualification reasons | Identify patterns |
| Conversion rate (qualified → purchased) | Effectiveness |
| Refund rate (post-implementation) | Success measure |

---

## Why This Works

- **Reduces refunds:** Bad fits filtered before money moves
- **Reduces emotional labor:** System handles rejection, not you
- **Increases seriousness:** Barrier signals commitment
- **Filters vibe buyers:** Specific questions expose misalignment
- **Protects reputation:** No failed engagements to explain

This is the bouncer before the door.
