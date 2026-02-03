# Displacement Risk Atlas - Build Instructions

## Overview

The Displacement Risk Atlas is a 20-page PDF analyzing 10 sectors approaching automation displacement thresholds.

**Status:** ✅ Built v1.0 (2026-W06)

## Quick Build

```bash
# From repository root
python3 scripts/build_displacement_atlas.py \
  --run-json products/displacement_risk_atlas/runs/2026-W06/run.json
```

## Generated Files

The build generates 4 files in `products/displacement_risk_atlas/runs/2026-W06/outputs/`:

1. **displacement_risk_atlas_v1.0.pdf** (13.9 KB)
   - Full 20-page product
   - All 10 sectors analyzed
   - Ready for Gumroad distribution

2. **displacement_risk_atlas_preview.pdf** (3.7 KB)
   - 3-page preview version
   - Cover + framework + sample sector
   - For landing page download

3. **displacement_risk_atlas_v1.0.md** (8.2 KB)
   - Markdown version of full content
   - Documentation/reference

4. **manifest.json** (1.7 KB)
   - Build metadata
   - SHA256 hashes
   - Input/output tracking

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

## Verification

Test the generated PDFs:

```bash
# Check file types
file products/displacement_risk_atlas/runs/2026-W06/outputs/*.pdf

# View content
head -50 products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_v1.0.md

# Verify hashes
cat products/displacement_risk_atlas/runs/2026-W06/outputs/manifest.json | jq '.outputs'
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

### Build fails
- Verify `product_build_utils.py` exists in scripts/
- Check run.json is valid JSON
- Ensure output directory is writable

### PDFs corrupted
- Verify using: `file displacement_risk_atlas_v*.pdf`
- Should show: "PDF document, version 1.4"
- Check file size > 0 bytes

### Content issues
- Edit sector data in `build_displacement_atlas.py`
- Rebuild with updated content
- Verify changes in markdown output first

## Version History

- **v1.0 (2026-W06)**: Initial release
  - 10 sectors analyzed
  - Framework documented
  - Mitigation patterns included
  - Preview version created

## Support

For questions about the build process:
- See `scripts/product_build_utils.py` for common utilities
- Review other product builders in `scripts/` for patterns
- Check `products/displacement_risk_atlas/README.md` for product specs
