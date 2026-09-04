# SHADOWLOCK

**A Universal, Read-Only Outcome Mirror for Operational Decision Systems**

Aziel Eliab  
July 2026  
License: Apache-2.0

> Change is optional. Truth is not.

---

## Abstract

Modern operational software systems make thousands of micro-decisions daily:
which job to send, which technician to assign, which route to take, which
quote to offer, which SLA to promise. Those systems are rarely short of
dashboards. They are short of an honest answer to a narrower question:
*given the inputs the host already had when the work started, what range
of outcomes was plausible — and what actually happened?*

ShadowLock is a read-only, zero-retention, software-agnostic outcome
mirror. It does not control, optimize, replace, dispatch, schedule, or
learn. It observes selectively (exactly a 1-in-5 rate, realized by an
opaque hash), computes a class-conditional counterfactual expectation
from initiation fields only, reports anonymous financial variance, and
forgets everything.

This document is the specification implemented by the `shadowlock`
Python package. Forks are welcome and always allowed.

---

## 1. The measurement gap

Operational stacks record *what was done*. Dispatchers record *who was
sent*. Billing records *what was charged*. None of those streams, by
themselves, measure the gap between the world that occurred and the
world that was available under the same inputs.

Without that gap:

- a slow job looks like a slow technician, or a slow region, or a slow
  day, with no envelope to say which of those claims is even in bounds;
- a high invoice looks like success, even when the host's own priors
  said the work should have cleared for less;
- a missed quote looks like weather, even when the initiation fields
  already implied a tighter revenue band.

The missing instrument is not another optimizer. Optimizers change the
system under test. The missing instrument is a **mirror**: it reads, it
computes a counterfactual, it reports, it forgets. Change remains a
choice for the operator. Truth does not.

ShadowLock fills that gap and then gets out of the way. It has no write
path into the host. It has no store of operations. It has no identity
fields in its reports. It is designed to be left running in places
where a control plane would be refused.

---

## 2. Design principles

Five constraints are non-negotiable. The implementation enforces them
in code; this section states them as spec.

### 2.1 Read-only

ShadowLock never writes, controls, schedules, or modifies an external
system. Host adapters expose only `iter_jobs()` and `load`. A call to
`write`, `save`, `update`, `dispatch`, `schedule`, or `modify` raises.
Input files are opened with `O_RDONLY`. There is no callback into the
host, no webhook, no "suggested assignment" channel.

### 2.2 Zero retention

All computation is in memory. There is no sqlite, no job log on disk,
no `.shadowlock` directory of operations. A `ShadowLockSession` holds
sampled envelopes until `.forget()` or context-manager exit; then they
are gone. The CLI may print a report to stdout or write a
**summary-only** file the user asked for (aggregates and truncated
hashes; no raw ids, no names). Across runs, nothing remains.

### 2.3 Software-agnostic

The host is not a vendor. Any system that can emit a job-shaped record
— JSONL, CSV, or an in-memory list — can be mirrored. Adapters map host
fields into a `JobEnvelope` and drop raw identifiers and PII keys at
the boundary. Forks may add adapters; they may not add write adapters.

### 2.4 Selective observation

ShadowLock evaluates **exactly 1 in 5** operations (20%). The rate is
exact as a *rate*, realized by an opaque hash, not by round-robin and
not by a visible counter.

```
int.from_bytes(sha256(salt || id)[:8], "big") % 5 == 0
```

The salt is session-local. Same id + same salt always yields the same
sample decision. Across a large closed set of distinct ids the sampled
count sits near 20% (hash distribution). Operators see a 1-in-5 mirror,
not a list of *which* tickets were chosen.

### 2.5 Non-attributable reporting

Reports never emit person, team, or department names. Identifiers are
truncated hashes only (`sha256` hex[:12]). A known name string in
adapter source must not appear in `report.to_dict()` or JSON. The
mirror measures *systems*, not people.

---

## 3. Universal architecture

```
host records ──► read-only adapter ──► JobEnvelope (anonymous)
                                              │
                                              ▼
                                   Sampler (1 in 5, opaque)
                                              │
                                              ▼
                         Expectation (class-conditional prior,
                         initiation fields only, this session)
                                              │
                                              ▼
                              FinancialLedger + Report
                                              │
                                              ▼
                                   forget() — gone
```

The session is the process. It is created, it observes an adapter, it
returns a `Report`, it forgets. It does not daemonize. The optional
localhost UI and AZ-OS hook bind loopback only. It does not create a
data directory.

### 3.0 AZ-OS hook

ShadowLock OS-hooks into **AZ-OS** for process/job observation under
ethics policy. Integrity precedes execution. The hook is an IPC/API
attach to AZ Interface (`127.0.0.1:8800`) plus an optional Unix-domain
JSON frame. Five gates (definition, evidence, impact, integrity,
responsibility) must pass before attach. Observation is read-only:
no kernel intercept, no ptrace, no dispatch, no process control.
Hosted AZ-OS `/v1` remains overlay labels, not a remote shell.

### 3.1 JobEnvelope

An envelope is already anonymous:

| Field | Role |
|-------|------|
| `hashed_id` | `sha256(salt \|\| raw_id).hex()[:12]` |
| `timestamp` | ISO-8601 or epoch, normalized to ISO |
| `task_class` | host work type |
| `urgency` | 0–1, or a mapped enum |
| `context_signals` | numeric/categorical fields the host already had; no PII keys |
| `actual_outcome` | close-out label |
| `actual_revenue` | close-out |
| `actual_cost` | close-out |
| `actual_duration` | close-out |

Raw ids are hashed on ingest and dropped. Keys such as `name`, `email`,
`phone`, `team`, `department`, and `*_name` are dropped. Values that
look like emails are dropped from `context_signals`.

### 3.2 Adapters

- `MemoryAdapter` — in-memory list of mappings.
- `JsonlAdapter` — read-only JSONL file.
- `CsvAdapter` — read-only CSV file with a header row.
- `AzosHookAdapter` — jobs/processes already collected through an AZ-OS attach.

Field aliases (`job_id`, `ticket`, `priority`, `revenue`, …) are
accepted so a host export does not have to be rewritten. Two adapters
given the same raw id and the same salt produce the same `hashed_id`.

---

## 4. Selective sampling (1 in 5)

Evaluating every operation would turn the mirror into a warehouse. That
violates zero retention and invites attribution. Evaluating a hidden
subset at a known rate is enough to estimate variance and not enough
to reconstruct a person's day.

Construction:

1. Draw a session-local salt (or accept one for reproducibility).
2. For each host id, compute `SHA-256(salt || id)`.
3. Sample if the first 8 bytes, as a big-endian integer, modulo 5, equal 0.
4. `hashed_id` is the same digest, hex-encoded, truncated to 12 characters.

Properties:

- **Deterministic** inside a session (and across sessions that reuse a salt).
- **Opaque** from the outside: there is no round-robin, no "every fifth
  row," no public list of sampled tickets.
- **Rate** is 1-in-5. On 500 distinct ids the count is expected near 100;
  tests accept a band (80–120) because a cryptographic hash is not a
  quota on an open stream.

The sample bit is computed at ingest from the raw id, then the raw id
is discarded. The session never holds a host identifier.

---

## 5. Counterfactual methodology

At sample time ShadowLock computes an **expectation envelope** from
only the fields the host already had at initiation: `task_class`,
`urgency`, `context_signals`. Close-out actuals are not inputs to the
expectation. Changing actuals must not change the expectation, only
the delta. Tests enforce this.

The baseline is not machine learning. It is a **class-conditional
empirical prior** built from previously sampled jobs *in this same
in-memory session*:

- expected duration / cost / revenue = median of matching-class actuals
  already seen;
- low / high = min / max of those actuals;
- if the class has not been seen yet, use optional `class_priors`
  `(low, high)` with the midpoint as the point estimate;
- if neither history nor a class prior exists, the field is a
  0-width **unknown** (expected is `None`; that field does not enter
  the ledger for that job). Operators who want a conservative wide
  range pass it as `class_priors`.

Urgency is an initiation field. The baseline applies a small, documented
scale to expected duration (higher urgency → slightly less expected
time). It does not look at actuals to do so.

After the expectation is recorded, the job's actuals are folded into
the in-memory prior so later jobs of the same class can use them. That
update never leaves the process. `forget()` clears it.

Deltas at close-out:

```
Δtime     = actual_duration − expected_duration
Δcost     = actual_cost     − expected_cost
Δrevenue  = actual_revenue  − expected_revenue
```

Honesty rule: the first jobs in a class are weakly identified. The
report does not pretend otherwise. A wide prior is a wide prior.

---

## 6. Financial ledger

Every report carries a ledger over **sampled** jobs only:

| Field | Definition |
|-------|------------|
| `money_made` | sum of positive revenue deltas |
| `money_lost` | sum of negative revenue deltas (as positive dollars) plus cost overruns (`actual_cost − expected_cost` when positive) |
| `money_left_on_table` | expected revenue **high-end** minus actual, when actual < expected |
| `net_variance` | `money_made − money_lost` |
| `efficiency_score` | 0–1 mean of per-job clipped ratios: expected/actual for time and cost, actual/expected for revenue |

`money_left_on_table` is opportunity cost. It is reported separately
and is not subtracted a second time inside `net_variance`.

These numbers are not a forecast, not a KPI target, and not a claim
about a person. They are the sampled difference between actuals and a
session-local envelope.

---

## 7. Reporting

A `Report` is an anonymous aggregate:

- counts: observed, sampled, target rate 0.2;
- `sampled_hashed_ids`: 12-character hex only;
- ledger fields as in §6;
- `by_task_class`: counts, no names;
- notes stating the anonymity rules.

`report.to_dict()` / JSON is the public surface. Tests fail if a known
name, email, team, department, phone, or raw work-order id leaks into
that surface.

The CLI:

```
shadowlock version
shadowlock attach
shadowlock observe --azos --stdout
shadowlock observe --in jobs.jsonl --format jsonl|csv --out report.json
shadowlock observe --in jobs.jsonl --stdout
```

`--out` writes the summary JSON the user asked for. It is not a job
log. Input files stay read-only.

---

## 8. Security

ShadowLock is a local, stdlib-only library. The threat model is
*accidental retention and accidental attribution*, not an exotic
attacker.

- **In-memory.** Envelopes live on the session object. `forget()` and
  context-manager exit drop them. No sqlite, no `~/.shadowlock`, no
  rotating log.
- **No outbound network.** The library does not import `requests`,
  `httpx`, or any HTTP client. There is no telemetry.
- **No persistence of operations.** The only disk write the CLI will
  perform is an operator-requested summary report.
- **Optional air-gap flag.** `--airgap` (and `ShadowLockSession(airgap=True)`)
  refuses to run if `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `FTP_PROXY`,
  or their lowercase forms are set.
- **Hash-verifiable source.** This project ships source, not a
  proprietary binary. Release tarballs are ordinary sdist artifacts.
  The SHA-256 of the published tarball is listed in the README and on
  GitHub Releases so an operator can verify bytes. That is the
  "signed, hash-verifiable" distribution path: inspectable source plus
  a published digest, not a sealed vendor blob.

Adapters hash identifiers before the session sees them. Reports cannot
name a person because the name never entered the envelope.

---

## 9. Strategic implications

A control plane that cannot be audited will eventually be refused. A
mirror that cannot write back can be left on.

Organizations that already run heavy operational software get, for the
first time, a vendor-neutral estimate of:

- money made beyond the initiation envelope;
- money lost to overruns;
- money left on the table relative to the high end of the same envelope;
- an efficiency score that is a ratio against the envelope, not a
  ranking of staff.

Because observation is 1-in-5 and identifiers are truncated hashes,
the report is a **system** instrument. It is safe to share with a
board, a regulator, or a counterparty who should not receive a
personnel file.

Because retention is zero, the instrument does not become a second
system of record. That is the point. The host remains the host.
ShadowLock remains a pass.

Forks are first-class. A downstream operator may add a read-only
adapter for a private host format. They may not add a write adapter
and still call the result ShadowLock.

---

## 10. What it is not

ShadowLock is **not**:

- a dispatcher, scheduler, or optimizer;
- a workforce ranking, scorecard, or HR tool;
- a machine-learning trainer or model host;
- a database, warehouse, or audit log of jobs;
- a replacement for the operational system it mirrors;
- a network service, API gateway, or FastAPI app;
- a kernel hook, ptrace injector, or process controller;
- a way to identify, contact, or evaluate a named person.

If a fork adds any of those, it has left this spec.

---

## 11. Conclusion

Operations already have plenty of software that *acts*. They have
almost none that will *look*, tell the truth about the gap between
what happened and what the initiation fields made plausible, and then
**forget**.

ShadowLock is that instrument. Read-only. Zero retention.
Software-agnostic. One in five. Anonymous. Honest about its prior.

Change is optional. Truth is not.

---

Copyright 2026 Aziel Eliab. Licensed under Apache-2.0.
Forks are welcome and always allowed.
