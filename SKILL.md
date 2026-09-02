---
name: ShadowLock
description: Use when calling ShadowLock hosted /v1 or installing the local package. Author Aziel Eliab.
---

# ShadowLock

Looks at jobs you already have. Read-only. Zero retention. Author: **Aziel Eliab**.

**THIS IS:** a read-only, zero-retention outcome mirror for operational decisions.

**THIS IS NOT:** a dispatcher, optimizer, scheduler, predictor, people profiler, or truth score. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill
```

## Local (after one-click install)

```bash
curl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash
shadowlock ui
shadowlock doctor --verify
```

Then open http://127.0.0.1:8764 (loopback only). Tap **Import JSON file**, then **Export JSON report**.

Counted download (gzip HTTP 200, no 302): https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/shadowlock

Paper: DOI https://doi.org/10.5281/zenodo.21435707 · https://zenodo.org/records/21435707 · Apache-2.0. Forks welcome.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Zero-retention observation of a job list you already have. No OS hook.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/shadowlock/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://shadowlock-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `shadowlock doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.
