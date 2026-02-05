# Displacement Risk Atlas - Build Instructions

## Overview

The Displacement Risk Atlas is a professionally designed PDF analyzing 10 sectors approaching automation displacement thresholds.

**Status:** ✅ Built v1.1 (2026-W06) - Designed Artifact with HTML/CSS Rendering

## Prerequisites

```bash
# Install dependencies
pip install -e .

# Install Playwright browsers (required for PDF generation)
playwright install chromium
```

## Quick Build

```bash
# From repository root
python3 scripts/build_displacement_atlas.py \
  --run-json products/displacement_risk_atlas/runs/2026-W06/run.json
```

## Generated Files

The build generates 5 files in `products/displacement_risk_atlas/runs/2026-W06/outputs/`:

1. **displacement_risk_atlas_v1.0.pdf** (~69 KB)
   - Full designed PDF with all content
   - All 10 sectors analyzed
   - Professional clinical dossier aesthetic
   - Ready for Gumroad distribution

2. **displacement_risk_atlas_preview.pdf** (~44 KB)
   - 3-page preview version
   - Cover + framework excerpt + sample sector + CTA
   - Designed for conversion
   - For landing page download

3. **displacement_risk_atlas_full.html** (~24 KB)
   - Full HTML source for PDF
   - Can be customized for different themes

4. **displacement_risk_atlas_preview.html** (~8 KB)
   - Preview HTML source
   - Separate flow optimized for sales

5. **manifest.json** (~2 KB)
   - Build metadata
   - SHA256 hashes for all outputs
   - Input/output tracking
   - Tamper-evident

## Architecture

### Data Layer
- `data/sectors.json` - Externalized sector data (10 sectors)
- `data/DATA_ASSUMPTIONS.md` - Methodology and limitations documentation

### Presentation Layer
- `templates/atlas.html` - Jinja2 template for full PDF
- `templates/preview.html` - Jinja2 template for preview PDF
- `assets/theme.css` - Clinical dossier visual design system

### Build Layer
- `scripts/build_displacement_atlas.py` - Main builder (v1.1)
- Uses Jinja2 for templating
- Uses Playwright Chromium for HTML-to-PDF rendering
- Deterministic builds with SHA256 verification

## Content Structure

### Part 1: Framework (5 pages)
- Leverage Destruction Mechanism
- Bargaining Power Threshold Model
- Cascading Displacement Pattern
- Mitigation Framework Overview

### Part 2: Sector Analysis (10 pages)

Each sector includes:
- Current automation penetration (%)
- Threshold proximity score (0-10)
- Task commoditization indicators
- Adjacent market pressure points
- Timeline estimates (procedural)

**Sectors:**
1. AI/ML Engineering (Junior) - 35% penetration, 7.5/10 proximity
2. Legal Research - 40% penetration, 7.8/10 proximity
3. Medical Diagnostics (Radiology) - 30% penetration, 6.5/10 proximity
4. Financial Analysis - 45% penetration, 7.2/10 proximity
5. Content Production (Media) - 38% penetration, 6.8/10 proximity
6. Customer Service (Enterprise) - 55% penetration, 8.1/10 proximity
7. Data Entry/Processing - 60% penetration, 8.5/10 proximity
8. Junior Software Development - 32% penetration, 7.0/10 proximity
9. Graphic Design (Template-Based) - 42% penetration, 7.3/10 proximity
10. Administrative Coordination - 48% penetration, 7.6/10 proximity

### Part 3: Mitigation Patterns (3 pages)
- Pattern Category 1: Leverage Preservation
- Pattern Category 2: Non-Commoditizable Skills
- Pattern Category 3: Market Position Shifting
- Pattern Category 4: Portfolio Approaches

### Page 20: About & Contact
- CrisisCore Systems information
- Field notes subscription
- Contact details
- License information

## Governance Compliance

All content follows strict governance rules:

✅ No career advice claims  
✅ No financial advice  
✅ No guaranteed outcomes  
✅ Procedural framing only  
✅ Pattern documentation, not prescription  
✅ Clear disclaimers throughout

### Forbidden Phrases (not used)
- "You should..."
- "This will protect you..."
- "Follow this plan..."
- "Guaranteed safety..."

### Allowed Framing (used)
- "This sector shows..."
- "The mechanism operates as..."
- "Observable patterns include..."
- "Mitigation approaches include..."

## Distribution

### Gumroad Setup
1. Upload `displacement_risk_atlas_v1.0.pdf`
2. Set pricing:
   - Personal use: $19
   - Commercial use: $99
3. Add product description from `GUMROAD_DESCRIPTION.md`
4. Configure licenses (see `licenses/` directory)

### Landing Page
1. Upload preview PDF to landing page assets
2. Link from forge/index.html email capture section
3. Include in Email 5 of welcome sequence

## Verification & Testing

### Automated Tests

Run the test suite to verify the build:

```bash
# Run all build verification tests
python3 tests/test_displacement_atlas_build.py
```

Tests verify:
- ✅ All expected files generated
- ✅ Preview PDF has 3 pages
- ✅ Full PDF has reasonable page count
- ✅ PDFs have proper file sizes (not suspiciously small)
- ✅ Manifest contains SHA256 hashes
- ✅ run.json updated with build status
- ✅ All 10 sectors present in HTML/PDF
- ✅ Sector data loaded from JSON

### Manual Verification

```bash
# Check file types
file products/displacement_risk_atlas/runs/2026-W06/outputs/*.pdf

# View HTML output (before PDF conversion)
cat products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_full.html

# Verify hashes
cat products/displacement_risk_atlas/runs/2026-W06/outputs/manifest.json | jq '.outputs'

# Check page counts
python3 -c "from scripts.product_build_utils import count_pdf_pages; from pathlib import Path; print(count_pdf_pages(Path('products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_v1.0.pdf')))"
```

## Rebuilding

The build is deterministic and can be run multiple times:

```bash
# Rebuild (will overwrite existing files)
python3 scripts/build_displacement_atlas.py \
  --run-json products/displacement_risk_atlas/runs/2026-W06/run.json

# Build with custom output directory
python3 scripts/build_displacement_atlas.py \
  --run-json products/displacement_risk_atlas/runs/2026-W06/run.json \
  --out-dir /tmp/atlas-build
```

## Customization

### Updating Sector Data

Edit `products/displacement_risk_atlas/data/sectors.json`:

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

Then rebuild. No code changes needed.

### Customizing Visual Design

Edit `products/displacement_risk_atlas/assets/theme.css`:

- **Typography:** Modify font sizes, families, line-height
- **Colors:** Change accent colors, backgrounds
- **Layout:** Adjust margins, padding, grid
- **Page breaks:** Control where content splits across pages

Three pre-defined aesthetics (choose in CSS):
1. **Clinical Dossier** (current) - Minimal, high-legibility, regulator-ready
2. **Artifact Zine** - Texture, glitch marks, ritual feel
3. **Hybrid** - Clinical grid + subtle artifact overlays

### Customizing Templates

Edit HTML templates:
- `templates/atlas.html` - Full PDF structure
- `templates/preview.html` - Preview PDF structure

Uses Jinja2 syntax:
```html
{% for sector in sectors %}
  <div class="sector-page">
    <h2>{{ sector.name }}</h2>
    ...
  </div>
{% endfor %}
```

### Testing Custom Changes

```bash
# 1. Make changes to CSS/HTML/data
# 2. Rebuild
python3 scripts/build_displacement_atlas.py \
  --run-json products/displacement_risk_atlas/runs/2026-W06/run.json

# 3. Run tests
python3 tests/test_displacement_atlas_build.py

# 4. Check HTML output first (faster iteration)
open products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_full.html
```

## Next Steps

1. **Test download flow**
   - Upload to Gumroad (test mode)
   - Test purchase → download
   - Verify PDF opens correctly

2. **Add to landing page**
   - Upload preview PDF
   - Update forge/index.html links
   - Test email capture → preview download

3. **Email sequence integration**
   - Verify Email 5 links work
   - Test purchase tracking
   - Monitor conversion metrics

4. **Monitor and iterate**
   - Track sales via Gumroad
   - Collect feedback
   - Plan v1.1 updates if needed

## Troubleshooting

### Build fails with "Missing dependency 'playwright'"

```bash
# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Build fails with "Sectors data file not found"

Check that `products/displacement_risk_atlas/data/sectors.json` exists.

### Build fails with "Failed to render template"

- Check Jinja2 syntax in HTML templates
- Verify all template variables are provided in context
- Check for typos in template names

### PDFs look wrong or fonts missing

- Verify CSS file is being loaded correctly
- Check browser console for errors (HTML opens in Chromium)
- Ensure `wait_for_fonts` is enabled in `write_html_to_pdf`

### Page count is different than expected

This is normal. The HTML/CSS layout determines actual page count.
The important thing is:
- All content is present (test with `test_html_contains_all_sectors`)
- PDFs are not suspiciously small (<50KB for full)
- Preview is ~3 pages

### Hashes don't match on rebuild

Check for:
- Timestamps in PDF metadata (should use fixed timestamps)
- Random elements in templates
- Changed input data

The build should be deterministic if inputs don't change.

## Version History

- **v1.1 (2026-W06)**: Designed artifact with HTML/CSS rendering
  - Added Jinja2 templates + Playwright HTML-to-PDF
  - Externalized sector data to JSON
  - Added Clinical Dossier visual design system
  - Added data assumptions documentation
  - Improved PDF file sizes (68KB vs 13.9KB)
  - Added comprehensive build tests
  - Maintained deterministic builds with SHA256 verification

- **v1.0 (2026-W06)**: Initial release
  - 10 sectors analyzed
  - Framework documented
  - Mitigation patterns included
  - Preview version created
  - Basic text PDF generation

## Support

For questions about the build process:
- See `scripts/product_build_utils.py` for common utilities
- Review `tests/test_displacement_atlas_build.py` for examples
- Check `products/displacement_risk_atlas/README.md` for product specs
- See `data/DATA_ASSUMPTIONS.md` for methodology
