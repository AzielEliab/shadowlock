# ShadowLock

A universal, read-only, zero-retention outcome mirror for operational
decision systems.

**Author:** Aziel Eliab
**Date:** July 2026
**License:** [Apache-2.0](LICENSE)

> Change is optional. Truth is not.

See the spec: [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

ShadowLock is **not** a dispatcher, optimizer, scheduler, or learning
system. It does not write back to the host. It observes selectively
(1 in 5), computes a counterfactual expectation from initiation fields,
reports anonymous financial variance, and forgets everything.

---

## Download

**Hosted (Cloudflare Worker, counted across branches and forks):**

# → [https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.1.0.tar.gz](https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.1.0.tar.gz) ←

Direct file: [shadowlock-0.1.0.tar.gz](https://shadowlock-download-tracker.vibelock.workers.dev/shadowlock-0.1.0.tar.gz)

- Tracker home: [https://shadowlock-download-tracker.vibelock.workers.dev/](https://shadowlock-download-tracker.vibelock.workers.dev/)
- Stats: [https://shadowlock-download-tracker.vibelock.workers.dev/stats](https://shadowlock-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/shadowlock/releases](https://github.com/AzielEliab/shadowlock/releases)

Query params: `owner`, `repo` (`owner/repo` is accepted), `branch`,
`fork` (`1` or `owner/repo`), `tag`, `asset`. Forks can POST `/event`
so their downloads are counted separately. See the worker README.

---

## Verify

Release artifacts are ordinary source tarballs, not a proprietary
binary. Publish the SHA-256 next to the file on GitHub Releases.
Verify a downloaded sdist:

```bash
sha256sum shadowlock-0.1.0.tar.gz
# compare to the digest published with the release
```

The published digest for the in-tree sdist (after `python -m build`)
is recorded here when a release is cut. Until then, hash the artifact
you built locally.

---

## What it does

1. **Read** a host export (JSONL, CSV, or an in-memory list) through a
   read-only adapter. Raw ids are hashed; PII keys are dropped.
2. **Sample** exactly 1 in 5 operations via
   `sha256(salt || id) % 5 == 0`. The salt is session-local.
3. **Expect** a class-conditional envelope from initiation fields only
   (`task_class`, `urgency`, `context_signals`). No ML.
4. **Ledger** money made, money lost, money left on the table, net
   variance, efficiency score (0–1).
5. **Report** anonymous aggregates and `sha256` hex[:12] ids.
6. **Forget.** `forget()` or leaving the context manager drops every
   held payload. No `.shadowlock` store, no sqlite, no job log.

## Install

Python 3.10+. Stdlib only in the core (no numpy, no HTTP client).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

From a release artifact:

```bash
python -m pip install shadowlock-0.1.0.tar.gz
```

## CLI

```bash
shadowlock version

shadowlock observe --in jobs.jsonl --format jsonl --out report.json
shadowlock observe --in jobs.jsonl --stdout
shadowlock observe --in jobs.csv --format csv --stdout
shadowlock observe --in jobs.jsonl --stdout --airgap
```

`--out` writes the anonymous summary JSON only (aggregates, hashed
ids). Input files are opened read-only. `--airgap` refuses to run if
`HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` (or lowercase) are set.

Library entry point:

```python
from shadowlock.adapters import JsonlAdapter, MemoryAdapter
from shadowlock.session import ShadowLockSession

with ShadowLockSession() as session:
    report = session.observe(JsonlAdapter("jobs.jsonl"))
    print(report.to_json())
# payloads are gone
```

## Example

```bash
python examples/observe_jobs.py
```

That script reads `examples/jobs.jsonl` (synthetic, no real PII),
prints an anonymous report, and forgets.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Fixtures are synthetic. They cover read-only adapters, `forget()`,
sampler determinism and ~20% rate, name/email non-leakage, ledger
fields, counterfactual independence from actuals, CLI, no data
directory, and hashed_id agreement across adapters.

## Layout

```
shadowlock/         library (envelope, adapters, sample, counterfactual,
                    ledger, session, report, cli)
tests/              pytest, offline, no network
docs/whitepaper.md  July 2026 spec
examples/           observe a synthetic JSONL
workers/download-tracker/   Cloudflare Worker + wrangler.toml
CONTRIBUTING.md     forks are first-class
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
