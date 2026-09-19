# shadowlock download tracker

Isolated Worker `shadowlock-download-tracker`. Project `shadowlock`.
KV namespace `SHADOWLOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the **product UI** (observe workspace + counted download). Increments a **page-view** counter (separate from downloads).
GET `/count` returns `{project, views, downloads, total}` (does not increment).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME` / `https://aziel-runtime.vibelock.workers.dev`). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 (photon QNS1 packet transfer) is a hub cite / Worker mesh cross-map only — not a Softwares-tab product, not a public qnsd proxy. Local qnsd lives in https://github.com/AzielEliab/qnm-node. Runtime cites + catalog field live in https://github.com/AzielEliab/aziel-runtime. Pair custody: https://github.com/AzielEliab/azinterface. No Node Gate. No auto-heal. Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`.

Verify: `curl -sS -A 'Mozilla/5.0' https://shadowlock-download-tracker.vibelock.workers.dev/v1/mesh/status` returns MESH-OK style JSON with `enabled: false` by default.
POST `/v1/observe` accepts `{observed, counterfactual}` or `{jobs}`. Does not increment.
POST `/v1/hook` is an ethics-gated AZ-OS hook frame. Does not increment views or downloads.
GET `/cite.json` `/robots.txt` `/sitemap.xml` `/llms.txt` `/sigil.png` — SEO + cite + official sigil.

Host: https://shadowlock-download-tracker.vibelock.workers.dev

## Human / bot schema (`/stats` and `/count`)

Additive dual-count (Whitestone canary). Classification lives in `src/classify.js`
and response shaping in `src/stats-shape.js`.

Invariant: `views === views_human + views_bot` and
`downloads === downloads_human + downloads_bot`.

Legacy strategy (b): existing KV totals are never reset. Pre-split remainder
is shown as bot on read (`views_bot = views - views_human`). Author: Aziel Eliab only.

