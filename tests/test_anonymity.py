"""Names/emails/teams must not appear in report JSON even if the source had them."""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock.adapters import CsvAdapter, JsonlAdapter, MemoryAdapter
from shadowlock.session import ShadowLockSession

LEAKS = (
    "Alice Example",
    "alice@example.test",
    "Red Team",
    "Field Ops",
    "555-0100",
    "Bob Example",
    "WO-0001",
    "WO-0000",
)


def _assert_clean(payload: str) -> None:
    for leak in LEAKS:
        assert leak not in payload, leak


def test_memory_adapter_drops_pii_from_report(jobs_with_pii: list[dict], salt: str) -> None:
    session = ShadowLockSession(salt=salt)
    report = session.observe(MemoryAdapter(jobs_with_pii))
    payload = report.to_json()
    _assert_clean(payload)
    as_dict = json.dumps(report.to_dict())
    _assert_clean(as_dict)
    for hid in report.hashed_ids:
        assert len(hid) == 12
        assert all(c in "0123456789abcdef" for c in hid)


def test_jsonl_adapter_drops_pii(jsonl_file: Path, salt: str) -> None:
    session = ShadowLockSession(salt=salt)
    report = session.observe(JsonlAdapter(jsonl_file))
    _assert_clean(report.to_json())
    _assert_clean(json.dumps(report.to_dict()))


def test_csv_adapter_drops_pii(csv_file: Path, salt: str) -> None:
    session = ShadowLockSession(salt=salt)
    report = session.observe(CsvAdapter(csv_file))
    _assert_clean(report.to_json())
