# Collapse-Ready Sprint

Asset: `NNASSET-0010-collapse-ready-sprint`

14-day fixed-scope audit and hardening engagement.

Delivers: threat model, data flow maps, findings register, pass/fail gates, hardening recommendations, executive summary.

Principles:

- Pre-purchase eligibility gate (filter bad fits before payment)
- Async-only engagement (no calls unless purchased separately)
- Fixed scope (no scope creep)
- Written deliverables only
- Conditional refunds (pre-sprint only)
- Time-box enforcement (client delays do not extend timeline)
- Fully automated client lifecycle

Hard boundaries:

- Governance: [docs/01_rules.md](../../docs/01_rules.md)
- Workflow: [docs/02_workflow.md](../../docs/02_workflow.md)
- Monetization: [monetization/architecture.md](../../monetization/architecture.md)
- Automation: [automation/service_wiring.md](../../automation/service_wiring.md)

---

## ⚠️ This Is Not Compliance Certification

**Important:** This engagement does not certify compliance, security, or legal sufficiency.

It produces artifacts suitable for evaluation by those authorities.

Specifically, this engagement:

- Does NOT certify SOC 2, ISO 27001, HIPAA, or any regulatory compliance
- Does NOT guarantee security or absence of vulnerabilities
- Does NOT provide legal advice or legal sufficiency determination
- Does NOT replace penetration testing or red team exercises

It DOES provide:

- Structured security assessment artifacts
- Documented findings and recommendations
- Pass/fail gate evaluations
- Data flow and threat analysis

Use these artifacts to support your compliance and security programs, not to replace them.

---

## Pre-Purchase Eligibility Gate

**Before payment, prospects must pass an eligibility check.**

This filters out:

- Systems not ready for assessment
- Prospects who cannot provide access
- Prospects who need calls or ongoing support
- Prospects who need faster than 14 days
- Prospects who need compliance certification
- Slow-response organizations (3+ days turnaround)

**Flow:**

```
Sales page → Eligibility form → [Qualified] → Stripe checkout
                              → [Disqualified] → Polite rejection + resources
```

See [templates/eligibility_gate_spec.md](templates/eligibility_gate_spec.md) for full specification.

**This is the single highest-ROI control surface.** It reduces refunds, reduces emotional labor, and filters misaligned prospects before money moves.

---

## Stack (Locked)

| Component | Tool | Purpose |
| --- | --- | --- |
| Docs | Google Docs | Artifact creation |
| Storage | Google Drive | Delivery + archive |
| Payments | Stripe | Checkout + refunds |
| Automation | Make (Integromat) | Workflow orchestration |
| Forms | Tally.so | Intake + receipt confirmation |
| Internal Tracking | Notion | Status + task management |
| Email | Gmail (via Make) | Client communication |

Optional upgrade: n8n (self-hosted) for sovereignty.

---

## Why This Stack

- Lowest friction
- Fastest to ship
- Excellent async + artifact handling
- No DevOps overhead
- Easy to reason about under stress
- Fully auditable (timestamps, access logs, receipts)

Matches the procedural survivability principle.

---

## Global Engagement Rules (System-Enforced)

These rules are enforced by the automation, not manually:

| Rule | Description |
| --- | --- |
| Pre-purchase eligibility | Bad fits filtered before payment |
| Async-only | No synchronous communication unless purchased |
| Fixed scope | Scope locked at intake acceptance |
| Written deliverables only | No verbal commitments |
| Conditional refunds only | Refunds only pre-sprint start |
| No scope creep | Changes require new engagement |
| No "quick calls" | Call add-on required for meetings |
| Time-box enforcement | Client delays do not extend timeline |

The automation is the bouncer.

---

## Time-Box Enforcement

**Rule:** Client delays do not extend sprint timelines unless explicitly agreed in writing.

| Day | Trigger | Action |
| --- | --- | --- |
| Day 5 | Access not granted | Warning email (72h) |
| Day 8 | Still no access | Final warning (48h) |
| Day 14 | Sprint deadline | Auto-close, partial delivery |

If client delays cause incomplete assessment:

- Partial findings delivered with scope limitations documented
- "INCOMPLETE - CLIENT DELAY" noted in deliverables
- No refund (sprint started, work performed)

This prevents "we slowed you down" reversals.

---

## Disagreement Containment

**Disagreement does not invalidate delivery.**

All findings represent bounded analysis under stated assumptions. If client disagrees with conclusions:

- Alternate conclusions require alternate assumptions
- Alternate assumptions must be documented separately
- Provider is not obligated to revise conclusions based on disagreement alone
- Delivery is complete upon receipt confirmation, regardless of agreement

This protects against:

- Endless rebuttal cycles
- Defensive back-and-forth
- "Can you revise this conclusion?" pressure

See [licenses/LICENSE_engagement_v01.txt](licenses/LICENSE_engagement_v01.txt) for full terms.

---

## Conditional Refund Policy

Refunds allowed only if:

- Intake is rejected due to missing / incompatible inputs
- Client cannot provide required access
- Scope mismatch discovered before work begins

No refunds once sprint starts.

Sprint start defined as: workspace + documents created.

See [refund_policy.md](templates/refund_policy.md) for full policy text.

---

## Folder Structure

```text
products/
  collapse_ready_sprint/
    README.md
    templates/
      eligibility_gate_spec.md    # Pre-purchase qualification
      threat_model.md
      data_flow_map.md
      findings_register.md
      pass_fail_gates.md
      executive_summary.md
      scope_lock.md
      intake_form_spec.md
      refund_policy.md
      email_templates.md
      drive_structure.md
    runs/
      YYYY-Www/
        inputs/
        outputs/
        run.json
    licenses/
      LICENSE_engagement_v01.txt
```

---

## Automation Scenarios

End-to-end workflow broken into Make scenarios.

See [../../automation/service_wiring.md](../../automation/service_wiring.md) for full scenario blueprints.

### Scenario 0 — Pre-Purchase Eligibility Gate (Critical)

Trigger: `Tally → Eligibility Form Submitted`

Actions:
1. Validate eligibility responses against disqualification criteria
2. If qualified: Generate Stripe checkout link, send "You're Eligible" email
3. If disqualified: Send "Not a Fit" email with resources
4. Log lead in Notion (Qualified/Disqualified)

See [templates/eligibility_gate_spec.md](templates/eligibility_gate_spec.md) for full specification.

### Scenario 1 — Payment → Intake Gate

Trigger: `Stripe → checkout.session.completed`

Actions:
1. Retrieve session (email, product, call add-on, payment ID)
2. Generate intake token (UUID)
3. Create unique Tally intake link (prefilled)
4. Send "Sprint Intake Required" email (48h deadline)
5. Create Notion client record (status: Pending)

### Scenario 2 — Intake Submission → Validation

Trigger: `Tally → Form Submitted`

Actions:
1. Validate required fields
2. Route to Scenario 2A (invalid) or Scenario 3 (valid)

### Scenario 2A — Intake Failed

Actions:
1. Send "Intake Incomplete" email (72h deadline)
2. Update Notion status (Incomplete)
3. If deadline expires: optional partial refund, close record

### Scenario 3 — Workspace Creation (Sprint Start)

⚠️ This moment locks refunds.

Actions:
1. Create Google Drive client folder
2. Copy document templates
3. Auto-populate client data
4. Generate scope lock document
5. Send "Sprint Activated" email
6. Update Notion status (Active)

### Scenario 4 — Internal Execution Support

No client touch. Internal only.

Actions:
1. Auto-create Notion tasks
2. Send deadline reminders (day 10)

### Scenario 5 — Delivery Package Generation

Trigger: `Notion → Sprint = Ready to Deliver`

Actions:
1. Export PDFs from Google Docs
2. Generate README.md (artifact list, scope, residual risks)
3. ZIP package
4. Upload to /Delivery/ folder
5. Generate view-only link

### Scenario 6 — Delivery & Closure

Actions:
1. Send delivery email
2. Send receipt confirmation form (Tally)
3. On submission: close Notion record, archive permissions

---

## Optional Enhancements

### Artifact Integrity (Recommended)

- Generate SHA256 hashes of delivery PDFs
- Include hashes in README
- Demonstrates seriousness and auditability

### Future Upgrades

- Swap Google Docs → Markdown + Git
- Self-host n8n when revenue justifies
- Add anonymized case-study request (30 days post-close)
- Add "pre-audit" upsell path

---

## What You Do Not Have to Do

The system handles:

- Chasing clients
- Scheduling calls
- Re-explaining scope
- Justifying credentials
- Managing files manually
- Arguing about refunds
- Defending boundaries verbally

---

## Governance

- Engagement must not encourage manipulative behavior
- No deceptive claims about outcomes
- Fixed scope, fixed deliverables
- Auditability required (timestamps, logs, receipts)
- No identity dependence

See [monetization/architecture.md](../../monetization/architecture.md) for surface governance.

---

## Monetization Telemetry (Minimal)

When a sprint completes, log exactly one `product_event` row:

```yaml
timestamp: 2026-02-02T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0010-collapse-ready-sprint
version: v01
confidence_score: 0.8
```

This belongs to product telemetry (not content analytics inputs).
