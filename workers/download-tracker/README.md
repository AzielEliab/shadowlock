# ShadowLock download tracker (Cloudflare Worker)

Counts GitHub-release downloads for ShadowLock across the canonical
repository, other branches, and forks. Forks are identified by GitHub
`owner/repo`.

**This worker must be deployed** before
`https://shadowlock-download-tracker.vibelock.workers.dev` resolves.
Until then, send people to
[GitHub Releases](https://github.com/AzielEliab/shadowlock/releases).

No secrets belong in this directory. The KV namespace id in
`wrangler.toml` is the placeholder `REPLACE_ME` until you create a
namespace.

ShadowLock is a read-only outcome mirror. Change is optional. Truth is
not.

## Bindings

| Binding     | Type | Purpose |
|-------------|------|---------|
| `DOWNLOADS` | KV   | Counters keyed `project|owner|repo|branch|fork` |

## Deploy

```bash
cd workers/download-tracker

# 1. Log in once (opens a browser; token stays in wrangler, not in git)
npx wrangler login

# 2. Create the KV namespace. Paste the id into wrangler.toml
#    replacing REPLACE_ME. Binding name MUST stay DOWNLOADS.
npx wrangler kv namespace create DOWNLOADS

# 3. Deploy
npx wrangler deploy
```

The `workers.dev` subdomain wrangler prints
(`shadowlock-download-tracker.<account>.workers.dev`) is enough until
custom DNS is ready. This tree documents the intended public URL
`https://shadowlock-download-tracker.vibelock.workers.dev`.

Do not deploy from this tree until KV is a real id.

## Routes

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Index page with the GitHub Releases link |
| GET | `/download?repo=&tag=&asset=` | Increment KV, 302 to the hosted asset (default: releases page) |
| GET | `/stats` | JSON totals plus per-repo and per-branch breakdown |
| POST | `/event` | A fork reports a download |

Query params on `/download`: `owner`, `repo` (`AzielEliab/shadowlock` is
accepted), `branch`, `fork` (`1` or `owner/repo`), `tag`, `asset`.

Default redirect with no asset:

```
https://github.com/AzielEliab/shadowlock/releases
```

Tracked asset URL (after deploy):

```
https://shadowlock-download-tracker.vibelock.workers.dev/download?repo=AzielEliab/shadowlock&tag=latest&asset=shadowlock-0.1.0.tar.gz
```

A fork reports its own download:

```bash
curl -X POST https://shadowlock-download-tracker.vibelock.workers.dev/event \
  -H "content-type: application/json" \
  -d '{
    "owner": "YourFork",
    "repo": "shadowlock",
    "branch": "main",
    "fork": "1",
    "asset": "shadowlock-0.1.0.tar.gz"
  }'
```

`fork=1` or `fork=YourFork/shadowlock`. If `owner/repo` is not
`AzielEliab/shadowlock`, the worker records `fork=1` automatically.

## Stats

`GET /stats` returns `total`, `by_repo`, `by_branch`, `by_fork`, and a
`breakdown` array so forks can read aggregates.

## CORS

All responses include `Access-Control-Allow-Origin: *`.
