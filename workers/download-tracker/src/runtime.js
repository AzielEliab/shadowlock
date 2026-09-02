/**
 * ShadowLock hosted runtime (port of envelope/sample/counterfactual/ledger/report).
 * Zero-retention: never write KV except existing download keys.
 * POST /v1/observe {observed, counterfactual}.
 */
const PRODUCT = "shadowlock";
const EXAMPLE_PAYLOAD = {
  "jobs": [
    {
      "id": "a",
      "status": "ok"
    }
  ]
};

const VERSION = "0.1.0";
const MOTTO = "Change is optional. Truth is not.";
const HOST = "https://shadowlock-download-tracker.vibelock.workers.dev";
const SKILL = "---\nname: ShadowLock\ndescription: Use when comparing an observed outcome to a counterfactual without storing PII. Change is optional. Truth is not. Hosted /v1 via this Worker or aziel-runtime. Author Aziel Eliab.\n---\n\n# ShadowLock\n\nChange is optional. Truth is not.\n\nAuthor: **Aziel Eliab**.\n\nUse when comparing an observed outcome to a counterfactual without storing PII. Change is optional. Truth is not.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Endpoints (this Worker)\n\nHost: `https://shadowlock-download-tracker.vibelock.workers.dev`\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| POST | `/v1/observe` | Observe {observed, counterfactual}. Not stored. |\n\nOpenAPI: `https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json`\n\nCatalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`\n\nMCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n\nCatalog aliases under `/p/shadowlock/\u2026`.\n\n## How to call (Mozilla/5.0)\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' -X POST https://shadowlock-download-tracker.vibelock.workers.dev/v1/observe \\\n  -H 'content-type: application/json' \\\n  -d '{\"observed\":{\"id\":\"job-1\",\"outcome\":\"done\"},\"counterfactual\":{\"outcome\":\"skipped\"}}'\ncurl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill\n```\n\nGrok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash\nshadowlock ui\n```\n\nThen open http://127.0.0.1:8764 (this computer only).\n\n## Honest banner\n\nTHIS IS: a counterfactual observation envelope with hashed ids. THIS IS NOT: a people profiler, PII store, or truth score. Zero-retention on /v1. Author Aziel Eliab.\n\nDOI: https://doi.org/10.5281/zenodo.21435707  \nRecord: https://zenodo.org/records/21435707\n\nApache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.\n\n## Catalog + local UI\n\nAuthor: **Aziel Eliab**. Honest scope: Zero-retention observation of a job list you already have. No OS hook.\n\n- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/shadowlock/\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- This Worker skill: `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill`\n- This Worker OpenAPI: https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json\n- Sample payload: `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/example`\n\nLocal UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `shadowlock doctor`.\n\nGrok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n";

const HASHED_ID_HEX_LEN = 12;
const PII_KEYS = new Set([
  "name","full_name","first_name","last_name","email","phone","phone_number","mobile","person",
  "person_name","team","team_name","department","department_name","technician","technician_name",
  "worker","worker_name","assignee","assignee_name","employee","employee_name","username","ssn",
  "address","operator","operator_name",
]);
const ID_KEYS = ["id","job_id","jobId","raw_id","ticket","ticket_id","work_order"];
const TS_KEYS = ["timestamp","ts","created_at","time","opened_at"];
const CLASS_KEYS = ["task_class","class","type","job_type","category"];
const URGENCY_KEYS = ["urgency","priority"];
const OUTCOME_KEYS = ["actual_outcome","outcome","status","result"];
const REVENUE_KEYS = ["actual_revenue","revenue"];
const COST_KEYS = ["actual_cost","cost"];
const DURATION_KEYS = ["actual_duration","duration"];
const CONTEXT_KEYS = ["context_signals","context","signals"];
const CORE_CONSUMED = new Set([...ID_KEYS, ...TS_KEYS, ...CLASS_KEYS, ...URGENCY_KEYS, ...OUTCOME_KEYS, ...REVENUE_KEYS, ...COST_KEYS, ...CONTEXT_KEYS]);
const URGENCY_ENUM = { low: 0.25, medium: 0.5, med: 0.5, high: 0.75, critical: 1.0, urgent: 0.9 };

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

function isPiiKey(key) {
  const k = String(key).trim().toLowerCase().replace(/-/g, "_");
  if (PII_KEYS.has(k)) return true;
  for (const token of ["email", "phone", "ssn", "fullname"]) {
    if (k.includes(token)) return true;
  }
  if (k.endsWith("_name") || k.endsWith("name")) return true;
  if (k === "team" || k === "department" || k === "person") return true;
  return false;
}

function sanitizeContext(signals) {
  const out = {};
  if (!signals || typeof signals !== "object") return out;
  for (const [key, value] of Object.entries(signals)) {
    if (isPiiKey(key)) continue;
    if (typeof value === "boolean") out[key] = value;
    else if (typeof value === "number" && Number.isFinite(value)) out[key] = value;
    else if (typeof value === "string") {
      if (value.includes("@") && value.split("@").pop().includes(".")) continue;
      out[key] = value;
    }
  }
  return out;
}

function first(record, keys, fallback = null) {
  for (const k of keys) {
    if (record[k] != null && record[k] !== "") return record[k];
  }
  return fallback;
}

function asFloat(value, fallback = null) {
  if (value == null || value === "") return fallback;
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function asUrgency(value) {
  if (value == null || value === "") return 0.5;
  if (typeof value === "string") {
    const mapped = URGENCY_ENUM[value.trim().toLowerCase()];
    if (mapped != null) return mapped;
    const n = Number(value);
    if (!Number.isFinite(n)) return 0.5;
    value = n;
  }
  const n = Number(value);
  if (n > 1.0) {
    if (n <= 5) return Math.max(0, Math.min(1, n / 5));
    if (n <= 10) return Math.max(0, Math.min(1, n / 10));
    return 1.0;
  }
  return Math.max(0, Math.min(1, n));
}

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

async function sha256Bytes(bytes) {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
}

async function identityDigest(salt, rawId) {
  const enc = new TextEncoder();
  const saltB = enc.encode(String(salt));
  const idB = enc.encode(String(rawId));
  const cat = new Uint8Array(saltB.length + idB.length);
  cat.set(saltB, 0);
  cat.set(idB, saltB.length);
  return sha256Bytes(cat);
}

function hexOf(bytes) {
  return [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function recordToEnvelope(record, salt) {
  let rawId = first(record, ID_KEYS, null);
  if (rawId == null) {
    const subset = {};
    for (const k of [...CLASS_KEYS, ...TS_KEYS].sort()) {
      if (k in record) subset[k] = record[k];
    }
    rawId = JSON.stringify(subset);
  }
  const digest = await identityDigest(salt, rawId);
  const hid = hexOf(digest).slice(0, HASHED_ID_HEX_LEN);
  let n64 = 0n;
  for (let i = 0; i < 8; i++) n64 = (n64 << 8n) + BigInt(digest[i]);
  const sampled = n64 % 5n === 0n;
  let ctxRaw = first(record, CONTEXT_KEYS, {});
  if (!ctxRaw || typeof ctxRaw !== "object") ctxRaw = {};
  const ctx = { ...ctxRaw };
  for (const [key, value] of Object.entries(record)) {
    if (CORE_CONSUMED.has(key) || isPiiKey(key)) continue;
    if (!(key in ctx)) ctx[key] = value;
  }
  const outcome = first(record, OUTCOME_KEYS);
  return {
    hashed_id: hid,
    timestamp: first(record, TS_KEYS) ? String(first(record, TS_KEYS)) : utcNow(),
    task_class: String(first(record, CLASS_KEYS, "unknown")),
    urgency: asUrgency(first(record, URGENCY_KEYS, 0.5)),
    context_signals: sanitizeContext(ctx),
    actual_outcome: outcome == null ? null : String(outcome),
    actual_revenue: asFloat(first(record, REVENUE_KEYS)),
    actual_cost: asFloat(first(record, COST_KEYS)),
    actual_duration: asFloat(first(record, DURATION_KEYS)),
    sampled,
  };
}

function mid(lo, hi) {
  return (lo + hi) / 2;
}

function rangeOf(values, fallback) {
  if (!values.length) {
    const [lo, hi] = fallback;
    return [lo, mid(lo, hi), hi];
  }
  return [Math.min(...values), median(values), Math.max(...values)];
}

function median(values) {
  const s = [...values].sort((a, b) => a - b);
  const midI = Math.floor(s.length / 2);
  return s.length % 2 ? s[midI] : (s[midI - 1] + s[midI]) / 2;
}

function asRange(value) {
  if (value == null) return null;
  if (Array.isArray(value) && value.length >= 2) return [Number(value[0]), Number(value[1])];
  if (typeof value === "object" && "low" in value && "high" in value) return [Number(value.low), Number(value.high)];
  if (typeof value === "number") return [value, value];
  return null;
}

function classPriors(counterfactual, taskClass) {
  let spec;
  if (counterfactual[taskClass] && typeof counterfactual[taskClass] === "object") {
    spec = { ...counterfactual[taskClass] };
  } else {
    spec = {};
    for (const key of ["duration", "cost", "revenue"]) {
      if (key in counterfactual) spec[key] = counterfactual[key];
    }
  }
  const prior = {};
  for (const key of ["duration", "cost", "revenue"]) {
    const mapped = asRange(spec[key]);
    if (mapped) prior[key] = mapped;
  }
  return Object.keys(prior).length ? { [taskClass]: prior } : {};
}

function resolveField(values, spec, fallback) {
  if (values.length) {
    const [lo, midv, hi] = rangeOf(values, fallback);
    return [lo, midv, hi, false];
  }
  if (spec != null) {
    if (Array.isArray(spec) && spec.length >= 2) {
      const lo = Number(spec[0]); const hi = Number(spec[1]);
      return [lo, mid(lo, hi), hi, false];
    }
    if (spec && typeof spec === "object" && "low" in spec && "high" in spec) {
      const lo = Number(spec.low); const hi = Number(spec.high);
      return [lo, mid(lo, hi), hi, false];
    }
  }
  return [null, null, null, true];
}

function computeExpectation({ task_class, urgency, history, class_priors }) {
  const same = (history || []).filter((h) => String(h.task_class) === String(task_class));
  const durations = same.filter((h) => h.actual_duration != null).map((h) => Number(h.actual_duration));
  const costs = same.filter((h) => h.actual_cost != null).map((h) => Number(h.actual_cost));
  const revenues = same.filter((h) => h.actual_revenue != null).map((h) => Number(h.actual_revenue));
  const prior = (class_priors || {})[task_class] || {};
  let [d_lo, d_mid, d_hi, d_unk] = resolveField(durations, prior.duration, [0, 1_000_000]);
  const [c_lo, c_mid, c_hi, c_unk] = resolveField(costs, prior.cost, [0, 1_000_000_000]);
  const [r_lo, r_mid, r_hi, r_unk] = resolveField(revenues, prior.revenue, [0, 1_000_000_000]);
  if (d_mid != null) {
    const scale = 1.1 - 0.2 * Math.max(0, Math.min(1, Number(urgency)));
    d_mid *= scale;
    if (d_lo != null) d_lo *= scale;
    if (d_hi != null) d_hi *= scale;
  }
  const unknown = d_unk && c_unk && r_unk && !same.length;
  return {
    duration: d_mid, duration_low: d_lo, duration_high: d_hi,
    cost: c_mid, cost_low: c_lo, cost_high: c_hi,
    revenue: r_mid, revenue_low: r_lo, revenue_high: r_hi,
    unknown, task_class: String(task_class), urgency: Number(urgency),
  };
}

function clip01(v) {
  if (v < 0) return 0;
  if (v > 1) return 1;
  return v;
}

function jobEfficiency(env, exp) {
  const parts = [];
  if (env.actual_duration && exp.duration && env.actual_duration > 0) {
    parts.push(clip01(exp.duration / env.actual_duration));
  }
  if (env.actual_cost && exp.cost && env.actual_cost > 0) {
    parts.push(clip01(exp.cost / env.actual_cost));
  }
  if (env.actual_revenue != null && exp.revenue && exp.revenue > 0) {
    parts.push(clip01(env.actual_revenue / exp.revenue));
  }
  if (!parts.length) return null;
  return parts.reduce((a, b) => a + b, 0) / parts.length;
}

function ledgerAdd(ledger, env, exp) {
  const actualRev = env.actual_revenue;
  const expectedRev = exp.revenue;
  if (actualRev != null && expectedRev != null) {
    const delta = actualRev - expectedRev;
    if (delta > 0) ledger.money_made += delta;
    else if (delta < 0) ledger.money_lost += -delta;
    if (actualRev < expectedRev) {
      const high = exp.revenue_high != null ? exp.revenue_high : expectedRev;
      ledger.money_left_on_table += Math.max(0, high - actualRev);
    }
  }
  const actualCost = env.actual_cost;
  const expectedCost = exp.cost;
  if (actualCost != null && expectedCost != null) {
    const overrun = actualCost - expectedCost;
    if (overrun > 0) ledger.money_lost += overrun;
  }
  const eff = jobEfficiency(env, exp);
  if (eff != null) ledger._efficiencies.push(eff);
  ledger.net_variance = ledger.money_made - ledger.money_lost;
  ledger.efficiency_score = ledger._efficiencies.length
    ? ledger._efficiencies.reduce((a, b) => a + b, 0) / ledger._efficiencies.length
    : 0;
}

function round6(n) {
  return Math.round(n * 1e6) / 1e6;
}

async function observePair(observed, counterfactual) {
  const salt = "ui-session";
  const env = await recordToEnvelope(observed, salt);
  const priors = classPriors(counterfactual, env.task_class);
  const exp = computeExpectation({
    task_class: env.task_class,
    urgency: env.urgency,
    history: [],
    class_priors: priors,
  });
  const ledger = { money_made: 0, money_lost: 0, money_left_on_table: 0, net_variance: 0, efficiency_score: 0, _efficiencies: [] };
  ledgerAdd(ledger, env, exp);
  const report = {
    observed: 1,
    sampled: 1,
    sample_rate_target: 1.0,
    sampled_hashed_ids: [env.hashed_id],
    ledger: {
      money_made: round6(ledger.money_made),
      money_lost: round6(ledger.money_lost),
      money_left_on_table: round6(ledger.money_left_on_table),
      net_variance: round6(ledger.net_variance),
      efficiency_score: round6(ledger.efficiency_score),
    },
    by_task_class: { [env.task_class]: 1 },
    notes: [
      "ShadowLock reports are anonymous aggregates.",
      "Identifiers are sha256 hex[:12] only.",
      "No person, team, or department names are emitted.",
      "Zero-retention: this API does not write KV except existing download keys.",
    ],
  };
  return {
    product: PRODUCT,
    version: VERSION,
    motto: MOTTO,
    report,
    expectation: exp,
    initiation: { task_class: env.task_class, urgency: env.urgency, context_signals: { ...env.context_signals } },
    hashed_id: env.hashed_id,
  };
}

function openapiSpec() {
  return {
    openapi: "3.1.0",
    info: {
      title: "ShadowLock runtime",
      version: VERSION,
      description: "Read-only zero-retention outcome mirror. " + MOTTO,
    },
    servers: [{ url: HOST }],
    paths: {
      
            "/v1/example": { get: { operationId: "shadowlockExample", summary: "Sample JSON payload. Does not increment downloads.", responses: { "200": { description: "OK" } } } },
      "/v1/skill": {
        get: {
          operationId: "shadowlock_skill",
          summary: "Return skill markdown. Does not increment download KV.",
          responses: { "200": { description: "markdown" } },
        },
      },
"/v1/health": {
        get: { operationId: "health", summary: "Liveness", responses: { "200": { description: "ok", content: { "application/json": { schema: { type: "object" } } } } } },
      },
      "/v1/observe": {
        post: {
          operationId: "observe",
          summary: "Observe one {observed, counterfactual} pair. Returns report JSON. Zero-retention.",
          requestBody: {
            required: true,
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  required: ["observed", "counterfactual"],
                  properties: {
                    observed: { type: "object" },
                    counterfactual: { type: "object" },
                  },
                },
              },
            },
          },
          responses: { "200": { description: "report", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
    },
  };
}

function aiHtml() {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShadowLock — use with Grok, ChatGPT, Venice</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  code { background: #151922; padding: .15rem .4rem; border-radius: 4px; }
  a { color: #c9d4ff; }
  .motto { color: #9aa3b2; font-style: italic; }
</style>
<body>
  <h1>ShadowLock live API</h1>
  <p class="motto">${MOTTO}</p>
  <p>Zero-retention: observe payloads are not stored. Download counters stay on existing KV keys only.</p>
  <h2>ChatGPT (GPT Actions)</h2>
  <p>Paste this OpenAPI URL into GPT Actions:</p>
  <p><code>${HOST}/openapi.json</code></p>
  <h2>Grok / xAI</h2>
  <p>Custom tool pointing at <code>POST ${HOST}/v1/observe</code>.</p>
  <h2>Venice</h2>
  <p>Custom HTTP tool from the same OpenAPI URL.</p>
  <h2>MCP catalog</h2>
  <p>The shared catalog (ships separately) is <code>https://aziel-runtime.vibelock.workers.dev/mcp</code>.</p>
  <p><a href="/openapi.json">openapi.json</a> · <a href="/v1/health">health</a> · <a href="/">downloads</a></p>
</body>
</html>`;
}

export async function handleRuntimeApi(request, url) {
  const path = url.pathname;
  const isApi = path === "/v1" || path.startsWith("/v1/") || path === "/openapi.json" || path === "/ai";
  if (!isApi) return null;
  try {
    if (path === "/v1/health" && request.method === "GET") {
      return json({ ok: true, author: "Aziel Eliab", product: PRODUCT, version: VERSION });
    }
  if ((path === "/v1/example" || path === "/v1/example/") && (request.method === "GET" || request.method === "HEAD")) {
    return json({
      ok: true,
      product: PRODUCT,
      author: "Aziel Eliab",
      example: EXAMPLE_PAYLOAD,
      note: "Sample payload only. Does not increment downloads.",
    });
  }

    if (path === "/v1/skill" && request.method === "GET") {
      return new Response(SKILL, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() },
      });
  }
    if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec());
    if (path === "/ai" && request.method === "GET") {
      return new Response(aiHtml(), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
    }
    if (path === "/v1/observe" && request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "JSON body required" }, 400); }
      if (!body || typeof body.observed !== "object" || body.observed == null || Array.isArray(body.observed)) {
        return json({ error: "observed must be a JSON object" }, 400);
      }
      if (!body || typeof body.counterfactual !== "object" || body.counterfactual == null || Array.isArray(body.counterfactual)) {
        return json({ error: "counterfactual must be a JSON object" }, 400);
      }
      return json(await observePair(body.observed, body.counterfactual));
    }
    return json({ error: "not found" }, 404);
  } catch (err) {
    return json({ error: String(err.message || err) }, 400);
  }
}
