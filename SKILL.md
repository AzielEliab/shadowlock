---
name: ShadowLock
description: Use when calling ShadowLock hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (qnm-node + aziel-runtime). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. OS-hooks into AZ-OS for process/job observation under ethics policy. Author Aziel Eliab.
---

# ShadowLock

Looks at jobs you already have. Read-only. Zero retention. OS-hooks into **AZ-OS** under ethics policy. Author: **Aziel Eliab**.

**THIS IS:** a read-only, zero-retention outcome mirror that attaches to AZ-OS for process/job observation.

**THIS IS NOT:** a dispatcher, optimizer, scheduler, predictor, people profiler, truth score, kernel hook, or process controller. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill`
- Hosted product UI: `GET https://shadowlock-download-tracker.vibelock.workers.dev/` (observe workspace + counted download)

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness (includes `azos_hook`)
- `GET /v1/skill` — this file
- `GET /v1/mesh` — PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer cross-map (not Softwares-tab; no public qnsd proxy). Never enables.
- `GET /v1/mesh/nodes` — PROXY Live Nodes roster (5-minute presence). Peers see the QNS-CD-1.0 cross-map.
- `POST /v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` — PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path.
- `POST /v1/observe` — observe `{observed, counterfactual}` or `{jobs}`
- `POST /v1/hook` — ethics-gated AZ-OS hook frame
- Product POSTs listed in OpenAPI

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. OpenAPI: import as a GPT Action, custom tool, or HTTP tool. MCP: POST the catalog `/mcp` endpoint for Cursor, Glama, Claude, and other MCP clients.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/mesh
curl -s -A 'Mozilla/5.0' -X POST https://shadowlock-download-tracker.vibelock.workers.dev/v1/hook \
  -H 'content-type: application/json' \
  -d '{"jobs":[{"id":"job-1","task_class":"repair","actual_outcome":"complete"}]}'
```

## Local (after one-click install)

```bash
curl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash
shadowlock ui
shadowlock attach
shadowlock doctor --verify
```

Then open http://127.0.0.1:8764 (loopback only). Tap **Import JSON file** or **Attach via AZ-OS**, then **Export JSON report**. AZ-OS control surface: http://127.0.0.1:8800 (`azos ui`). Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). QNS-CD-1.0 cites [qnm-node](https://github.com/AzielEliab/qnm-node) and [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody is [AZInterface](https://github.com/AzielEliab/azinterface).

Counted download (gzip HTTP 200, no 302): https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/shadowlock

Cite: Eliab, Aziel. (2026). ShadowLock 0.2.0 [Software]. Apache-2.0. https://github.com/AzielEliab/shadowlock
Historical DOI https://doi.org/10.5281/zenodo.21435707 is tombstoned. Software deposit needed. No DOI invented. Apache-2.0. Forks welcome.
