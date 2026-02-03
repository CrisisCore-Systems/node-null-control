# Displacement Risk Atlas - Data Directory

## Overview

This directory contains externalized data for the Displacement Risk Atlas product. Separating data from code allows for easy updates without touching the build system.

## Files

### `sectors.json`

Contains all sector analysis data used in the PDF generation.

**Structure:**
```json
{
  "sectors": [
    {
      "name": "Sector Name",
      "penetration": "XX",
      "proximity": "X.X",
      "routine_tasks": [...],
      "adjacent_markets": [...],
      "near_term": "...",
      "mid_term": "..."
    }
  ]
}
```

**Field Descriptions:**

- **name** (string): Sector name, used as heading in PDF
- **penetration** (string): Current automation penetration percentage (0-100)
- **proximity** (string): Proximity score to leverage collapse threshold (0-10 scale)
- **routine_tasks** (array of strings): List of tasks being commoditized by automation
  - Format: "Task description (HIGH/MEDIUM/LOW automation)"
- **adjacent_markets** (array of strings): Markets where displaced workers might seek employment
  - Format: "Market name (HIGH/MEDIUM/LOW saturation risk)"
- **near_term** (string): 0-2 year timeline observation
- **mid_term** (string): 2-5 year timeline observation

**Updating Sectors:**

1. Edit `sectors.json` directly
2. Rebuild the PDF: `python3 scripts/build_displacement_atlas.py --run-json products/displacement_risk_atlas/runs/2026-W06/run.json`
3. No code changes needed

**Adding New Sectors:**

Add a new object to the `sectors` array following the structure above. The build system will automatically include it in the generated PDF.

### `DATA_ASSUMPTIONS.md`

Documents the methodology, data sources, and limitations of the proximity scores and penetration estimates.

**Purpose:**
- Explains what the numbers mean
- Documents data sources and update policy
- Clarifies what the data IS and IS NOT
- Provides disclaimers

**Updating:**
- Review quarterly or when methodology changes
- Update data sources section when new sources are added
- Maintain version history at bottom

## Data Quality Guidelines

### Penetration Percentages
- Should be whole numbers (no decimals)
- Range: 0-100
- Based on observable automation tool adoption and capability
- Documented in DATA_ASSUMPTIONS.md

### Proximity Scores
- Should have one decimal place (e.g., "7.5")
- Range: 0.0-10.0
- Higher scores indicate closer to leverage collapse
- Relative comparison tool, not absolute prediction

### Task Lists
- Use present tense
- Include automation level in parentheses
- Keep descriptions concise (one line)
- Focus on routine vs. judgment distinction

### Market Lists
- Name adjacent/substitute markets
- Include saturation risk level
- Consider both displacement and demand sides

### Timeline Estimates
- Use procedural language ("observed", "reported", "likely")
- Avoid prediction language ("will", "guaranteed")
- Include context (regulation, economics, technology)
- Maintain governance compliance

## Governance Compliance

All data and framing must follow governance rules:

✅ **Allowed:**
- "X% of tasks can be automated"
- "Proximity score of Y/10"
- "Observable patterns include..."
- "Timeline estimate (procedural, not predictive)"

❌ **Forbidden:**
- "You should avoid this sector"
- "This will protect you"
- "Guaranteed safe/unsafe"
- Any prescriptive career advice

## Version Control

When updating sector data:
1. Document the change in git commit message
2. Update `DATA_ASSUMPTIONS.md` if methodology changes
3. Increment version in `run.json` if releasing new PDF
4. Rebuild and test before distribution

## Testing Data Changes

```bash
# After editing sectors.json
python3 tests/test_displacement_atlas_build.py

# Check specific validations
python3 -c "
from pathlib import Path
from scripts.product_build_utils import read_json

data = read_json(Path('products/displacement_risk_atlas/data/sectors.json'))
print(f'Sectors: {len(data[\"sectors\"])}')
for s in data['sectors']:
    print(f'  {s[\"name\"]}: {s[\"penetration\"]}% penetration, {s[\"proximity\"]}/10 proximity')
"
```

## Support

Questions about data format or methodology:
- See `DATA_ASSUMPTIONS.md` for methodology
- See `BUILD.md` for build instructions
- Contact: support@crisiscore.systems
