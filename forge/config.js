// Forge config (client-side)
//
// Keep this page governance-safe by default:
// - No analytics
// - No trackers
// - No network calls for identity unless you explicitly set an endpoint
//
// If you set IDENTITY_POST_URL, it must accept a JSON POST body.
// You are responsible for consent + compliance.

window.NODE_NULL_FORGE_CONFIG = {
  // Where to load the assets mirror from.
  // Relative paths work on static hosts that serve the repo as a site.
  // You can override via URL param ?assets_url=https://...
  ASSETS_URL: "../monetization/assets/assets.json",

  // Optional identity capture endpoint (disabled by default).
  // Example: "https://example.com/forge/identity"
  IDENTITY_POST_URL: null,

  // UI
  SHOW_DRAFT_ASSETS: false,
};
