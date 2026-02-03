# Displacement Risk Atlas - GitHub Issues to Create

This document contains the GitHub issues that should be created to track implementation of the Displacement Risk Atlas product across all components.

---

## Issue 1: Upload Displacement Risk Atlas to Gumroad

**Title:** Upload Displacement Risk Atlas v1.0 to Gumroad

**Labels:** `product`, `distribution`, `displacement-atlas`

**Description:**

Upload the Displacement Risk Atlas v1.0 PDF to Gumroad for distribution.

### Tasks
- [ ] Create Gumroad product listing
- [ ] Upload full PDF: `products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_v1.0.pdf`
- [ ] Configure pricing tiers:
  - Personal use: $19
  - Commercial use: $99
- [ ] Add product description from `products/displacement_risk_atlas/GUMROAD_DESCRIPTION.md`
- [ ] Upload license files from `products/displacement_risk_atlas/licenses/`
- [ ] Configure delivery settings (immediate download)
- [ ] Set up 30-day refund policy
- [ ] Test purchase flow
- [ ] Verify PDF delivery works correctly

### Resources
- Product description: `products/displacement_risk_atlas/GUMROAD_DESCRIPTION.md`
- Build documentation: `products/displacement_risk_atlas/BUILD.md`
- License files: `products/displacement_risk_atlas/licenses/`

---

## Issue 2: Set Up Email Sequence in ConvertKit/Beehiiv

**Title:** Configure Displacement Atlas email sequence (5 emails over 8 days)

**Labels:** `email`, `automation`, `displacement-atlas`

**Description:**

Set up the 5-email welcome sequence for Displacement Risk Atlas in ConvertKit or Beehiiv.

### Tasks
- [ ] Choose email platform (ConvertKit or Beehiiv free tier)
- [ ] Create email sequence "displacement-atlas-sequence"
- [ ] Write Email 1: Welcome + Framework (Day 0)
- [ ] Write Email 2: AI Displacement (Day 2)
- [ ] Write Email 3: Legal/Medical (Day 4)
- [ ] Write Email 4: Cascading Pattern (Day 6)
- [ ] Write Email 5: Product Offer (Day 8)
- [ ] Configure automation trigger from landing page signup
- [ ] Add tag "displacement-atlas-sequence" to new subscribers
- [ ] Schedule emails at 10:00 AM recipient timezone
- [ ] Set up post-purchase tagging ("atlas-buyer")
- [ ] Configure post-sequence flow (weekly field notes)
- [ ] Test complete sequence with test email
- [ ] Verify links work in all emails

### Resources
- Email sequence copy: `forge/email_sequences/displacement_atlas_welcome.md`
- Landing page form: `forge/index.html` (id="email-signup")

### Governance Compliance
- ✅ No urgency/scarcity tactics
- ✅ No guaranteed outcomes
- ✅ No advice claims
- ✅ Clear disclaimers
- ✅ Procedural framing only
- ✅ 30-day refund guarantee
- ✅ Unsubscribe in every email

---

## Issue 3: Deploy Landing Page Updates

**Title:** Deploy forge/index.html updates for Displacement Atlas

**Labels:** `landing-page`, `deployment`, `displacement-atlas`

**Description:**

Deploy the updated landing page with Displacement Risk Atlas email capture section.

### Tasks
- [ ] Review HTML changes in `forge/index.html`
- [ ] Test email capture form locally
- [ ] Verify email signup integration with backend
- [ ] Configure `EMAIL_SIGNUP_URL` in `forge/config.js`
- [ ] Set up email API key (ConvertKit/Beehiiv)
- [ ] Test form submission end-to-end
- [ ] Verify UTM parameter tracking
- [ ] Deploy to production
- [ ] Test live form submission
- [ ] Monitor initial signups

### Resources
- Landing page: `forge/index.html`
- App logic: `forge/app.js`
- Config: `forge/config.js`

---

## Issue 4: Create and Test Preview PDF Download Flow

**Title:** Set up preview PDF download for Displacement Atlas

**Labels:** `landing-page`, `assets`, `displacement-atlas`

**Description:**

Set up the free 3-page preview PDF download flow on the landing page.

### Tasks
- [ ] Upload preview PDF to hosting (Vercel, S3, or similar)
- [ ] Add download link to Email 1 of sequence
- [ ] Create thank-you page or auto-download
- [ ] Test download flow
- [ ] Verify PDF opens correctly in browsers
- [ ] Monitor download metrics

### Resources
- Preview PDF: `products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_preview.pdf`
- Email sequence: `forge/email_sequences/displacement_atlas_welcome.md`

---

## Issue 5: Test Build and Verify Product Quality

**Title:** Run full build verification for Displacement Atlas v1.0

**Labels:** `build`, `quality`, `displacement-atlas`

**Description:**

Run comprehensive build verification and quality checks for the Displacement Risk Atlas.

### Tasks
- [ ] Run build script: `python3 scripts/build_displacement_atlas.py --run-json products/displacement_risk_atlas/runs/2026-W06/run.json`
- [ ] Verify all outputs generated correctly:
  - Full PDF (13.9 KB)
  - Preview PDF (3.7 KB)
  - Markdown version (8.2 KB)
  - Manifest.json (1.7 KB)
- [ ] Check PDF formatting and readability
- [ ] Verify all 20 pages render correctly
- [ ] Review content for governance compliance
- [ ] Scan for forbidden phrases (using `scripts/scan_forbidden_phrases.py`)
- [ ] Verify no advice claims
- [ ] Verify procedural framing only
- [ ] Check all disclaimers present
- [ ] Test PDF on multiple devices/readers
- [ ] Verify manifest hashes match files

### Resources
- Build script: `scripts/build_displacement_atlas.py`
- Build docs: `products/displacement_risk_atlas/BUILD.md`
- Governance checklist in run.json

---

## Issue 6: Set Up Analytics and Tracking

**Title:** Configure analytics for Displacement Atlas launch

**Labels:** `analytics`, `monitoring`, `displacement-atlas`

**Description:**

Set up tracking and analytics for the Displacement Atlas launch to measure success.

### Tasks
- [ ] Set up UTM parameters for traffic sources
- [ ] Configure Gumroad sales tracking
- [ ] Set up email open/click tracking
- [ ] Monitor conversion metrics:
  - Landing page visitors
  - Email signups
  - Email sequence opens (target >40% for Email 1, >30% for Email 5)
  - Email 5 clicks (target >5%)
  - Conversions (target >1%)
- [ ] Create dashboard for key metrics
- [ ] Set up alerts for anomalies

### Target Metrics (First 90 days)
- Phase 1: 100+ email signups
- Phase 2: 1-3 sales (1%+ conversion)
- Phase 3: $200-400/month revenue

### Resources
- Product README: `products/displacement_risk_atlas/README.md`
- Email sequence metrics: `forge/email_sequences/displacement_atlas_welcome.md`

---

## Issue 7: Document Distribution and Support Process

**Title:** Create distribution and customer support documentation

**Labels:** `documentation`, `support`, `displacement-atlas`

**Description:**

Document the processes for product distribution and customer support.

### Tasks
- [ ] Document Gumroad configuration
- [ ] Create customer support FAQ
- [ ] Document refund process (30-day guarantee)
- [ ] Create license verification process
- [ ] Document commercial license upgrade process
- [ ] Create troubleshooting guide
- [ ] Set up support email monitoring
- [ ] Create response templates for common questions

### Resources
- FAQ section in: `products/displacement_risk_atlas/PUBLIC.md`
- Support email: support@crisiscore.systems

---

## Implementation Order

**Recommended sequence:**

1. **Issue 5** (Build verification) - Verify product quality first
2. **Issue 1** (Gumroad upload) - Make product available
3. **Issue 4** (Preview PDF) - Set up free preview
4. **Issue 3** (Landing page) - Deploy signup page
5. **Issue 2** (Email sequence) - Configure automation
6. **Issue 6** (Analytics) - Start tracking metrics
7. **Issue 7** (Documentation) - Support infrastructure

---

## Notes

- All tasks follow governance constraints (no advice claims, procedural framing only)
- 30-day refund policy on all purchases
- No urgency/scarcity tactics
- Clear disclaimers in all marketing materials
- Email sequence designed for 1-2% conversion rate
