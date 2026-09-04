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
    --ok: #7dcea0;
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
  .lede { color: var(--muted); margin: 0 0 1.1rem; max-width: 40rem; }
  .limit { color: var(--gold); margin: 0 0 1.4rem; font-size: 0.95rem; }
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
  textarea, input[type=file] {
    width: 100%; padding: 0.55rem 0.65rem; border: 1px solid var(--line);
    border-radius: 6px; background: #10161d; color: var(--ink);
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.88rem;
  }
  textarea:focus { outline: 2px solid var(--focus); outline-offset: 1px; }
  .actions { display: flex; gap: 0.65rem; flex-wrap: wrap; margin: 0.4rem 0 1.2rem; }
  button {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.85rem;
    letter-spacing: 0.04em; padding: 0.65rem 1rem; border-radius: 8px;
    border: 1px solid var(--ink); background: var(--ink); color: var(--bg);
    cursor: pointer; font-weight: 650;
  }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  button.ghost { background: transparent; color: var(--ink); }
  .addfile {
    display: flex; align-items: center; justify-content: center; text-align: center;
    width: 100%; min-height: 7.2rem; font-size: 1.55rem; font-weight: 700;
    letter-spacing: 0.02em; border: 2px dashed var(--gold); background: #1a160c;
    color: var(--ink); border-radius: 14px; cursor: pointer; margin: 0.2rem 0 0.7rem;
  }
  .addfile:hover { filter: brightness(1.08); }
  .views { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; overflow: hidden; margin: 0 0 1rem; }
  .views button { border: 0; border-radius: 0; padding: 0.35rem 0.9rem; background: transparent; color: var(--muted); }
  .views button.on { background: var(--gold); color: #14110a; font-weight: 650; }
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
  .plain { font-size: 1.15rem; margin: 0 0 0.7rem; }
  .err { color: var(--bad); }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0,0,0,0); border: 0; }
  .hidden { display: none; }
  footer { margin-top: 2rem; color: var(--muted); font-size: 0.88rem; }
  .foot-note { font-style: italic; }
</style>
</head>
<body>
  <header>
    <div class="tag">ShadowLock · __VERSION__ · Aziel Eliab · loopback · zero-retention</div>
    <h1>ShadowLock</h1>
    <p class="motto">Change is optional. Truth is not.</p>
    <p class="lede">
      Import a job file you already have, or attach via AZ-OS.
      The page compares it to a guess, shows money made / lost / left on
      the table, and forgets the file. Bound to 127.0.0.1 only. Nothing
      is written to disk.
    </p>
    <p class="limit">OS-hooks into AZ-OS for process/job observation under ethics policy. This is a comparison, not a dispatcher, optimizer, scheduler, or truth score.</p>
  </header>

  <form id="mirror-form" autocomplete="off">
    <fieldset>
      <legend>Import</legend>
      <p class="lede" style="margin-bottom:0.4rem">Tap the big button to pick a JSON file. Paste is optional.</p>
      <input id="import-json" class="sr-only" type="file" accept="application/json,.json">
      <button class="addfile" id="import-btn" type="button">Import JSON file</button>
      <label for="observed">
        <span class="kicker">Observed outcome (or paste)</span>
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
      <button type="button" class="ghost" id="attach">Attach via AZ-OS</button>
      <button type="button" class="ghost" id="sample">Load sample</button>
      <button type="button" class="ghost" id="export" disabled>Export JSON report</button>
    </div>
  </form>

  <section id="result" hidden>
    <h2>View</h2>
    <div class="views" role="group" aria-label="Simple or advanced">
      <button type="button" id="view-simple" class="on">Simple</button>
      <button type="button" id="view-advanced">Advanced</button>
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

  <footer>
    <p>Apache-2.0 · Aziel Eliab · July 2026 · Bound to 127.0.0.1 · <code>shadowlock ui</code></p>
    <p class="foot-note">Zero-retention: uploads stay in this process and are not written to disk. AZ-OS hook is ethics-gated observation, not process control.</p>
  </footer>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  let last = null;
  let view = "simple";
  const SAMPLE_OBS = {"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"};
  const SAMPLE_CF = {"duration":[25,45],"cost":[70,110],"revenue":[180,260]};
  function fail(msg) { $("err").hidden = false; $("err").textContent = msg; }
  function setView(name) {
    view = name;
    $("view-simple").classList.toggle("on", name === "simple");
    $("view-advanced").classList.toggle("on", name === "advanced");
    $("advanced").classList.toggle("hidden", name !== "advanced");
  }
  $("view-simple").addEventListener("click", () => setView("simple"));
  $("view-advanced").addEventListener("click", () => setView("advanced"));
  function render(data) {
    last = data;
    $("result").hidden = false;
    const r = data.report || {};
    const L = r.ledger || {};
    $("plain").textContent = "Compared this job to a guess. Names are dropped. Nothing is saved.";
    $("summary").innerHTML =
      "<dt>jobs looked at</dt><dd>" + (r.observed ?? "—") + "</dd>" +
      "<dt>jobs sampled</dt><dd>" + (r.sampled ?? "—") + "</dd>" +
      "<dt>money made</dt><dd>" + (L.money_made ?? "—") + "</dd>" +
      "<dt>money lost</dt><dd>" + (L.money_lost ?? "—") + "</dd>" +
      "<dt>left on the table</dt><dd>" + (L.money_left_on_table ?? "—") + "</dd>" +
      "<dt>net gap</dt><dd>" + (L.net_variance ?? "—") + "</dd>";
    $("json").textContent = JSON.stringify(data, null, 2);
    $("export").disabled = false;
    setView(view);
  }
  async function runMirror(observed, counterfactual) {
    $("err").hidden = true;
    $("run").disabled = true;
    try {
      const res = await fetch("/api/observe", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ observed: observed, counterfactual: counterfactual }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
      render(data);
    } catch (e) { fail(String(e.message || e)); }
    finally { $("run").disabled = false; }
  }
  $("mirror-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    let observed, counterfactual;
    try {
      observed = JSON.parse($("observed").value || "{}");
      counterfactual = JSON.parse($("counterfactual").value || "{}");
    } catch (e) { fail("That JSON is not valid."); return; }
    await runMirror(observed, counterfactual);
  });
  $("import-btn").addEventListener("click", () => $("import-json").click());
  $("import-json").addEventListener("change", () => {
    const f = $("import-json").files && $("import-json").files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      let obj;
      try { obj = JSON.parse(String(reader.result || "{}")); } catch (e) { fail("That file is not valid JSON."); return; }
      const observed = obj.observed || obj.payload && obj.payload.observed || obj;
      const counterfactual = obj.counterfactual || (obj.payload && obj.payload.counterfactual) || {};
      $("observed").value = JSON.stringify(observed, null, 2);
      if (counterfactual && typeof counterfactual === "object" && Object.keys(counterfactual).length) {
        $("counterfactual").value = JSON.stringify(counterfactual, null, 2);
      }
      runMirror(observed, counterfactual);
    };
    reader.readAsText(f);
  });
  $("attach").addEventListener("click", async () => {
    $("err").hidden = true;
    $("attach").disabled = true;
    let observed = {}, counterfactual = {};
    try {
      observed = JSON.parse($("observed").value || "{}");
      counterfactual = JSON.parse($("counterfactual").value || "{}");
    } catch (e) { observed = {}; counterfactual = {}; }
    try {
      const body = { ethics: { actor: "operator" } };
      if (observed && typeof observed === "object" && Object.keys(observed).length) {
        body.jobs = [observed];
        body.counterfactual = counterfactual;
      }
      const res = await fetch("/api/attach", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
      if (data.report) render(data);
      else {
        $("result").hidden = false;
        $("plain").textContent = data.attached
          ? "Attached via AZ-OS. Ethics passed. No jobs sampled yet."
          : "AZ-OS attach did not complete.";
        $("summary").innerHTML =
          "<dt>attached</dt><dd>" + (data.attached ? "yes" : "no") + "</dd>" +
          "<dt>protocol</dt><dd>" + (data.protocol || "—") + "</dd>" +
          "<dt>ethics</dt><dd>" + ((data.ethics && data.ethics.passed) ? "passed" : "refused") + "</dd>";
        $("json").textContent = JSON.stringify(data, null, 2);
        last = data;
        $("export").disabled = false;
      }
    } catch (e) { fail(String(e.message || e)); }
    finally { $("attach").disabled = false; }
  });
  $("sample").addEventListener("click", () => {
    $("observed").value = JSON.stringify(SAMPLE_OBS, null, 2);
    $("counterfactual").value = JSON.stringify(SAMPLE_CF, null, 2);
    runMirror(SAMPLE_OBS, SAMPLE_CF);
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
            "UI path: a single imported or pasted pair, processed in memory, not written to disk.",
        ],
    )
    return {
        "report": report.to_dict(),
        "expectation": asdict(exp),
        "initiation": env.initiation_fields(),
        "hashed_id": env.hashed_id,
        "author": "Aziel Eliab",
        "product": "ShadowLock",
        "version": __version__,
        "azos_hook": True,
    }


def _handle_hook(body: dict[str, Any]) -> dict[str, Any]:
    """Ethics-gated AZ-OS attach on loopback. Optional jobs in the body."""
    from shadowlock.azos_hook import LocalObserver, records_from_frame
    from shadowlock.errors import EthicsError, HookError

    ethics = body.get("ethics") if isinstance(body.get("ethics"), dict) else None
    jobs = records_from_frame(body)
    host = str(body.get("host") or "127.0.0.1")
    port = int(body.get("port") or 8800)
    live = bool(body.get("live", True))
    observer = LocalObserver(host=host, port=port)
    try:
        receipt = observer.attach(ethics=ethics, extra_jobs=jobs, live=live)
    except (EthicsError, HookError) as exc:
        return {
            "ok": False,
            "attached": False,
            "error": str(exc),
            "author": "Aziel Eliab",
            "product": "ShadowLock",
            "version": __version__,
            "azos_hook": True,
        }
    out = receipt.as_dict()
    out["version"] = __version__
    if receipt.jobs:
        observed = receipt.jobs[0]
        counterfactual = body.get("counterfactual") if isinstance(body.get("counterfactual"), dict) else {}
        paired = _observe_pair(observed, counterfactual)
        out.update(paired)
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _loopback_ok(self) -> bool:
        peer = self.client_address[0] if self.client_address else ""
        host = (self.headers.get("Host") or "").split(":")[0].strip()
        if peer not in LOOPBACK:
            return False
        if host and host not in LOOPBACK:
            return False
        return True

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
        if not self._loopback_ok():
            self._json(403, {"error": "loopback only"})
            return
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._json(
                200,
                {
                    "ok": True,
                    "bind_host": DEFAULT_HOST,
                    "name": "ShadowLock",
                    "author": "Aziel Eliab",
                    "azos_hook": True,
                    "ethics": "Integrity precedes execution.",
                    "version": __version__,
                },
            )
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self._loopback_ok():
            self._json(403, {"error": "loopback only"})
            return
        path = urlparse(self.path).path
        if path == "/api/observe":
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
            return
        if path in ("/api/attach", "/api/hook"):
            try:
                self._json(200, _handle_hook(self._read_json()))
            except Exception as exc:  # noqa: BLE001
                self._json(400, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})


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
