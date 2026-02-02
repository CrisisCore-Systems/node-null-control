# Email Templates

Document: Collapse-Ready Sprint — Email Templates

Version: v01

---

## Overview

All emails sent via Gmail through Make automation. Templates use variable substitution for personalization.

---

## Email 1: Sprint Intake Required

**Trigger:** Stripe checkout.session.completed

**Subject:** Collapse-Ready Sprint — Intake Required (48h)

**Body:**

```
Thank you for purchasing the Collapse-Ready Sprint.

To begin your engagement, complete the intake form within 48 hours:

{{intake_link}}

WHAT HAPPENS NEXT

1. Complete the intake form (required information about your system)
2. We validate your submission
3. Your sprint workspace is created (this starts the sprint)
4. You receive a "Sprint Activated" email
5. Delivery in 14 days

IMPORTANT REMINDERS

• This engagement is async-only. No calls unless you purchased the call add-on.
• Scope is fixed once the sprint starts. No changes mid-engagement.
• Refunds are only available before the sprint starts. Once workspace is created, no refunds.
• All deliverables are written documents (PDFs).

REFUND POLICY

Refunds are available if:
- Your intake is rejected due to missing or incompatible inputs
- You cannot provide required access
- Scope mismatch is discovered before sprint start

Once the sprint starts, no refunds are available.

DEADLINE

Complete the intake form within 48 hours of receiving this email.

If you have questions about the intake form, reply to this email.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
Purchase ID: {{purchase_id}}
```

---

## Email 2: Intake Incomplete

**Trigger:** Intake validation failed (Scenario 2A)

**Subject:** Collapse-Ready Sprint — Intake Incomplete (Action Required)

**Body:**

```
Your intake form submission is incomplete.

MISSING OR INVALID FIELDS

{{missing_fields_list}}

NEXT STEPS

Update your submission within 72 hours:

{{intake_edit_link}}

If you cannot complete the required fields, reply to this email to discuss options (refund may be available).

DEADLINE

72 hours from this email.

If the deadline passes without a complete submission, your engagement may be cancelled with a partial refund.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
```

---

## Email 3: Sprint Activated

**Trigger:** Workspace created (Scenario 3)

**Subject:** Collapse-Ready Sprint — Sprint Activated

**Body:**

```
Your Collapse-Ready Sprint has started.

WHAT THIS MEANS

• Your workspace has been created
• Documents are being prepared
• Delivery expected: {{delivery_date}}
• Refunds are no longer available

YOUR SCOPE

System: {{system_name}}

In Scope:
{{in_scope_summary}}

Out of Scope:
{{out_of_scope_summary}}

Success Criteria:
{{success_criteria}}

ENGAGEMENT RULES (REMINDER)

• Async-only communication (no calls unless purchased)
• Fixed scope (no changes)
• Written deliverables only
• Single delivery (no revision cycles)

WHAT TO EXPECT

• Work begins immediately
• You may receive clarifying questions via email
• Respond to questions within 24 hours to avoid delays
• Delivery package will be sent on or before {{delivery_date}}

If you have urgent information to share, reply to this email.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
Sprint Start: {{sprint_start_date}}
Delivery Date: {{delivery_date}}
```

---

## Email 4: Clarifying Question

**Trigger:** Manual (during sprint execution)

**Subject:** Collapse-Ready Sprint — Clarification Needed

**Body:**

```
A clarifying question has come up during your sprint.

QUESTION

{{question_text}}

CONTEXT

{{context_text}}

RESPONSE NEEDED

Please reply to this email within 24 hours.

If we don't receive a response, we will proceed with documented assumptions.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
```

---

## Email 5: Delivery Package

**Trigger:** Scenario 6 (delivery ready)

**Subject:** Collapse-Ready Sprint — Delivery Package

**Body:**

```
Your Collapse-Ready Sprint delivery package is ready.

SECURE DOWNLOAD LINK

{{delivery_link}}

This link provides view-only access to your delivery folder.

PACKAGE CONTENTS

• Executive Summary (PDF)
• Threat Model (PDF)
• Data Flow Map (PDF)
• Findings Register (PDF)
• Pass/Fail Gates (PDF)
• README (artifact list, scope summary, residual risks)

EXECUTIVE SUMMARY EXCERPT

{{executive_summary_excerpt}}

NEXT STEPS

1. Download and review your delivery package
2. Confirm receipt using this form: {{receipt_confirmation_link}}
3. (Optional) Schedule a review call if you purchased the call add-on

QUESTIONS

If you have questions about the findings, reply to this email.

If you purchased the call add-on, you can schedule a review call:
{{call_scheduling_link}}

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
Delivery Date: {{delivery_date}}
```

---

## Email 6: Receipt Confirmation Reminder

**Trigger:** 48 hours after delivery, no confirmation received

**Subject:** Collapse-Ready Sprint — Please Confirm Receipt

**Body:**

```
We sent your delivery package 48 hours ago.

Please confirm receipt:

{{receipt_confirmation_link}}

This helps us close your engagement properly and archive your records.

If you have questions about the delivery, reply to this email.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
```

---

## Email 7: Engagement Closed

**Trigger:** Receipt confirmation submitted

**Subject:** Collapse-Ready Sprint — Engagement Complete

**Body:**

```
Thank you for confirming receipt of your delivery package.

Your Collapse-Ready Sprint engagement is now closed.

SUMMARY

• Sprint Start: {{sprint_start_date}}
• Delivery Date: {{delivery_date}}
• Status: Complete

YOUR FILES

Your delivery folder will remain accessible for 90 days:
{{delivery_link}}

After 90 days, files will be archived.

FEEDBACK

If you have feedback about this engagement, reply to this email.

Thank you for choosing the Collapse-Ready Sprint.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
```

---

## Email 8: Intake Deadline Expiring (Optional)

**Trigger:** 24 hours before intake deadline

**Subject:** Collapse-Ready Sprint — Intake Deadline Tomorrow

**Body:**

```
Your intake form deadline is in 24 hours.

Complete your intake to start your sprint:

{{intake_link}}

If you do not complete the intake form by the deadline:
• Your engagement may be cancelled
• A refund will be processed

If you need more time, reply to this email before the deadline.

---
Collapse-Ready Sprint
Engagement Token: {{intake_token}}
```

---

## Variable Reference

| Variable | Source | Example |
| --- | --- | --- |
| `{{intake_link}}` | Tally + token | https://tally.so/r/xxx?token=uuid |
| `{{intake_token}}` | Make UUID | 550e8400-e29b... |
| `{{purchase_id}}` | Stripe | pi_3ABC123xyz |
| `{{delivery_date}}` | Calculated | 2026-02-16 |
| `{{sprint_start_date}}` | Timestamp | 2026-02-02 |
| `{{system_name}}` | Intake form | Example App |
| `{{delivery_link}}` | Google Drive | https://drive.google.com/... |
| `{{receipt_confirmation_link}}` | Tally | https://tally.so/r/confirm?token=uuid |
| `{{call_scheduling_link}}` | Calendly/Cal.com | https://cal.com/... |
| `{{missing_fields_list}}` | Validation | - System description incomplete |
| `{{executive_summary_excerpt}}` | Generated | "5 findings identified..." |

---

## Email Settings

| Setting | Value |
| --- | --- |
| From Name | Collapse-Ready Sprint |
| Reply-To | Dedicated engagement email |
| Format | Plain text (preferred for deliverability) |
| Tracking | Disabled (privacy) |
