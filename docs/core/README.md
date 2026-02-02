# Core Documentation System

Cognitive infrastructure for capturing decision-grade thinking — not notes, not content, but reusable decision patterns.

## Purpose

You are not documenting answers.
You are documenting **how you detect reality under pressure**.

Every artifact must answer at least one of these:

- What pattern was I detecting?
- What failure mode was I trying to avoid?
- What constraint mattered more than others?
- What decision did this make inevitable?

Each entry is a **cognitive primitive**, not prose.

---

## Directory Structure

```
/docs/core/
├── principles/           # Non-negotiable axioms (Principle Codex)
├── constraints/          # Constraint Maps (reality wins)
├── README.md             # This file

/docs/decisions/
└── decision_spines/      # Irreversibility filters

/docs/diagnostics/
└── trees/                # Root-cause extraction

/docs/patterns/
├── patterns/             # Repeatable reality
└── anti_patterns/        # What looks right but is dangerous

/docs/solutions/
└── solution_patterns/    # What actually works

/docs/clients/
└── transformation_maps/  # High-stakes change maps

/docs/adversarial/
└── scenarios/            # Hostile environment tests

/docs/learning/
└── postmortems/          # Learning artifacts
```

---

## Template Index

| Template | Location | Use When |
|----------|----------|----------|
| [Decision Spine](../decisions/TEMPLATE_decision_spine.md) | `/docs/decisions/` | Choosing under uncertainty |
| [Diagnostic Tree](../diagnostics/TEMPLATE_diagnostic_tree.md) | `/docs/diagnostics/` | Something is failing or unclear |
| [Pattern Library Entry](../patterns/TEMPLATE_pattern.md) | `/docs/patterns/patterns/` | Noticing something recurring |
| [Anti-Pattern](../patterns/TEMPLATE_anti_pattern.md) | `/docs/patterns/anti_patterns/` | Something looks right but is dangerous |
| [Solution Pattern](../solutions/TEMPLATE_solution_pattern.md) | `/docs/solutions/` | Proven something survives reality |
| [Constraint Map](./TEMPLATE_constraint_map.md) | `/docs/core/constraints/` | Constraints dominate creativity |
| [Client Transformation Map](../clients/TEMPLATE_transformation_map.md) | `/docs/clients/` | High-stakes client/system change |
| [Adversarial Scenario](../adversarial/TEMPLATE_adversarial_scenario.md) | `/docs/adversarial/` | Systems that must survive scrutiny |
| [Principle Codex Entry](./TEMPLATE_principle.md) | `/docs/core/principles/` | Defining non-negotiable axioms |
| [Post-Mortem](../learning/TEMPLATE_postmortem.md) | `/docs/learning/` | After outcomes (good or bad) |

---

## Metadata Header (Required)

Every file must include this header at the top:

```yaml
---
type: decision_spine | diagnostic_tree | pattern | anti_pattern | solution_pattern | constraint_map | transformation_map | adversarial_scenario | principle | postmortem
domain: security | business | legal | product | operations | platform | content | analytics
confidence: high | medium | low
last_updated: YYYY-MM-DD
---
```

This enables structured reasoning over your knowledge base.

---

## How to Use with LLMs

When using an LLM (like ChatGPT), don't ask:

> "What should I do?"

Instead, ask:

> "Using my Decision Spines + Constraint Maps, evaluate this situation."

Or:

> "Apply my anti-patterns and adversarial scenarios to this plan."

Because your IP is structured, the model can:

- Compare current problems to past patterns
- Detect conflicts between principles
- Flag when you're violating your own rules
- Propose decisions in your voice and logic

---

## Why This Matters

- **You stop re-deriving conclusions** — past thinking is instantly accessible
- **You externalize judgment without losing rigor** — decisions are traceable
- **You preserve scar tissue, not just ideas** — hard-won skepticism is encoded
- **You get consistency under stress** — principles guide when data is incomplete

This is not note-taking. It's **cognitive infrastructure**.
