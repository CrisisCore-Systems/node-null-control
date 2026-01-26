# Content Template Pack v01

Asset: `NNASSET-0006-content-template-pack`

Production-ready template system:

- PDF template pack (what buyers get)
- Digital asset bundle (includes source files)

Principles:

- Templates are stable, versioned structures.
- Templates focus on structure, not manipulation.
- No identity dependence required.
- Templates follow proven patterns without exploitation.

Hard rule (no manipulation):

- Templates must not encourage manipulative content.
- Structure-focused, not exploitation-focused.
- Educational guidance only, not psychological manipulation.

Outputs policy (repo hygiene):

- Template source files are committed.
- Generated outputs (filled templates) are not committed.
- The repo keeps: templates, schemas, documentation, and examples.

---

## Folder structure

```text
products/
  content_template_pack/
    README.md
    templates/
      hook_templates/
        hook_h1_question.md
        hook_h2_statement.md
        hook_h3_contrast.md
        hook_h4_curiosity.md
      structure_templates/
        structure_short_form.md
        structure_educational.md
        structure_narrative.md
      script_templates/
        script_20s.md
        script_30s.md
        script_60s.md
      caption_templates/
        caption_minimal.md
        caption_story.md
        caption_cta_free.md
      template_variables.md
      usage_guide.md
    runs/
      YYYY-Www/
        inputs/
        outputs/
        run.json
    licenses/
      LICENSE_commercial_v01.txt
      LICENSE_personal_v01.txt
      LICENSE_team_v01.txt
```

---

## Template categories

### Hook templates

Proven opening structures:

| Template | Type | Use case |
| --- | --- | --- |
| H1 Question | Curiosity | Open with engaging question |
| H2 Statement | Authority | Open with strong claim |
| H3 Contrast | Tension | Open with unexpected contrast |
| H4 Curiosity | Mystery | Open with incomplete information |

### Structure templates

Content organization patterns:

| Template | Format | Duration |
| --- | --- | --- |
| Short Form | Hook → Insight → Loop | 20-35s |
| Educational | Problem → Explanation → Takeaway | 30-60s |
| Narrative | Setup → Tension → Resolution (open) | 30-60s |

### Script templates

Duration-specific frameworks:

| Template | Duration | Sections |
| --- | --- | --- |
| 20s Script | 15-25s | Hook (2s) + Core (15s) + Loop (3s) |
| 30s Script | 25-35s | Hook (3s) + Build (20s) + Open (7s) |
| 60s Script | 50-70s | Hook (5s) + Develop (45s) + Close (10s) |

### Caption templates

Platform-appropriate text formats:

| Template | Style | Purpose |
| --- | --- | --- |
| Minimal | Brief | Algorithmic-friendly |
| Story | Extended | Context-heavy |
| CTA-Free | Clean | No engagement bait |

---

## Template philosophy

### What templates provide:
- Structural frameworks
- Timing guidelines
- Section breakdowns
- Format specifications

### What templates do NOT provide:
- Manipulation tactics
- Psychological tricks
- Engagement bait phrases
- Dark pattern suggestions

---

## Governance

- Templates must not encourage manipulative content.
- No exploitation strategies embedded.
- Structure-focused, educational purpose.
- No identity dependence.
- Users responsible for ethical content.

See [monetization/assets/validation.md](../../monetization/assets/validation.md) for the activation gate.

---

## Monetization telemetry (minimal)

When you sell the template pack, log exactly one `product_event` row:

```yaml
timestamp: 2026-01-26T00:00:00Z
conversion_type: purchase
product_id: NNASSET-0006-content-template-pack
version: v01
confidence_score: 0.5
```

This belongs to product telemetry (not content analytics inputs).
