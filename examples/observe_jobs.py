#!/usr/bin/env python3
"""Observe synthetic jobs, print an anonymous report, forget.

No real PII. No network. No data directory.
"""

from __future__ import annotations

from pathlib import Path

from shadowlock.adapters import JsonlAdapter
from shadowlock.session import ShadowLockSession

HERE = Path(__file__).resolve().parent
JOBS = HERE / "jobs.jsonl"

# Optional initiation envelopes for classes not yet seen in this session.
CLASS_PRIORS = {
    "install": {"duration": (20, 80), "cost": (50, 180), "revenue": (150, 500)},
    "repair": {"duration": (15, 70), "cost": (40, 160), "revenue": (120, 450)},
    "inspect": {"duration": (10, 40), "cost": (20, 90), "revenue": (80, 250)},
    "quote": {"duration": (10, 50), "cost": (15, 80), "revenue": (50, 300)},
}


def main() -> None:
    adapter = JsonlAdapter(JOBS)
    with ShadowLockSession(salt="example-salt", class_priors=CLASS_PRIORS) as session:
        report = session.observe(adapter)
        print(report.to_json())
        print(f"held before forget: {session.held_payload_count()}")
    print("forgotten; change is optional. truth is not.")


if __name__ == "__main__":
    main()
