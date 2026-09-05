---
name: ShadowLock
description: Use when calling ShadowLock hosted /v1 or installing the local package. OS-hooks into AZ-OS for process/job observation under ethics policy. Author Aziel Eliab.
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
- `POST /v1/observe` — observe `{observed, counterfactual}` or `{jobs}`
- `POST /v1/hook` — ethics-gated AZ-OS hook frame
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill
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

Then open http://127.0.0.1:8764 (loopback only). Tap **Import JSON file** or **Attach via AZ-OS**, then **Export JSON report**. AZ-OS control surface: http://127.0.0.1:8800 (`azos ui`).

Counted download (gzip HTTP 200, no 302): https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/shadowlock

Cite: Eliab, Aziel. (2026). ShadowLock 0.2.0 [Software]. Apache-2.0. https://github.com/AzielEliab/shadowlock
Historical DOI https://doi.org/10.5281/zenodo.21435707 is tombstoned. Software deposit needed. No DOI invented. Apache-2.0. Forks welcome.
