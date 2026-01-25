# Forge (Conversion Interface)

Single-page, neutral routing interface for the Ghost Network.

Goals:

- Explain the system (not the creator)
- Route attention into assets (starting with Weekly Signal Brief)
- Optional identity binding (off-by-default; local-only)

## Deploy

Any static host:

- GitHub Pages
- Cloudflare Pages
- Netlify
- Vercel (static)

If you want identity capture using a Vercel Serverless Function, deploy on Vercel and use `/api/identity`.

### GitHub Pages (simple)

Option A: serve the repo root (publishes a lot of internal docs). Only do this if that’s intended.

Option B (recommended): copy just `forge/` + the minimal linked docs into a `public/` or `site/` folder and publish that.

## Configuration

Edit `forge/config.js`:

- `ASSETS_URL`: where the page loads `monetization/assets/assets.json` from
- `IDENTITY_POST_URL`: optional POST endpoint for identity binding (disabled by default)

### Vercel API (recommended)

This repo includes a minimal serverless endpoint at `api/identity.js`.

To enable server capture:

1) In Vercel project settings, set env var `IDENTITY_WEBHOOK_URL` to a compliant sink you control (Make/Zapier/webhook receiver).
2) Set `IDENTITY_POST_URL` in `forge/config.js` to `"/api/identity"`.
3) Users must check the consent box before any network post occurs.

Notes:

- The client never sends the raw access token; it sends `token_sha256` only.
- If `IDENTITY_WEBHOOK_URL` is not set, the API returns `501 identity_capture_disabled`.

By default, the page:

- Stores identity in `localStorage` only
- Does not send identity over the network
- Uses no analytics and no trackers

## Local preview

Open `forge/index.html` directly in a browser.

Note: some browsers block `fetch()` from `file://` pages. If assets don’t load locally, use a tiny static server.

Example (Python):

- `python -m http.server 8000`
- open `http://localhost:8000/forge/`
