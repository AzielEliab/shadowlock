#!/usr/bin/env python3
"""Attach via AZ-OS ethics (offline fixture) and observe synthetic jobs.

No real PII. No network. Demonstrates the hook adapter, not a live AZ-OS.
"""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock.azos_hook import LocalObserver
from shadowlock.ethics import DEFAULT_OBSERVE_PROPOSAL

HERE = Path(__file__).resolve().parent
JOBS = HERE / "jobs.jsonl"


def main() -> None:
    extra = []
    for line in JOBS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        extra.append(json.loads(line))
    observer = LocalObserver(salt="example-azos")
    receipt = observer.attach(ethics=DEFAULT_OBSERVE_PROPOSAL, extra_jobs=extra, live=False)
    print(receipt.as_dict())
    report = observer.observe()
    print(report.to_json())
    observer.detach()
    print("forgotten; integrity precedes execution.")


if __name__ == "__main__":
    main()
