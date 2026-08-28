"""Synthetic fixtures. No real PII. No network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

SALT = "test-salt-shadowlock-2026"

SYNTHETIC_JOBS = [
    {
        "id": f"WO-{i:04d}",
        "timestamp": f"2026-07-{(i % 28) + 1:02d}T08:00:00Z",
        "task_class": ["install", "repair", "inspect"][i % 3],
        "urgency": (i % 10) / 10.0,
        "context_signals": {"region": ["north", "south", "east"][i % 3], "shift": i % 2},
        "actual_outcome": "complete",
        "actual_revenue": 200.0 + (i % 7) * 25.0,
        "actual_cost": 80.0 + (i % 5) * 10.0,
        "actual_duration": 30.0 + (i % 9) * 5.0,
    }
    for i in range(40)
]


@pytest.fixture
def salt() -> str:
    return SALT


@pytest.fixture
def jobs() -> list[dict]:
    return [dict(j) for j in SYNTHETIC_JOBS]


@pytest.fixture
def jobs_with_pii(jobs: list[dict]) -> list[dict]:
    out = []
    for i, j in enumerate(jobs):
        rec = dict(j)
        rec["name"] = "Alice Example"
        rec["email"] = "alice@example.test"
        rec["team"] = "Red Team"
        rec["department"] = "Field Ops"
        rec["phone"] = "555-0100"
        rec["technician_name"] = "Bob Example"
        out.append(rec)
    return out


@pytest.fixture
def jsonl_file(tmp_path: Path, jobs_with_pii: list[dict]) -> Path:
    p = tmp_path / "jobs.jsonl"
    with p.open("w", encoding="utf-8") as fh:
        for rec in jobs_with_pii:
            fh.write(json.dumps(rec) + "\n")
    return p


@pytest.fixture
def csv_file(tmp_path: Path, jobs: list[dict]) -> Path:
    p = tmp_path / "jobs.csv"
    import csv

    fieldnames = [
        "id",
        "timestamp",
        "task_class",
        "urgency",
        "actual_outcome",
        "actual_revenue",
        "actual_cost",
        "actual_duration",
        "region",
        "name",
        "email",
    ]
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for rec in jobs:
            row = {k: rec.get(k, "") for k in fieldnames}
            row["region"] = rec["context_signals"]["region"]
            row["name"] = "Alice Example"
            row["email"] = "alice@example.test"
            w.writerow(row)
    return p
