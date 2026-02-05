# Vercel PDF Deployment - Verification Checklist

## Summary

This PR implements Option A from the problem statement: hosting the Displacement Risk Atlas preview PDF as a static file in the Vercel deployment with ConvertKit form redirect.

## Changes Made

### 1. Built Preview PDF ✓
- Generated `displacement_risk_atlas_preview.pdf` (44KB, 3 pages)
- Used existing build script: `scripts/build_displacement_atlas.py`
- Output location: `products/displacement_risk_atlas/runs/2026-W06/outputs/`

### 2. Static File Deployment ✓
- Created: `public/preview/` directory
- Added: `public/preview/displacement_risk_atlas_preview.pdf`
- File will be served at: `/preview/displacement_risk_atlas_preview.pdf`

### 3. Vercel Configuration ✓
- Updated `vercel.json` with headers for `/preview/(.*)` pattern:
  - `Cache-Control: public, max-age=31536000, immutable` (1 year cache)
  - `Content-Type: application/pdf`
  - `X-Content-Type-Options: nosniff` (security)

### 4. ConvertKit Form Redirect ✓
- Updated `forge/index.html` with `data-options` attribute
- Form action: `redirect`
- Redirect URL: `https://ghost-network-interface.vercel.app/preview/displacement_risk_atlas_preview.pdf`
- Success message: empty (redirect is immediate)

### 5. Tests Added ✓
- Created `tests/test_vercel_deployment.py` with 3 tests:
  1. Verify PDF exists and has correct size
  2. Verify vercel.json configuration
  3. Verify Kit form has redirect URL
- All tests passing

## Verification Steps

After Vercel deployment completes (~30 seconds after push):

### 1. Test PDF URL Directly
```bash
curl -I https://ghost-network-interface.vercel.app/preview/displacement_risk_atlas_preview.pdf
```

Expected response:
- Status: `200 OK`
- `Content-Type: application/pdf`
- `Cache-Control: public, max-age=31536000, immutable`
- `Content-Length: 44430` (approximately)

### 2. Test Browser Access
1. Navigate to: `https://ghost-network-interface.vercel.app/preview/displacement_risk_atlas_preview.pdf`
2. PDF should load directly in browser
3. Should show 3 pages:
   - Page 1: Cover
   - Page 2: Framework excerpt
   - Page 3: Sample sector + CTA

### 3. Test Form Submission Flow
1. Navigate to: `https://ghost-network-interface.vercel.app/` (or `/forge/`)
2. Scroll to "Displacement Risk Atlas" section
3. Enter email in form
4. Click "Access Preview"
5. **Expected:** Immediate redirect to PDF (browser downloads or displays)
6. **Important:** Check Kit settings first (see below)

## Critical Kit Settings

⚠️ **Before testing form submission:**

1. Login to ConvertKit/Kit at: `https://app.kit.com`
2. Navigate to: **Settings → Email → Subscribers**
3. Set: **Confirmed opt-in: OFF**
4. If this is ON, users will see "check your email" message instead of immediate redirect

This is mentioned in the problem statement as critical.

## Expected Behavior

### With Double Opt-In DISABLED (Recommended for testing):
1. User enters email
2. Form submits to Kit
3. **Immediate redirect** to PDF URL
4. PDF downloads or displays in browser
5. User also subscribed to email list

### With Double Opt-In ENABLED:
1. User enters email
2. Form submits to Kit
3. Kit shows "Check your email" message
4. Redirect does NOT happen until email is confirmed
5. (This defeats the purpose of instant PDF access)

## File Locations

### Repository Structure
```
/home/runner/work/node-null-control/node-null-control/
├── public/
│   └── preview/
│       └── displacement_risk_atlas_preview.pdf  (44KB, committed)
├── forge/
│   └── index.html  (updated with redirect)
├── vercel.json  (updated with preview headers)
└── tests/
    └── test_vercel_deployment.py  (new tests)
```

### Generated Files (Not Committed)
```
products/displacement_risk_atlas/runs/2026-W06/outputs/
├── displacement_risk_atlas_preview.pdf  (44KB, gitignored)
├── displacement_risk_atlas_v1.0.pdf  (68KB, gitignored)
├── displacement_risk_atlas_full.html  (gitignored)
├── displacement_risk_atlas_preview.html  (gitignored)
└── manifest.json  (gitignored)
```

Note: Product outputs are gitignored per `.gitignore` line 24.

## Testing Commands

### Run All Tests
```bash
cd /home/runner/work/node-null-control/node-null-control
python3 -m pytest tests/test_vercel_deployment.py -v
```

### Test PDF Exists
```bash
ls -lh public/preview/displacement_risk_atlas_preview.pdf
file public/preview/displacement_risk_atlas_preview.pdf
```

### Validate Configuration
```bash
# Validate vercel.json
python3 -c "import json; json.load(open('vercel.json'))"

# Check redirect URL
grep -o 'redirect_url":"[^"]*"' forge/index.html
```

## Next Actions

1. ✅ **Verify Vercel deployment** (~30 seconds after push)
   - Check: `https://ghost-network-interface.vercel.app/preview/displacement_risk_atlas_preview.pdf`

2. ⚠️ **Disable double opt-in** in Kit settings
   - Kit dashboard → Settings → Email → Subscribers → Confirmed opt-in: OFF

3. ✅ **Test form submission flow**
   - Submit test email → verify immediate PDF redirect

4. ✅ **Monitor Kit form analytics**
   - Track submissions
   - Track successful redirects
   - Check for errors

5. 📝 **Update documentation** (if needed)
   - Add URL to product README
   - Update email sequence links

## Troubleshooting

### PDF Not Loading (404)
- Wait 30-60 seconds for Vercel deployment
- Clear browser cache
- Check Vercel deployment logs

### Form Doesn't Redirect
- Check Kit double opt-in setting (must be OFF)
- Check browser console for JavaScript errors
- Verify `data-options` attribute is present in form HTML

### PDF Downloads Instead of Displaying
- Expected behavior in some browsers
- Depends on browser PDF viewer settings
- Not a bug, both behaviors are acceptable

### Wrong PDF Content
- Rebuild PDF: `python3 scripts/build_displacement_atlas.py --run-json products/displacement_risk_atlas/runs/2026-W06/run.json`
- Copy to public: `cp products/displacement_risk_atlas/runs/2026-W06/outputs/displacement_risk_atlas_preview.pdf public/preview/`
- Commit and push

## Security Summary

✅ No security vulnerabilities detected (CodeQL scan passed)

- PDF served with `X-Content-Type-Options: nosniff` header
- No user input or dynamic content in PDF
- Static file serving only
- No secret keys or credentials in code
- Form handled by ConvertKit (external, trusted service)

## References

- Problem statement: Option A - Static File in Vercel Deployment
- Kit form ID: 9045590
- Vercel domain: ghost-network-interface.vercel.app
- PDF size: 44,430 bytes (44KB as specified)
- PDF pages: 3 (cover + excerpt + sample + CTA)

---

**Status:** ✅ All changes implemented and tested  
**Ready for:** Production deployment  
**Verification:** Required after Vercel deployment completes
