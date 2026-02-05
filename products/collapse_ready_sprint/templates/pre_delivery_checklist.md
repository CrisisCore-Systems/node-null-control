# Pre-Delivery Quality Checklist

Document: Collapse-Ready Sprint — Pre-Delivery Quality Gates

Version: v01

---

## Purpose

This checklist ensures deliverables meet quality standards before release.

**Use case:** Run this checklist before triggering Scenario 5 (Delivery Package Generation).

**Who runs it:** Operator (internal only — client never sees this)

---

## Hostile-Auditor Review Standard

Review each artifact as if a hostile auditor will challenge every statement.

Questions to ask:

1. Can every claim be traced to evidence?
2. Are assumptions explicitly documented?
3. Are limitations clearly stated?
4. Could a determined adversary find an undocumented gap?
5. Would this hold up under legal scrutiny?

---

## Pre-Delivery Checklist

### Section A — Completeness

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] Threat Model complete | | |
| [ ] Data Flow Map complete | | |
| [ ] Findings Register complete | | |
| [ ] Pass/Fail Gates evaluated | | |
| [ ] Executive Summary complete | | |
| [ ] Scope Lock document finalized | | |

**All documents must be complete before delivery.**

---

### Section B — Consistency

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] Client name consistent across all documents | | |
| [ ] Dates consistent (sprint start, delivery) | | |
| [ ] System name consistent | | |
| [ ] Scope matches scope lock document | | |
| [ ] Findings IDs sequential and complete | | |
| [ ] Cross-references valid (no broken links) | | |

---

### Section C — Evidence Quality

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] Each finding has evidence | | |
| [ ] Evidence is specific (not vague assertions) | | |
| [ ] Severity ratings justified | | |
| [ ] Recommendations are actionable | | |
| [ ] Residual risks documented | | |

---

### Section D — Hostile-Auditor Questions

For each major finding, answer:

| Finding ID | Claim Traceable? | Assumptions Stated? | Limitations Documented? |
| --- | --- | --- | --- |
| F-001 | | | |
| F-002 | | | |
| F-003 | | | |

**If ANY finding fails hostile-auditor review → fix before delivery.**

---

### Section E — Pass/Fail Gate Integrity

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] All gates evaluated (no gaps) | | |
| [ ] Pass/fail determinations are binary | | |
| [ ] Evidence supports each determination | | |
| [ ] Blocking vs non-blocking classification complete | | |
| [ ] Overall pass rate calculated correctly | | |

---

### Section F — Executive Summary Quality

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] Key findings match Findings Register | | |
| [ ] Risk summary accurate | | |
| [ ] Recommendations prioritized | | |
| [ ] Residual risks acknowledged | | |
| [ ] Evaluation Notice present | | |
| [ ] Signature block present | | |

---

### Section G — Scope Boundary Enforcement

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] No scope creep (all work within scope lock) | | |
| [ ] Out-of-scope items documented (not addressed) | | |
| [ ] Assumptions documented in each artifact | | |
| [ ] Limitations stated explicitly | | |

---

### Section H — Defensive Documentation

| Check | Pass | Notes |
| --- | --- | --- |
| [ ] Disagreement containment language present | | |
| [ ] "Point-in-time" limitation stated | | |
| [ ] "Information provided" caveat present | | |
| [ ] No guarantees of completeness | | |
| [ ] Evaluation Notice in Executive Summary | | |

---

## Final Approval

| Approver | Date | Signature |
| --- | --- | --- |
| | | |

**Checklist Status:**

- [ ] All checks PASS — proceed to delivery
- [ ] One or more checks FAIL — fix before delivery

---

## Automation Integration

### Scenario 5 Pre-Condition

Before generating delivery package:

1. Verify this checklist exists in client folder
2. Verify all checkboxes are checked (if using Notion)
3. If checklist incomplete → block delivery generation

### Notion Integration (Optional)

Create database: `CRS Pre-Delivery Checks`

| Field | Type |
| --- | --- |
| Client | Relation (CRS Clients) |
| Checklist Status | Select: Incomplete, Complete |
| Section A | Checkbox |
| Section B | Checkbox |
| Section C | Checkbox |
| Section D | Checkbox |
| Section E | Checkbox |
| Section F | Checkbox |
| Section G | Checkbox |
| Section H | Checkbox |
| Final Approval | Date |
| Approver Notes | Text |

### Make Module Addition

In Scenario 5, add Module 0.5:

```
Module: Notion → Search database
Database: CRS Pre-Delivery Checks
Filter: Client = {{client_id}} AND Checklist Status = "Complete"
```

If no match → abort delivery, send alert.

---

## Why This Matters

- **Prevents embarrassing errors:** Catches gaps before client sees them
- **Reduces rework:** Fix issues before delivery, not after
- **Defensible process:** Shows due diligence if challenged
- **Quality signal:** Consistent, thorough deliverables build reputation
- **Hostile-auditor ready:** Every claim can withstand scrutiny
