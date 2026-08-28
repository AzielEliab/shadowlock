"""Two adapters yield the same envelope hashed_id for the same raw id + salt."""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock.adapters import CsvAdapter, JsonlAdapter, MemoryAdapter
from shadowlock.sample import hashed_id_for


def test_two_adapters_same_hashed_id(jobs: list[dict], salt: str, tmp_path: Path) -> None:
    rec = jobs[0]
    mem = list(MemoryAdapter([rec]).iter_jobs(salt))
    jsonl = tmp_path / "one.jsonl"
    jsonl.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    file_envs = list(JsonlAdapter(jsonl).iter_jobs(salt))
    assert mem[0].hashed_id == file_envs[0].hashed_id
    assert mem[0].hashed_id == hashed_id_for(salt, rec["id"])
    assert mem[0].task_class == file_envs[0].task_class


def test_csv_and_memory_same_hashed_id(jobs: list[dict], salt: str, csv_file: Path) -> None:
    mem = {e.hashed_id for e in MemoryAdapter(jobs).iter_jobs(salt)}
    csv_ids = {e.hashed_id for e in CsvAdapter(csv_file).iter_jobs(salt)}
    assert mem == csv_ids


def test_load_alias(jobs: list[dict], salt: str) -> None:
    adapter = MemoryAdapter(jobs)
    assert [e.hashed_id for e in adapter.load(salt)] == [
        e.hashed_id for e in adapter.iter_jobs(salt)
    ]
