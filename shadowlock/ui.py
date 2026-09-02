"""Localhost UI for ShadowLock. Binds 127.0.0.1. No CDN, no disk writes."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from shadowlock import __version__
from shadowlock.adapters import record_to_envelope
from shadowlock.counterfactual import Expectation
from shadowlock.ledger import FinancialLedger
from shadowlock.report import Report

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8764
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
MAX_BODY = 1 * 1024 * 1024

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShadowLock</title>
<style>
  :root {
    --bg: #0f1419; --panel: #171e27; --ink: #e8edf2; --muted: #8b97a6;
    --line: #2a3544; --gold: #d4bc6a; --focus: #7aa2d4; --bad: #d4534b;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Segoe UI", sans-serif; line-height: 1.45;
  }
  body { max-width: 46rem; margin: 0 auto; padding: 2.1rem 1.2rem 4rem; }
  .tag {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
  }
  h1 { font-size: 2rem; font-weight: 650; letter-spacing: 0.04em; margin: 0.35rem 0 0.25rem; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 0.85rem; font-size: 1.05rem; }
  .lede { color: var(--muted); margin: 0 0 1.5rem; max-width: 40rem; }
  fieldset {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 1.1rem 1.15rem 1.2rem; margin: 0 0 1rem;
  }
  legend {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.72rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); padding: 0 0.4rem;
  }
  label { display: block; font-size: 0.92rem; margin: 0.85rem 0 0.3rem; }
  label .kicker {
    display: block; font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.12rem;
  }
  textarea {
    width: 100%; padding: 0.55rem 0.65rem; border: 1px solid var(--line);
    border-radius: 6px; background: #10161d; color: var(--ink);
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.88rem;
  }
  textarea:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .actions { display: flex; gap: 0.65rem; flex-wrap: wrap; margin: 0 0 1.6rem; }
  button {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.65rem 1rem; border-radius: 8px;
    border: 1px solid var(--ink); background: var(--ink); color: var(--bg);
    cursor: pointer; font-weight: 650;
  }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  button.ghost { background: transparent; color: var(--ink); }
  h2 {
    font-size: 1.05rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin: 1.2rem 0 0.7rem;
  }
  .card {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 0.85rem 1rem;
  }
  dl { display: grid; grid-template-columns: 12rem 1fr; gap: 0.3rem 1rem; margin: 0; }
  dt { color: var(--muted); }
  pre {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.8rem;
    white-space: pre-wrap; word-break: break-word; margin: 0;
  }
  .err { color: var(--bad); }
  footer { margin-top: 2rem; color: var(--muted); font-size: 0.88rem; }
  .foot-note { font-style: italic; }
</style>
</head>
<body>
  <header>
    <div class="tag">ShadowLock · __VERSION__ · loopback · zero-retention</div>
    <h1>ShadowLock</h1>
    <p class="motto">Change is optional. Truth is not.</p>
    <p class="lede">
      Paste an observed outcome and a counterfactual prior. The mirror reports
      anonymous aggregates and forgets the payloads. Nothing is written to disk.
      This is not a dispatcher, optimizer, or scheduler. Bound to 127.0.0.1 only.
    </p>
  </header>

  <form id="mirror-form" autocomplete="off">
    <fieldset>
      <legend>Mirror</legend>
      <label for="observed">
        <span class="kicker">Observed outcome</span>
        JSON object: task_class, urgency, actual_duration, actual_cost, actual_revenue, actual_outcome.
      </label>
      <textarea id="observed" rows="8" placeholder='{"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"}'></textarea>
      <label for="counterfactual">
        <span class="kicker">Counterfactual</span>
        JSON prior for the class: duration / cost / revenue as [low, high] or a midpoint.
      </label>
      <textarea id="counterfactual" rows="6" placeholder='{"duration":[25,45],"cost":[70,110],"revenue":[180,260]}'></textarea>
    </fieldset>
    <div class="actions">
      <button type="submit" id="run">Show report</button>
      <label class="ghost">Import JSON file <input type="file" id="import-json" accept="application/json,.json"></label>
      <button type="button" class="ghost" id="export" disabled>Export JSON report</button>
    </div>
  </form>

  <section id="result" hidden>
    <h2>Read-only report</h2>
    <div class="card">
      <dl id="summary"></dl>
    </div>
    <h2>JSON</h2>
    <div class="card"><pre id="json"></pre></div>
  </section>
  <p class="err" id="err" hidden></p>

  <footer>
    <p>Apache-2.0 · Aziel Eliab · July 2026 · Bound to 127.0.0.1 · <code>shadowlock ui</code></p>
    <p class="foot-note">Zero-retention: uploads stay in this process and are not written to disk.</p>
  </footer>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  let last = null;
  function fail(msg) { $("err").hidden = false; $("err").textContent = msg; }
  $("mirror-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    $("err").hidden = true;
    $("run").disabled = true;
    try {
      const res = await fetch("/api/observe", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          observed: JSON.parse($("observed").value || "{}"),
          counterfactual: JSON.parse($("counterfactual").value || "{}"),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
      last = data;
      $("result").hidden = false;
      const r = data.report || {};
      const L = r.ledger || {};
      $("summary").innerHTML =
        "<dt>observed</dt><dd>" + (r.observed ?? "—") + "</dd>" +
        "<dt>sampled</dt><dd>" + (r.sampled ?? "—") + "</dd>" +
        "<dt>money made</dt><dd>" + (L.money_made ?? "—") + "</dd>" +
        "<dt>money lost</dt><dd>" + (L.money_lost ?? "—") + "</dd>" +
        "<dt>left on table</dt><dd>" + (L.money_left_on_table ?? "—") + "</dd>" +
        "<dt>net variance</dt><dd>" + (L.net_variance ?? "—") + "</dd>" +
        "<dt>efficiency</dt><dd>" + (L.efficiency_score ?? "—") + "</dd>";
      $("json").textContent = JSON.stringify(data, null, 2);
      $("export").disabled = false;
    } catch (e) { fail(String(e.message || e)); }
    finally { $("run").disabled = false; }
  });
  const importEl = $("import-json");
  if (importEl) importEl.addEventListener("change", () => {
    const f = importEl.files && importEl.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      let obj;
      try { obj = JSON.parse(String(reader.result || "{}")); } catch (e) { fail("invalid JSON"); return; }
      const observed = obj.observed || obj;
      const counterfactual = obj.counterfactual || {};
      $("observed").value = JSON.stringify(observed, null, 2);
      if (Object.keys(counterfactual).length) $("counterfactual").value = JSON.stringify(counterfactual, null, 2);
    };
    reader.readAsText(f);
  });
  $("export").addEventListener("click", () => {
    if (!last) return;
    const blob = new Blob([JSON.stringify(last, null, 2)], {type: "application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "shadowlock-report.json";
    a.click();
    URL.revokeObjectURL(a.href);
  });
})();
</script>
</body>
</html>
""".replace("__VERSION__", __version__)


def _as_range(value: Any) -> Any:
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return [float(value[0]), float(value[1])]
    if isinstance(value, dict) and "low" in value and "high" in value:
        return {"low": float(value["low"]), "high": float(value["high"])}
    if isinstance(value, (int, float)):
        n = float(value)
        return [n, n]
    return None


def _class_priors(counterfactual: dict[str, Any], task_class: str) -> dict[str, Any]:
    if task_class in counterfactual and isinstance(counterfactual[task_class], dict):
        spec = dict(counterfactual[task_class])
    else:
        spec = {
            key: counterfactual[key]
            for key in ("duration", "cost", "revenue")
            if key in counterfactual
        }
    prior: dict[str, Any] = {}
    for key in ("duration", "cost", "revenue"):
        mapped = _as_range(spec.get(key))
        if mapped is not None:
            prior[key] = mapped
    return {task_class: prior} if prior else {}


def _observe_pair(observed: dict[str, Any], counterfactual: dict[str, Any]) -> dict[str, Any]:
    env = record_to_envelope(observed, salt="ui-session")
    priors = _class_priors(counterfactual, env.task_class)
    exp = Expectation.compute(
        task_class=env.task_class,
        urgency=env.urgency,
        context_signals=env.context_signals,
        class_priors=priors,
    )
    ledger = FinancialLedger()
    ledger.add(env, exp)
    report = Report(
        observed=1,
        sampled=1,
        sample_rate=1.0,
        hashed_ids=[env.hashed_id],
        ledger=ledger,
        by_task_class={env.task_class: 1},
        notes=[
            "ShadowLock reports are anonymous aggregates.",
            "Identifiers are sha256 hex[:12] only.",
            "No person, team, or department names are emitted.",
            "UI path: a single pasted pair, processed in memory, not written to disk.",
        ],
    )
    return {
        "report": report.to_dict(),
        "expectation": asdict(exp),
        "initiation": env.initiation_fields(),
        "hashed_id": env.hashed_id,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: Any) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ValueError("payload too large")
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._json(200, {"ok": True, "bind_host": DEFAULT_HOST, "name": "ShadowLock"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/observe":
            self._json(404, {"error": "not found"})
            return
        try:
            body = self._read_json()
            observed = body.get("observed")
            counterfactual = body.get("counterfactual")
            if not isinstance(observed, dict):
                self._json(400, {"error": "observed must be a JSON object"})
                return
            if not isinstance(counterfactual, dict):
                self._json(400, {"error": "counterfactual must be a JSON object"})
                return
            self._json(200, _observe_pair(observed, counterfactual))
        except Exception as exc:  # noqa: BLE001
            self._json(400, {"error": str(exc)})


def make_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError("ShadowLock UI binds loopback only (127.0.0.1)")
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host, port)
    sys.stdout.write(f"ShadowLock UI  http://{host}:{port}/\n")
    sys.stdout.write("Local only. Zero-retention: payloads are not written to disk.\n")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nstopped\n")
    finally:
        httpd.server_close()
