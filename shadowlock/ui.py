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
    color-scheme: light dark;
    --bg: #f7f4ec; --panel: #fffdf8; --ink: #1c1914; --muted: #4e483f;
    --line: #ddd4c2; --gold: #c9a227; --focus: #c9a227; --bad: #8f2d2d;
    --ok: #1d6b42; --field: #fffdf8;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #12110e; --panel: #1c1b17; --ink: #f4efe4; --muted: #c8bba6;
      --line: #3d382e; --gold: #c9a227; --focus: #c9a227; --bad: #f0a8a2;
      --ok: #9ddebe; --field: #14130f;
    }
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.5;
  }
  body { max-width: 40rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }
  .top {
    display: flex; justify-content: space-between; align-items: baseline;
    gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.75rem;
  }
  .brand { font-weight: 650; letter-spacing: 0.01em; }
  .meta { color: var(--muted); font-size: 0.92rem; }
  h1 { font-size: 1.85rem; font-weight: 650; margin: 0 0 0.45rem; line-height: 1.2; }
  .lede { margin: 0 0 1.25rem; max-width: 36rem; font-size: 1.05rem; }
  .hint { color: var(--muted); margin: 0.85rem 0 1.4rem; }
  code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.92em; }
  label { display: block; font-size: 0.95rem; margin: 0.9rem 0 0.35rem; }
  textarea {
    width: 100%; max-width: 100%; padding: 0.6rem 0.7rem; border: 1px solid var(--line);
    border-radius: 8px; background: var(--field); color: var(--ink);
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.88rem;
  }
  button, summary {
    font: inherit;
  }
  button {
    padding: 0.7rem 1.05rem; border-radius: 8px; border: 1px solid var(--ink);
    background: var(--ink); color: var(--bg); cursor: pointer; font-weight: 650;
  }
  button:disabled { opacity: 0.45; cursor: not-allowed; }
  button.primary { min-height: 2.75rem; }
  button.ghost { background: transparent; color: var(--ink); border-color: var(--line); font-weight: 550; }
  button:focus-visible, summary:focus-visible, textarea:focus-visible, a:focus-visible, input:focus-visible {
    outline: 3px solid var(--focus); outline-offset: 2px;
  }
  .actions { display: flex; gap: 0.6rem; flex-wrap: wrap; margin: 1rem 0 0.4rem; }
  details {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 0.75rem 1rem; margin: 0 0 0.8rem;
  }
  summary { cursor: pointer; font-weight: 650; }
  h2 { font-size: 1.15rem; font-weight: 650; margin: 0 0 0.7rem; }
  .card {
    border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
    padding: 1rem 1.05rem;
  }
  dl { display: grid; grid-template-columns: 11rem 1fr; gap: 0.35rem 1rem; margin: 0; }
  dt { color: var(--muted); }
  dd { margin: 0; }
  pre {
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.8rem;
    white-space: pre-wrap; overflow-wrap: anywhere; margin: 0.6rem 0 0;
  }
  .plain { font-size: 1.05rem; margin: 0 0 0.8rem; }
  .err { color: var(--bad); margin: 0.6rem 0 0; }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0,0,0,0); border: 0; }
  footer { margin-top: 1.6rem; color: var(--muted); font-size: 0.9rem; }
  @media (max-width: 480px) {
    body { padding: 1.1rem 0.9rem 2.4rem; }
    h1 { font-size: 1.55rem; }
    button, .actions button { width: 100%; }
    .actions { flex-direction: column; }
    dl { grid-template-columns: 1fr; gap: 0.1rem; }
    dd { margin-bottom: 0.65rem; }
  }
</style>
</head>
<body>
  <header class="top">
    <span class="brand">ShadowLock</span>
    <span class="meta">Aziel Eliab</span>
  </header>
  <main>
    <h1>Compare a finished job</h1>
    <p class="lede">ShadowLock compares a job you already finished to a guess, then forgets the file.</p>
    <input id="import-json" class="sr-only" type="file" accept="application/json,.json">
    <button class="primary" id="import-btn" type="button">Import JSON file</button>
    <p class="hint">Optional check in a terminal: <code>shadowlock doctor</code></p>
    <p class="err" id="err" hidden></p>

    <section id="result" hidden>
      <h2>Simple summary</h2>
      <div class="card">
        <p class="plain" id="plain"></p>
        <dl id="summary"></dl>
      </div>
    </section>

    <details id="advanced-panel">
      <summary>Advanced</summary>
      <form id="mirror-form" autocomplete="off">
        <label for="observed">Job JSON</label>
        <textarea id="observed" rows="7" placeholder='{"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"}'></textarea>
        <label for="counterfactual">Guess (duration, cost, revenue)</label>
        <textarea id="counterfactual" rows="5" placeholder='{"duration":[25,45],"cost":[70,110],"revenue":[180,260]}'></textarea>
        <div class="actions">
          <button type="submit" id="run">Show report</button>
          <button type="button" class="ghost" id="attach">Attach via AZ-OS</button>
          <button type="button" class="ghost" id="sample">Load sample</button>
          <button type="button" class="ghost" id="export" disabled>Export JSON report</button>
        </div>
        <h2>JSON</h2>
        <pre id="json"></pre>
      </form>
    </details>

    <details>
      <summary>About</summary>
      <p>Version __VERSION__. ShadowLock reads a job you already have, compares it with a guess, and drops what it read. It can attach to AZ-OS on this computer when the ethics check passes. Bound to 127.0.0.1. Uploads stay in this process and are not written to disk.</p>
      <p>Author: Aziel Eliab.</p>
    </details>
  </main>
  <footer>
    <p>Aziel Eliab · 127.0.0.1 · <code>shadowlock ui</code></p>
  </footer>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  let last = null;
  const SAMPLE_OBS = {"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"};
  const SAMPLE_CF = {"duration":[25,45],"cost":[70,110],"revenue":[180,260]};
  function fail(msg) { $("err").hidden = false; $("err").textContent = msg; }
  function render(data) {
    last = data;
    $("result").hidden = false;
    const r = data.report || {};
    const L = r.ledger || {};
    $("plain").textContent = "Compared this job to a guess. Names are left out. Nothing is saved.";
    $("summary").innerHTML =
      "<dt>Jobs looked at</dt><dd>" + (r.observed ?? "—") + "</dd>" +
      "<dt>Jobs sampled</dt><dd>" + (r.sampled ?? "—") + "</dd>" +
      "<dt>Money made</dt><dd>" + (L.money_made ?? "—") + "</dd>" +
      "<dt>Money lost</dt><dd>" + (L.money_lost ?? "—") + "</dd>" +
      "<dt>Left on the table</dt><dd>" + (L.money_left_on_table ?? "—") + "</dd>" +
      "<dt>Net gap</dt><dd>" + (L.net_variance ?? "—") + "</dd>";
    $("json").textContent = JSON.stringify(data, null, 2);
    $("export").disabled = false;
    if ($("result").scrollIntoView) $("result").scrollIntoView({block: "nearest"});
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
    } catch (e) { fail("That JSON is not valid. Check the braces, then try Show report again."); return; }
    await runMirror(observed, counterfactual);
  });
  $("import-btn").addEventListener("click", () => $("import-json").click());
  $("import-json").addEventListener("change", () => {
    const f = $("import-json").files && $("import-json").files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      let obj;
      try { obj = JSON.parse(String(reader.result || "{}")); } catch (e) { fail("That file is not valid JSON. Pick another JSON file."); return; }
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
      if (!res.ok || (data.error && !data.report)) {
        throw new Error((data.error || ("HTTP " + res.status)) + " Next: shadowlock doctor");
      }
      if (data.report) render(data);
      else {
        $("result").hidden = false;
        $("plain").textContent = data.attached
          ? "Attached to AZ-OS. The ethics check passed. No jobs sampled yet."
          : "AZ-OS attach did not complete. Open Advanced and try again, or run shadowlock doctor.";
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


def _health_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "bind_host": DEFAULT_HOST,
        "name": "ShadowLock",
        "author": "Aziel Eliab",
        "azos_hook": True,
        "ethics": "Integrity precedes execution.",
        "version": __version__,
    }


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
            accept = self.headers.get("Accept") or ""
            if "application/json" in accept and "text/html" not in accept:
                self._json(200, _health_payload())
                return
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            self._json(200, _health_payload())
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


def open_line(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"Open http://{host}:{port}/\n"


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host, port)
    sys.stdout.write(open_line(host, port))
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\nstopped\n")
    finally:
        httpd.server_close()
