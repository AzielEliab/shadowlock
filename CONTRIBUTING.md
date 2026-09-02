# Contributing to ShadowLock

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute. Pull requests are welcome
if you want a change upstream. Keep a fork forever if you do not.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only. pytest is the dev extra. No network.

## Ground rules

1. Treat `origin` as one peer among many. Downstream forks are part of
   the download-tracking model (see `workers/download-tracker`): they
   report as `{owner}/{repo}`, not as anonymous noise.
2. **No persistence.** Do not add sqlite, a `.shadowlock` operations
   store, `.shadowlock-state.json`, job logs on disk, or any write of raw envelopes. Session
   payloads live in memory and die on `forget()`. CLI `import`/`export` and the UI
   read and write only paths the user named.
3. **No write adapters.** Adapters expose `iter_jobs()` / `load` only.
   A method that writes, saves, updates, dispatches, schedules, or
   modifies an external system is out of spec and must raise.
4. **No identity fields in reports.** Person, team, and department
   names must never appear in `report.to_dict()` / JSON. Identifiers
   are `sha256` hex[:12] only. Tests that leak a known name must fail.
5. **Keep the dependency list tiny.** Stdlib only in the core. Optional
   dev extra is pytest. Do not import `requests`, `httpx`, or FastAPI.
6. **Do not add ML training, dispatch, or write-back.** The
   counterfactual is a class-conditional empirical prior from *this
   session's* sampled jobs. That is the baseline. Forks that train a
   model have left this spec.
7. **Do not invent evaluation numbers.** The 1-in-5 rate is a
   construction (`sha256(salt||id) % 5 == 0`), not a measured lift
   study. If you measure something, publish the method next to the
   number.
8. **Sampling stays opaque.** Do not replace the hash with round-robin
   or a public counter.

## Where to change things

- Envelope / PII drop: `shadowlock/envelope.py`
- Adapters: `shadowlock/adapters.py`
- Sampler: `shadowlock/sample.py`
- Counterfactual prior: `shadowlock/counterfactual.py`
- Ledger: `shadowlock/ledger.py`
- Session / forget: `shadowlock/session.py`
- Report: `shadowlock/report.py`
- CLI: `shadowlock/cli.py`
- New behavior needs a test that fails without the change.

## Reporting downloads from a fork

Point users at GitHub Releases. If you cut your own releases, POST
`/event` on the download-tracker worker so counts stay attributed to
your `owner/repo` (see `workers/download-tracker/README.md`).

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
