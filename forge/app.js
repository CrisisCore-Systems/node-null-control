function $(id){return document.getElementById(id)}

function getConfig(){
  const cfg = (window.NODE_NULL_FORGE_CONFIG || {});
  const url = new URL(window.location.href);
  const assetsOverride = url.searchParams.get("assets_url");
  return {
    ASSETS_URL: assetsOverride || cfg.ASSETS_URL || "../monetization/assets/assets.json",
    IDENTITY_POST_URL: cfg.IDENTITY_POST_URL || null,
    SHOW_DRAFT_ASSETS: Boolean(cfg.SHOW_DRAFT_ASSETS),
  };
}

function escapeHtml(s){
  return String(s)
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}

function renderAsset(asset){
  const status = asset.lifecycle_status || "unknown";
  const tagClass = status === "active" ? "asset__tag asset__tag--active" : "asset__tag asset__tag--draft";

  const name = escapeHtml(asset.asset_name || asset.asset_id || "asset");
  const id = escapeHtml(asset.asset_id || "");
  const version = escapeHtml(asset.asset_version || "");
  const surface = escapeHtml(asset.surface_type || "");
  const value = escapeHtml(asset.value_type || "");

  // Routing targets are intentionally conservative: link to the system docs.
  const weeklyBriefHref = "../products/weekly_signal_brief/README.md";

  const primaryLink = (asset.asset_id === "NNASSET-0001-weekly-signal-brief")
    ? `<a class="btn btn--primary" href="${weeklyBriefHref}">Weekly Signal Brief</a>`
    : "";

  return `
    <article class="asset">
      <div class="asset__top">
        <div>
          <h3 class="asset__name">${name}</h3>
          <div class="asset__meta">${id} • ${version} • ${surface}/${value}</div>
        </div>
        <span class="${tagClass}">${escapeHtml(status)}</span>
      </div>
      <div class="actions" style="margin-top:10px">
        ${primaryLink}
        <a class="btn btn--ghost" href="../monetization/assets/registry.md">Registry</a>
      </div>
    </article>
  `;
}

async function loadAssets(){
  const cfg = getConfig();
  const statusEl = $("assets_status");
  const listEl = $("assets_list");

  statusEl.textContent = "loading";
  listEl.innerHTML = "";

  try{
    const res = await fetch(cfg.ASSETS_URL, { cache: "no-store" });
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const assets = Array.isArray(data.assets) ? data.assets : [];

    const filtered = assets.filter(a => {
      const status = a.lifecycle_status;
      if(status === "active") return true;
      if(cfg.SHOW_DRAFT_ASSETS && (status === "draft" || status === "pending")) return true;
      return false;
    });

    statusEl.textContent = `${filtered.length} active`;

    if(filtered.length === 0){
      listEl.innerHTML = `<p class="muted">No active outputs published yet.</p>`;
      return;
    }

    listEl.innerHTML = filtered.map(renderAsset).join("");
  }catch(err){
    statusEl.textContent = "error";
    listEl.innerHTML = `<p class="muted">Failed to load assets. Check config.</p>`;
  }
}

function setStatus(msg, isError){
  const el = $("identity_status");
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "rgba(39,215,255,.92)";
}

function loadIdentity(){
  try{
    const raw = localStorage.getItem("node_null_identity_v1");
    return raw ? JSON.parse(raw) : null;
  }catch{ return null; }
}

function saveIdentity(identity){
  localStorage.setItem("node_null_identity_v1", JSON.stringify(identity));
}

function clearIdentity(){
  localStorage.removeItem("node_null_identity_v1");
}

async function maybePostIdentity(identity){
  const cfg = getConfig();
  if(!cfg.IDENTITY_POST_URL) return { posted:false };

  const res = await fetch(cfg.IDENTITY_POST_URL, {
    method:"POST",
    headers:{"content-type":"application/json"},
    body: JSON.stringify({
      schema_version:"v1",
      captured_at_utc: new Date().toISOString(),
      consent: true,
      identity
    })
  });
  if(!res.ok) throw new Error(`identity post failed: HTTP ${res.status}`);
  return { posted:true };
}

async function sha256Hex(str){
  const enc = new TextEncoder();
  const buf = await crypto.subtle.digest("SHA-256", enc.encode(String(str)));
  const bytes = Array.from(new Uint8Array(buf));
  return bytes.map(b => b.toString(16).padStart(2, "0")).join("");
}

function wireAccess(){
  const enter = $("enter");
  const access = $("access");
  const form = $("identity_form");
  const clearBtn = $("clear_identity");

  enter.addEventListener("click", () => {
    access.hidden = false;
    access.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  const existing = loadIdentity();
  if(existing){
    setStatus("identity already bound locally", false);
  } else {
    setStatus("identity not bound", false);
  }

  clearBtn.addEventListener("click", () => {
    clearIdentity();
    form.reset();
    setStatus("cleared", false);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fd = new FormData(form);
    const identity = {
      email: String(fd.get("email") || "").trim() || null,
      handle: String(fd.get("handle") || "").trim() || null,
      token: String(fd.get("token") || "").trim() || null,
    };

    const cfg = getConfig();
    const consent = Boolean(fd.get("consent"));
    if(cfg.IDENTITY_POST_URL && !consent){
      setStatus("consent required to post identity", true);
      return;
    }

    // Store locally regardless.
    saveIdentity(identity);

    try{
      // Never send raw token over the network; send hash only.
      const tokenSha = identity.token ? await sha256Hex(identity.token) : null;
      const payload = {
        email: identity.email,
        handle: identity.handle,
        token_sha256: tokenSha,
      };

      const r = await maybePostIdentity(payload);
      if(r.posted){
        setStatus("bound locally + posted to endpoint", false);
      } else {
        setStatus("bound locally (no network calls)", false);
      }
    }catch(err){
      setStatus("bound locally; endpoint post failed", true);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadAssets();
  wireAccess();
});
