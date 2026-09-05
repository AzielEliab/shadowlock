# ShadowLock

Looks at jobs you already finished and compares them to a guess.
It **OS-hooks into AZ-OS** for process/job observation under ethics policy.
It does **not** run jobs, save people, or send anything to the internet.

**Author:** Aziel Eliab
**Date:** July 2026
**License:** [Apache-2.0](LICENSE)

> Change is optional. Truth is not.

**THIS IS:** a read-only, zero-retention outcome mirror for jobs you already have.

**THIS IS NOT:** a dispatcher, optimizer, scheduler, predictor, people profiler, or truth score.

Paper: DOI [10.5281/zenodo.21435707](https://doi.org/10.5281/zenodo.21435707) · [Zenodo record](https://zenodo.org/records/21435707)

See the spec: [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## Quick start (three steps)

1. Install: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
2. Open the local page: `shadowlock ui`
3. At http://127.0.0.1:8764, tap **Import JSON file** or **Attach via AZ-OS**, then **Show report**. Tap **Export JSON report** to save. Optional check: `shadowlock doctor --verify`.

Loopback only (`127.0.0.1`). No CDN, no telemetry.

## One-click install

```bash
curl -fsSL https://shadowlock-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `shadowlock ui` or `shadowlock attach`.

Or open the hosted product UI (observe workspace + counted download):
https://shadowlock-download-tracker.vibelock.workers.dev/

Tap **Show report** to call `POST /v1/observe`. Tap **Download** / **One-click install** for the local package.

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://shadowlock-download-tracker.vibelock.workers.dev/](https://shadowlock-download-tracker.vibelock.workers.dev/)
- Direct tarball: [shadowlock-0.2.0.tar.gz](https://shadowlock-download-tracker.vibelock.workers.dev/download?asset=shadowlock-0.2.0.tar.gz)
- One-click install: [https://shadowlock-download-tracker.vibelock.workers.dev/install.sh](https://shadowlock-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill](https://shadowlock-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json](https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/shadowlock](https://github.com/AzielEliab/shadowlock)
- Zenodo DOI: [10.5281/zenodo.21435707](https://doi.org/10.5281/zenodo.21435707) · [record](https://zenodo.org/records/21435707)

Isolated counter: Worker `shadowlock-download-tracker`, KV `SHADOWLOCK_DOWNLOADS`. `/v1` does not increment downloads.

## What it does

1. **Read** a host export (JSONL, CSV, or a JSON file) through a read-only adapter. Raw ids are hashed; PII keys are dropped.
2. **Sample** exactly 1 in 5 operations via `sha256(salt || id) % 5 == 0`. The salt is session-local.
3. **Expect** a class-conditional envelope from initiation fields only. No ML.
4. **Ledger** money made, money lost, money left on the table, net variance.
5. **Report** anonymous aggregates and `sha256` hex[:12] ids.
6. **Forget.** `forget()` or leaving the context manager drops every held payload. No `.shadowlock` store.

ShadowLock **OS-hooks into AZ-OS** for process/job observation under ethics policy (`Integrity precedes execution.`). File observe still works (`shadowlock observe --in jobs.jsonl --stdout`). `shadowlock attach` and `shadowlock observe --azos` attach to local AZ Interface on `127.0.0.1:8800`. The hook is read-only: it does not intercept the caller kernel, ptrace, dispatch, or kill processes.

## CLI

```bash
shadowlock version
shadowlock ui
shadowlock doctor
shadowlock doctor --verify
shadowlock import examples/job.json
shadowlock export report.json

shadowlock attach
shadowlock observe --azos --stdout
shadowlock observe --in jobs.jsonl --format jsonl --out report.json
shadowlock observe --in jobs.jsonl --stdout
shadowlock observe --in jobs.csv --format csv --stdout
shadowlock observe --in jobs.jsonl --stdout --airgap
shadowlock observe --azos --in jobs.jsonl --stdout
```

`--out` writes the anonymous summary JSON only (aggregates, hashed ids).
Input files are opened read-only. `--airgap` refuses to run if
`HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` (or lowercase) are set.
`import` reads a JSON file you name. `export` writes a JSON file you name.
Neither keeps a hidden copy. `--azos` / `attach` talk to AZ-OS on loopback
(or hosted overlay labels if you pass `--hosted`). `--airgap` refuses hosted.

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
prints an anonymous report, and forgets. `examples/job.json` is a
one-job file for **Import JSON file**.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Fixtures are synthetic. They cover read-only adapters, `forget()`,
sampler determinism and ~20% rate, name/email non-leakage, ledger
fields, counterfactual independence from actuals, CLI, doctor,
import/export, no data directory, hashed_id agreement across adapters,
AZ-OS ethics gates, and the AZ-OS hook / local observer.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.shadowlock`. Offline. No analytics.

```bash
cd mobile
flutter create --org com.azieeliab --project-name shadowlock .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .`. Not a store listing.

## Verify

Release artifacts are ordinary source tarballs, not a proprietary binary.

```bash
sha256sum shadowlock-0.2.0.tar.gz
shadowlock doctor --verify
```

## Use with AI assistants

Live HTTPS runtime on the download-tracker Worker. Zero-retention: `/v1` does not write KV except existing download keys.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

**OpenAPI:** import https://shadowlock-download-tracker.vibelock.workers.dev/openapi.json as a GPT Action, custom tool, HTTP tool, or other OpenAPI connector.

**MCP:** `POST https://aziel-runtime.vibelock.workers.dev/mcp` for Cursor, Glama, Claude, and other MCP clients.

```bash
curl -sS -A 'Mozilla/5.0' -X POST https://shadowlock-download-tracker.vibelock.workers.dev/v1/observe \
  -H "content-type: application/json" \
  -d '{
    "observed": {"id":"WO-0001","task_class":"repair","urgency":0.5,"actual_duration":40,"actual_cost":90,"actual_revenue":220,"actual_outcome":"complete"},
    "counterfactual": {"duration":[25,45],"cost":[70,110],"revenue":[180,260]}
  }'
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
