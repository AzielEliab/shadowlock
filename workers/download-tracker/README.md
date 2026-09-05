# shadowlock download tracker

Isolated Worker `shadowlock-download-tracker`. Project `shadowlock`.
KV namespace `SHADOWLOCK_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the **product UI** (observe workspace + counted download). Increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
POST `/v1/observe` accepts `{observed, counterfactual}` or `{jobs}`. Does not increment.
POST `/v1/hook` is an ethics-gated AZ-OS hook frame. Does not increment views or downloads.
GET `/cite.json` `/robots.txt` `/sitemap.xml` `/llms.txt` `/sigil.png` — SEO + cite + Everblooming sigil.

Host: https://shadowlock-download-tracker.vibelock.workers.dev
