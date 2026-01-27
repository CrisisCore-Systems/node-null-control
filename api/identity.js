export default async function handler(req, res) {
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('cache-control', 'no-store');

  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('allow', 'POST');
    res.end(JSON.stringify({ ok: false, error: 'method_not_allowed' }));
    return;
  }

  const sinkUrl = process.env.IDENTITY_WEBHOOK_URL || '';
  if (!sinkUrl) {
    res.statusCode = 501;
    res.end(
      JSON.stringify({
        ok: false,
        error: 'identity_capture_disabled',
        hint: 'Set IDENTITY_WEBHOOK_URL in Vercel env to enable server capture.',
      })
    );
    return;
  }

  let body = req.body;
  // Vercel may pass raw string depending on runtime.
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'invalid_json' }));
      return;
    }
  }

  const schemaVersion = body?.schema_version;
  const capturedAt = body?.captured_at_utc;
  const consent = body?.consent === true;
  const identity = body?.identity || {};

  if (schemaVersion !== 'v1') {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false, error: 'schema_version_invalid' }));
    return;
  }

  if (!consent) {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false, error: 'consent_required' }));
    return;
  }

  // Minimal validation (keep governance-safe; do not require identity)
  const email = typeof identity.email === 'string' ? identity.email.trim().toLowerCase() : null;
  const handle = typeof identity.handle === 'string' ? identity.handle.trim() : null;
  const tokenSha256 = typeof identity.token_sha256 === 'string' ? identity.token_sha256.trim() : null;

  if (email && email.length > 320) {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false, error: 'email_too_long' }));
    return;
  }
  if (handle && handle.length > 160) {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false, error: 'handle_too_long' }));
    return;
  }
  if (tokenSha256 && !/^[0-9a-f]{64}$/i.test(tokenSha256)) {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false, error: 'token_sha256_invalid' }));
    return;
  }

  const event = {
    schema_version: 'v1',
    source: 'forge',
    received_at_utc: new Date().toISOString(),
    captured_at_utc: typeof capturedAt === 'string' ? capturedAt : null,
    identity: {
      email,
      handle,
      token_sha256: tokenSha256,
    },
  };

  try {
    const r = await fetch(sinkUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(event),
    });

    if (!r.ok) {
      res.statusCode = 502;
      res.end(JSON.stringify({ ok: false, error: 'sink_failed', status: r.status }));
      return;
    }

    res.statusCode = 200;
    res.end(JSON.stringify({ ok: true }));
  } catch {
    res.statusCode = 502;
    res.end(JSON.stringify({ ok: false, error: 'sink_unreachable' }));
  }
}
