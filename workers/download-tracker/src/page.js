/**
 * Human product surface for ShadowLock.
 * Dual-surface: this HTML is the complete software UI. Agents use /v1 + MCP.
 * Author: Aziel Eliab only. Apache-2.0. Forks welcome.
 */
const HOST = "https://shadowlock-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/shadowlock";
const GITHUB_LATEST = "https://github.com/AzielEliab/shadowlock/releases/latest";
const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
const CATALOG_CARD = "https://aziel-runtime.vibelock.workers.dev/p/shadowlock/";
const TITLE = "ShadowLock — Aziel Eliab";
const VERSION = "0.2.0";
const MOTTO = "Change is optional. Truth is not.";
const DESCRIPTION =
  "ShadowLock by Aziel Eliab is a read-only, zero-retention outcome mirror. Observe jobs you already have, compare them to a class prior, and read money made / lost / left on the table. OS-hooks into AZ-OS under ethics policy. Counted download and one-click install. Apache-2.0.";
const LIMITATION =
  "THIS IS: a counterfactual observation envelope with hashed ids. OS-hooks into AZ-OS under ethics policy. Hosted Attach is an ethics-gated overlay receipt, not a kernel and not process control. THIS IS NOT: a people profiler, PII store, truth score, dispatcher, optimizer, or process controller. Zero-retention on /v1. Author Aziel Eliab.";
const INSTALL_LINE = "curl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash";
const HISTORICAL_DOI = "10.5281/zenodo.21435707";
const DEFAULT_UA = "Mozilla/5.0";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function citeJson() {
  return {
    author: "Aziel Eliab",
    identity: "Aziel Eliab",
    title: "ShadowLock",
    version: VERSION,
    one_line:
      "Read-only zero-retention outcome mirror by Aziel Eliab. Compares a finished job to a class prior. Does not run jobs or store PII.",
    motto: MOTTO,
    github: GITHUB_REPO,
    homepage: HOST + "/",
    download: HOST + "/download",
    install: HOST + "/install.sh",
    doi: null,
    doi_historical: HISTORICAL_DOI,
    doi_url_historical: "https://doi.org/" + HISTORICAL_DOI,
    zenodo_status: "historical_doi_tombstoned",
    software_deposit_needed: true,
    doi_note:
      "Known DOI 10.5281/zenodo.21435707 is historical. Zenodo currently returns 410/404 for that record. Software deposit needed. No DOI invented.",
    license: "Apache-2.0",
    catalog: CATALOG,
    catalog_card: CATALOG_CARD,
    related_identifiers: [
      { identifier: GITHUB_REPO, relation: "isSupplementTo", resource_type: "software", scheme: "url" },
      { identifier: HOST + "/download", relation: "isIdenticalTo", resource_type: "software", scheme: "url" },
    ],
    software_tarball: {
      url: HOST + "/download",
      filename: "shadowlock-0.2.0.tar.gz",
      content_type: "application/gzip",
      note: "Counted Worker /download asset (gzip 200). No 302 to GitHub.",
    },
    how_to_cite:
      "Eliab, Aziel. (2026). ShadowLock 0.2.0 [Software]. Apache-2.0. https://github.com/AzielEliab/shadowlock https://shadowlock-download-tracker.vibelock.workers.dev/",
  };
}

export function jsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "ShadowLock",
    alternateName: TITLE,
    softwareVersion: VERSION,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Cloudflare Workers, Python 3.10+",
    description: DESCRIPTION,
    url: HOST + "/",
    downloadUrl: HOST + "/download",
    installUrl: HOST + "/install.sh",
    license: "https://www.apache.org/licenses/LICENSE-2.0",
    author: { "@type": "Person", name: "Aziel Eliab", url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: "Aziel Eliab", url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    sameAs: [GITHUB_REPO, CATALOG_CARD],
    image: HOST + "/sigil.png",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };
}

export function robotsTxt() {
  return [
    "User-agent: *",
    "Allow: /",
    "",
    "User-agent: GPTBot",
    "Allow: /",
    "User-agent: ChatGPT-User",
    "Allow: /",
    "User-agent: Google-Extended",
    "Allow: /",
    "User-agent: anthropic-ai",
    "Allow: /",
    "User-agent: ClaudeBot",
    "Allow: /",
    "User-agent: PerplexityBot",
    "Allow: /",
    "User-agent: Bytespider",
    "Allow: /",
    "User-agent: CCBot",
    "Allow: /",
    "",
    "Sitemap: " + HOST + "/sitemap.xml",
    "",
  ].join("\n");
}

export function sitemapXml() {
  const locs = [
    HOST + "/",
    HOST + "/download",
    HOST + "/install.sh",
    HOST + "/v1/skill",
    HOST + "/v1/health",
    HOST + "/openapi.json",
    HOST + "/cite.json",
    HOST + "/llms.txt",
    HOST + "/sigil.png",
    GITHUB_REPO,
    CATALOG_CARD,
  ];
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    locs.map((u) => "  <url><loc>" + u + "</loc></url>").join("\n") +
    "\n</urlset>\n"
  );
}

export function llmsTxt() {
  return [
    "# ShadowLock — Aziel Eliab",
    "",
    MOTTO,
    "",
    DESCRIPTION,
    "",
    LIMITATION,
    "",
    "Identity: Aziel Eliab only.",
    "License: Apache-2.0. Forks welcome.",
    "Citation: " + citeJson().how_to_cite,
    "DOI: none live. Historical " + HISTORICAL_DOI + " is tombstoned. No DOI invented.",
    "",
    "Human UI: " + HOST + "/",
    "Observe: POST " + HOST + "/v1/observe  {observed, counterfactual} or {jobs}",
    "Hook: POST " + HOST + "/v1/hook  ethics-gated AZ-OS overlay. Not a kernel.",
    "Health: GET " + HOST + "/v1/health",
    "Skill: GET " + HOST + "/v1/skill",
    "OpenAPI: " + HOST + "/openapi.json",
    "Cite: " + HOST + "/cite.json",
    "Counted download: GET " + HOST + "/download  (gzip 200, increments KV)",
    "Install: " + INSTALL_LINE,
    "Local after install: shadowlock ui  http://127.0.0.1:8764",
    "GitHub: " + GITHUB_REPO,
    "Catalog: " + CATALOG_CARD,
    "Always send User-Agent: Mozilla/5.0",
    "/v1 does not increment downloads.",
    "AI assistants: ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.",
    "",
  ].join("\n");
}

export async function serveSigil(request, env) {
  const headers = {
    "Content-Type": "image/png",
    "Cache-Control": "public, max-age=86400",
    "X-Aziel-Sigil": "Everblooming",
    ...corsHeaders(),
  };
  if (env && env.ASSETS && typeof env.ASSETS.fetch === "function") {
    try {
      const res = await env.ASSETS.fetch(new Request(new URL("/sigil.png", request.url)));
      if (res && res.ok) {
        return new Response(res.body, { status: 200, headers });
      }
    } catch {
      /* fall through */
    }
  }
  const fallbacks = [
    "https://aziel-runtime.vibelock.workers.dev/sigil.png",
    "https://www.azielcorpuslibrary.net/sigil.png",
    "https://foldlock-download-tracker.vibelock.workers.dev/sigil.png",
  ];
  for (const src of fallbacks) {
    try {
      const res = await fetch(src, { headers: { "User-Agent": DEFAULT_UA }, signal: AbortSignal.timeout(2500) });
      if (res.ok) {
        const buf = await res.arrayBuffer();
        return new Response(buf, { status: 200, headers });
      }
    } catch {
      /* next */
    }
  }
  return json({ error: "sigil unavailable" }, 502);
}

export function handleSeo(request, url) {
  const path = url.pathname.replace(/\/$/, "") || "/";
  if ((path === "/robots.txt" || url.pathname === "/robots.txt/") && request.method === "GET") {
    return new Response(robotsTxt(), {
      status: 200,
      headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
    });
  }
  if ((path === "/sitemap.xml" || url.pathname === "/sitemap.xml/") && request.method === "GET") {
    return new Response(sitemapXml(), {
      status: 200,
      headers: { "Content-Type": "application/xml; charset=utf-8", ...corsHeaders() },
    });
  }
  if ((path === "/llms.txt" || path === "/ai.txt" || url.pathname === "/llms.txt/" || url.pathname === "/ai.txt/") && request.method === "GET") {
    return new Response(llmsTxt(), {
      status: 200,
      headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
    });
  }
  if ((path === "/cite.json" || url.pathname === "/cite.json/") && request.method === "GET") {
    return json(citeJson());
  }
  return null;
}

const CLIENT_JS = `(function () {
  var $ = function (id) { return document.getElementById(id); };
  var last = null;
  var view = "simple";
  var SAMPLE_OBS = {"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"};
  var SAMPLE_CF = {"duration":[25,45],"cost":[70,110],"revenue":[180,260]};
  var SAMPLE_JOBS = [
    {"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"},
    {"id":"WO-0002","task_class":"repair","urgency":0.7,"actual_duration":55,"actual_cost":140,"actual_revenue":200,"actual_outcome":"complete"}
  ];
  function fail(msg) {
    $("err").hidden = false;
    $("err").textContent = msg;
  }
  function money(n) {
    if (n == null || n === "") return "—";
    var x = Number(n);
    if (!Number.isFinite(x)) return String(n);
    return x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }
  function setView(name) {
    view = name;
    $("view-simple").classList.toggle("on", name === "simple");
    $("view-advanced").classList.toggle("on", name === "advanced");
    $("advanced").classList.toggle("hidden", name !== "advanced");
  }
  function chips(ids) {
    if (!ids || !ids.length) return "—";
    return ids.map(function (id) { return '<code class="hid">' + String(id) + "</code>"; }).join(" ");
  }
  function classRows(map) {
    if (!map || typeof map !== "object") return "—";
    return Object.keys(map).map(function (k) { return k + " × " + map[k]; }).join(", ") || "—";
  }
  function ethicsRows(ethics) {
    if (!ethics) return "";
    var gates = ethics.gates || {};
    var rows = Object.keys(gates).map(function (k) {
      var g = gates[k] || {};
      return "<dt>" + k + "</dt><dd>" + (g.pass ? "pass" : "refuse") + " — " + (g.reason || "") + "</dd>";
    }).join("");
    return "<dt>ethics</dt><dd>" + (ethics.passed ? "passed" : "refused") + "</dd>" + rows;
  }
  function render(data) {
    last = data;
    $("result").hidden = false;
    $("err").hidden = true;
    var r = data.report || {};
    var L = r.ledger || {};
    var exp = data.expectation || {};
    var ids = r.sampled_hashed_ids || (data.hashed_id ? [data.hashed_id] : []);
    var attached = data.attached;
    var plain = "Compared this job list to a guess. Names are dropped. Nothing is saved on this Worker.";
    if (attached === true) plain = "Ethics-gated AZ-OS overlay attached. Observation is a receipt, not process control. Names are dropped. Nothing is saved.";
    if (attached === false) plain = "AZ-OS overlay did not attach. See ethics gates.";
    $("plain").textContent = plain;
    $("summary").innerHTML =
      "<dt>jobs looked at</dt><dd>" + (r.observed != null ? r.observed : (data.job_count != null ? data.job_count : "—")) + "</dd>" +
      "<dt>jobs sampled</dt><dd>" + (r.sampled != null ? r.sampled : "—") + "</dd>" +
      "<dt>task classes</dt><dd>" + classRows(r.by_task_class) + "</dd>" +
      "<dt>hashed ids</dt><dd>" + chips(ids) + "</dd>" +
      "<dt>money made</dt><dd>" + money(L.money_made) + "</dd>" +
      "<dt>money lost</dt><dd>" + money(L.money_lost) + "</dd>" +
      "<dt>left on the table</dt><dd>" + money(L.money_left_on_table) + "</dd>" +
      "<dt>net gap</dt><dd>" + money(L.net_variance) + "</dd>" +
      "<dt>efficiency</dt><dd>" + (L.efficiency_score != null ? money(L.efficiency_score) : "—") + "</dd>" +
      (exp.task_class ? "<dt>last class / urgency</dt><dd>" + exp.task_class + " · " + (exp.urgency != null ? exp.urgency : "—") + "</dd>" : "") +
      (data.protocol ? "<dt>protocol</dt><dd>" + data.protocol + "</dd>" : "") +
      ethicsRows(data.ethics);
    $("ledger-made").textContent = money(L.money_made);
    $("ledger-lost").textContent = money(L.money_lost);
    $("ledger-table").textContent = money(L.money_left_on_table);
    $("ledger-net").textContent = money(L.net_variance);
    $("json").textContent = JSON.stringify(data, null, 2);
    $("export").disabled = false;
    setView(view);
  }
  function parseObserved() {
    var jobsRaw = ($("jobs").value || "").trim();
    var observed = JSON.parse($("observed").value || "{}");
    var counterfactual = JSON.parse($("counterfactual").value || "{}");
    if (jobsRaw) {
      var jobs = JSON.parse(jobsRaw);
      if (!Array.isArray(jobs) || !jobs.length) throw new Error("Job list must be a non-empty JSON array.");
      return { jobs: jobs, counterfactual: counterfactual };
    }
    if (!observed || typeof observed !== "object" || Array.isArray(observed)) throw new Error("Observed must be a JSON object.");
    return { observed: observed, counterfactual: counterfactual };
  }
  async function postJson(path, body) {
    var res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "User-Agent": "Mozilla/5.0" },
      body: JSON.stringify(body),
    });
    var data = await res.json();
    if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
    return data;
  }
  async function runObserve() {
    $("err").hidden = true;
    $("run").disabled = true;
    try {
      render(await postJson("/v1/observe", parseObserved()));
    } catch (e) { fail(String(e.message || e)); }
    finally { $("run").disabled = false; }
  }
  async function runHook() {
    $("err").hidden = true;
    $("attach").disabled = true;
    try {
      var parsed;
      try { parsed = parseObserved(); }
      catch (e) { parsed = { jobs: [SAMPLE_OBS], counterfactual: SAMPLE_CF }; }
      var body = { ethics: { actor: "operator" }, counterfactual: parsed.counterfactual || {} };
      if (parsed.jobs) body.jobs = parsed.jobs;
      else if (parsed.observed && Object.keys(parsed.observed).length) body.jobs = [parsed.observed];
      var data = await postJson("/v1/hook", body);
      if (data.report) render(data);
      else {
        $("result").hidden = false;
        $("plain").textContent = data.attached
          ? "Attached via hosted AZ-OS overlay. Ethics passed. No jobs sampled yet."
          : "AZ-OS overlay did not complete.";
        $("summary").innerHTML =
          "<dt>attached</dt><dd>" + (data.attached ? "yes" : "no") + "</dd>" +
          "<dt>protocol</dt><dd>" + (data.protocol || "—") + "</dd>" +
          ethicsRows(data.ethics);
        $("json").textContent = JSON.stringify(data, null, 2);
        last = data;
        $("export").disabled = false;
      }
    } catch (e) { fail(String(e.message || e)); }
    finally { $("attach").disabled = false; }
  }
  $("mirror-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    runObserve();
  });
  $("view-simple").addEventListener("click", function () { setView("simple"); });
  $("view-advanced").addEventListener("click", function () { setView("advanced"); });
  $("import-btn").addEventListener("click", function () { $("import-json").click(); });
  $("import-json").addEventListener("change", function () {
    var f = $("import-json").files && $("import-json").files[0];
    if (!f) return;
    var reader = new FileReader();
    reader.onload = function () {
      var obj;
      try { obj = JSON.parse(String(reader.result || "{}")); }
      catch (e) { fail("That file is not valid JSON."); return; }
      var observed = obj.observed || (obj.payload && obj.payload.observed) || (Array.isArray(obj.jobs) ? obj.jobs[0] : obj);
      var counterfactual = obj.counterfactual || (obj.payload && obj.payload.counterfactual) || {};
      $("observed").value = JSON.stringify(observed, null, 2);
      if (counterfactual && typeof counterfactual === "object" && Object.keys(counterfactual).length) {
        $("counterfactual").value = JSON.stringify(counterfactual, null, 2);
      }
      if (Array.isArray(obj.jobs) && obj.jobs.length) {
        $("jobs").value = JSON.stringify(obj.jobs, null, 2);
      }
      runObserve();
    };
    reader.readAsText(f);
  });
  $("attach").addEventListener("click", runHook);
  $("sample").addEventListener("click", function () {
    $("observed").value = JSON.stringify(SAMPLE_OBS, null, 2);
    $("counterfactual").value = JSON.stringify(SAMPLE_CF, null, 2);
    $("jobs").value = JSON.stringify(SAMPLE_JOBS, null, 2);
    runObserve();
  });
  $("export").addEventListener("click", function () {
    if (!last) return;
    var blob = new Blob([JSON.stringify(last, null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "shadowlock-report.json";
    a.click();
    URL.revokeObjectURL(a.href);
  });
  var installBtn = $("install-btn");
  var installPre = $("install-cmd");
  if (installBtn) {
    installBtn.addEventListener("click", function () {
      var cmd = "curl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash";
      function done(ok) {
        installBtn.textContent = ok ? "Copied. Paste in Terminal, then run shadowlock ui" : "Select the command, copy it, then run shadowlock ui";
        installBtn.classList.add("copied");
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(cmd).then(function () { done(true); }).catch(function () { done(false); });
      } else {
        done(false);
        if (installPre && window.getSelection) {
          var r = document.createRange();
          r.selectNodeContents(installPre);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(r);
        }
      }
    });
  }
  fetch("/v1/health", { headers: { "User-Agent": "Mozilla/5.0" } })
    .then(function (res) { return res.json(); })
    .then(function (h) {
      var el = $("live");
      if (!el) return;
      el.hidden = false;
      el.textContent = h.ok ? ("Live · " + (h.product || "shadowlock") + " " + (h.version || "") + " · " + (h.ethics || "ready")) : "Worker health failed";
      el.classList.toggle("ok", !!h.ok);
    })
    .catch(function () {
      var el = $("live");
      if (el) { el.hidden = false; el.textContent = "Health unreachable"; }
    });
})();`;

export async function indexHtml(stats) {
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const gh = stats.github || {};
  const ld = JSON.stringify(jsonLd());
  const breakdown = (stats.breakdown || [])
    .map((b) => `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${Number(b.count) || 0}</li>`)
    .join("") || "<li>none yet</li>";
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TITLE}</title>
<meta name="description" content="${escapeHtml(DESCRIPTION)}">
<meta name="author" content="Aziel Eliab">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="icon" type="image/png" href="/sigil.png">
<meta property="og:type" content="website">
<meta property="og:title" content="${TITLE}">
<meta property="og:description" content="${escapeHtml(DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:image" content="${HOST}/sigil.png">
<meta property="og:site_name" content="ShadowLock">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${TITLE}">
<meta name="twitter:description" content="${escapeHtml(DESCRIPTION)}">
<meta name="twitter:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root {
    color-scheme: dark;
    --bg: #0e1014; --panel: #151922; --ink: #e8eaef; --muted: #9aa3b2;
    --line: #2a3140; --gold: #d4af37; --gold2: #f0d78c; --focus: #7aa2d4;
    --bad: #d4534b; --ok: #7dcea0; --ink-inv: #0e1014;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Segoe UI", sans-serif; line-height: 1.45; }
  body { max-width: 52rem; margin: 0 auto; padding: 2rem 1.2rem 4rem; }
  a { color: #c9d4ff; }
  .brandrow { display: flex; align-items: center; gap: 12px; margin: 0 0 10px; }
  .brandmark { width: 48px; height: 48px; border-radius: 12px; object-fit: cover; flex: 0 0 auto;
    box-shadow: 0 0 0 1px #d4af3733; background: #0a0c10; }
  .stamp { margin: 0; color: var(--gold); font-size: .88rem; letter-spacing: .02em; }
  .tag { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }
  h1 { font-size: 2rem; font-weight: 650; letter-spacing: 0.03em; margin: 0.2rem 0 0.25rem; }
  h2 { font-size: 1.05rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin: 1.4rem 0 0.7rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 0.75rem; font-size: 1.08rem; }
  .lede { color: var(--muted); margin: 0 0 1rem; max-width: 44rem; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: var(--gold2);
    padding: .85rem 1rem; border-radius: 10px; margin: 0 0 1.2rem; font-size: .92rem; }
  .live { display: inline-block; margin: 0 0 1rem; padding: .28rem .7rem; border-radius: 999px;
    border: 1px solid var(--line); color: var(--muted); font-size: .82rem; }
  .live.ok { border-color: #2f5a40; color: var(--ok); }
  fieldset, .card { border: 1px solid var(--line); border-radius: 12px; background: var(--panel);
    padding: 1.1rem 1.15rem 1.2rem; margin: 0 0 1rem; }
  legend { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); padding: 0 0.4rem; }
  label { display: block; font-size: 0.92rem; margin: 0.85rem 0 0.3rem; }
  label .kicker { display: block; font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.12rem; }
  textarea { width: 100%; padding: 0.55rem 0.65rem; border: 1px solid var(--line);
    border-radius: 6px; background: #10161d; color: var(--ink);
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.88rem; }
  textarea:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .actions { display: flex; gap: 0.65rem; flex-wrap: wrap; margin: 0.4rem 0 1.2rem; }
  button, a.btn { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.7rem 1rem; border-radius: 8px;
    border: 1px solid var(--ink); background: var(--ink); color: var(--ink-inv);
    cursor: pointer; font-weight: 650; text-decoration: none; display: inline-block; text-align: center; }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  button.ghost, a.btn.ghost { background: transparent; color: var(--ink); }
  button.gold, a.btn.gold { background: var(--gold); color: #14110a; border-color: var(--gold); }
  button.gold.copied { background: var(--ok); color: #0e1014; border-color: var(--ok); }
  .addfile { display: flex; align-items: center; justify-content: center; text-align: center;
    width: 100%; min-height: 6.4rem; font-size: 1.35rem; font-weight: 700;
    letter-spacing: 0.02em; border: 2px dashed var(--gold); background: #1a160c;
    color: var(--ink); border-radius: 14px; cursor: pointer; margin: 0.2rem 0 0.7rem; }
  .addfile:hover { filter: brightness(1.08); }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 560px) { .btns { grid-template-columns: 1fr; } body { padding-top: 1.2rem; } }
  a.btn.primary, .btns a.btn { width: 100%; font-size: 1.15rem; padding: 1rem 1.1rem; }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.1rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .95rem; font-weight: 500; color: var(--muted); }
  .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: .6rem; margin: 0 0 1rem; }
  @media (max-width: 720px) { .metrics { grid-template-columns: 1fr 1fr; } }
  .metric { border: 1px solid var(--line); border-radius: 10px; background: #10161d; padding: .7rem .8rem; }
  .metric b { display: block; font-size: 1.25rem; font-variant-numeric: tabular-nums; }
  .metric span { color: var(--muted); font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; }
  .views { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; overflow: hidden; margin: 0 0 1rem; }
  .views button { border: 0; border-radius: 0; padding: 0.35rem 0.9rem; background: transparent; color: var(--muted); }
  .views button.on { background: var(--gold); color: #14110a; font-weight: 650; }
  dl { display: grid; grid-template-columns: 12rem 1fr; gap: 0.3rem 1rem; margin: 0; }
  dt { color: var(--muted); }
  .hid { background: #10161d; padding: .1rem .35rem; border-radius: 4px; }
  pre { background: #0e1014; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  code { font-size: .88rem; }
  .plain { font-size: 1.08rem; margin: 0 0 0.7rem; }
  .err { color: var(--bad); }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0,0,0,0); border: 0; }
  .hidden { display: none; }
  .cite { border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.15rem; background: #12151c; }
  .cite h2 { margin-top: 0; }
  .iso { margin-top: .85rem; font-size: .85rem; color: #7d8696; }
  footer { margin-top: 2rem; color: var(--muted); font-size: 0.88rem; }
  .foot-note { font-style: italic; }
  a.skip { position: absolute; left: -999px; }
  a.skip:focus { left: 1rem; top: 1rem; background: var(--gold); color: #14110a; padding: .4rem .7rem; z-index: 2; }
</style>
</head>
<body>
  <a class="skip" href="#workspace">Skip to workspace</a>
  <header>
    <div class="brandrow">
      <img class="brandmark" src="/sigil.png" width="48" height="48" alt="Everblooming sigil">
      <p class="stamp">Everblooming sigil · Aziel Eliab</p>
    </div>
    <div class="tag">ShadowLock · ${VERSION} · Aziel Eliab · zero-retention · Apache-2.0</div>
    <h1>ShadowLock</h1>
    <p class="motto">${MOTTO}</p>
    <p class="lede">Observe jobs you already have. Compare them to a guess. Read money made, lost, and left on the table. Hashed ids only. This page is the software — not a downloads shell.</p>
    <p class="banner">${escapeHtml(LIMITATION)}</p>
    <p class="live" id="live" hidden>Checking health…</p>
  </header>

  <section id="workspace">
    <h2>Interactive workspace</h2>
    <form id="mirror-form" autocomplete="off">
      <fieldset>
        <legend>Observe</legend>
        <p class="lede" style="margin-bottom:0.4rem">Import a JSON file, paste one observed job, or paste a job list. Show report calls <code>POST /v1/observe</code>. Attach calls <code>POST /v1/hook</code>. Neither increments downloads.</p>
        <input id="import-json" class="sr-only" type="file" accept="application/json,.json">
        <button class="addfile" id="import-btn" type="button">Import JSON file</button>
        <label for="observed">
          <span class="kicker">Observed outcome</span>
          JSON object: id, task_class, urgency, actual_duration, actual_cost, actual_revenue, actual_outcome.
        </label>
        <textarea id="observed" rows="7" placeholder='{"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"}'></textarea>
        <label for="counterfactual">
          <span class="kicker">Counterfactual</span>
          Class prior: duration / cost / revenue as [low, high] or a midpoint.
        </label>
        <textarea id="counterfactual" rows="5" placeholder='{"duration":[25,45],"cost":[70,110],"revenue":[180,260]}'></textarea>
        <label for="jobs">
          <span class="kicker">Job list (optional)</span>
          JSON array. If filled, the Worker observes every job and aggregates the ledger.
        </label>
        <textarea id="jobs" rows="5" placeholder='[{"id":"WO-0001","task_class":"repair","actual_outcome":"complete"}]'></textarea>
      </fieldset>
      <div class="actions">
        <button type="submit" id="run">Show report</button>
        <button type="button" class="ghost" id="attach">Attach via AZ-OS</button>
        <button type="button" class="ghost" id="sample">Load sample</button>
        <button type="button" class="ghost" id="export" disabled>Export JSON report</button>
      </div>
    </form>

    <section id="result" hidden>
      <h2>Report</h2>
      <div class="views" role="group" aria-label="Simple or advanced">
        <button type="button" id="view-simple" class="on">Simple</button>
        <button type="button" id="view-advanced">Advanced</button>
      </div>
      <div class="metrics" aria-label="Ledger">
        <div class="metric"><span>Money made</span><b id="ledger-made">—</b></div>
        <div class="metric"><span>Money lost</span><b id="ledger-lost">—</b></div>
        <div class="metric"><span>Left on table</span><b id="ledger-table">—</b></div>
        <div class="metric"><span>Net gap</span><b id="ledger-net">—</b></div>
      </div>
      <div class="card">
        <p class="plain" id="plain"></p>
        <dl id="summary"></dl>
      </div>
      <div id="advanced" class="hidden">
        <h2>JSON</h2>
        <div class="card"><pre id="json"></pre></div>
      </div>
    </section>
    <p class="err" id="err" hidden></p>
  </section>

  <section id="install">
    <h2>Download and install</h2>
    <div class="card">
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p class="lede"><strong>Counted download.</strong> The gzip is served from this Worker (HTTP 200). No 302 to GitHub. One-click install copies a Terminal command, then run <code>shadowlock ui</code> on this computer.</p>
      <div class="btns">
        <a class="btn primary" href="/download?asset=shadowlock-0.2.0.tar.gz">Download</a>
        <button type="button" class="btn gold" id="install-btn">One-click install</button>
      </div>
      <pre id="install-cmd">${INSTALL_LINE}</pre>
      <p class="lede">Local UI after install: <code>shadowlock ui</code> at http://127.0.0.1:8764 (loopback only). Optional: <code>shadowlock attach</code> then <code>shadowlock doctor --verify</code>.</p>
      <p class="iso">Isolated counter: Worker <code>shadowlock-download-tracker</code>, project <code>shadowlock</code>, KV <code>SHADOWLOCK_DOWNLOADS</code>. Not mixed with any other product. <code>/v1</code> does not increment downloads.</p>
      <p class="lede">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
    </div>
  </section>

  <section class="cite" id="cite">
    <h2>How to cite</h2>
    <p>Eliab, Aziel. (2026). ShadowLock 0.2.0 [Software]. Apache-2.0. <a href="${GITHUB_REPO}">${GITHUB_REPO}</a> · <a href="${HOST}/">${HOST}/</a></p>
    <p>Identity is <strong>Aziel Eliab only</strong>. License Apache-2.0. Forks are welcome and always allowed.</p>
    <p>No live Zenodo DOI. Historical <code>${HISTORICAL_DOI}</code> is tombstoned (Zenodo 410/404). Software deposit needed. No DOI invented. Machine-readable: <a href="/cite.json">/cite.json</a>.</p>
    <p>
      <a href="/stats">JSON stats</a> ·
      <a href="/openapi.json">OpenAPI</a> ·
      <a href="/v1/skill">Skill</a> ·
      <a href="/v1/health">Health</a> ·
      <a href="/llms.txt">llms.txt</a> ·
      <a href="/ai">AI runtime</a> ·
      <a href="${GITHUB_REPO}">GitHub</a> ·
      <a href="${GITHUB_LATEST}">releases</a> ·
      <a href="${CATALOG_CARD}">catalog</a>
    </p>
    <h2>Per repo / branch / fork</h2>
    <ul>${breakdown}</ul>
  </section>

  <footer>
    <p>Apache-2.0 · Aziel Eliab · July 2026 · Hosted workspace calls this Worker’s <code>/v1/observe</code> and <code>/v1/hook</code></p>
    <p class="foot-note">Zero-retention: observe and hook payloads are not written to KV except existing download keys. Hosted Attach is an ethics-gated overlay, not the caller OS.</p>
  </footer>
<script>
${CLIENT_JS}
</script>
</body>
</html>`;
}
