"""Read-only: JsonlAdapter/CsvAdapter have no write/save/update; calling raises."""

from __future__ import annotations

from pathlib import Path

import pytest

from shadowlock.adapters import CsvAdapter, JsonlAdapter, MemoryAdapter
from shadowlock.errors import ReadOnlyError


@pytest.mark.parametrize("cls", [JsonlAdapter, CsvAdapter, MemoryAdapter])
def test_no_write_save_update_on_class(cls) -> None:
    for name in ("write", "save", "update"):
        assert name not in vars(cls)
        assert name not in getattr(cls, "__dict__", {})


def test_jsonl_write_methods_raise(jsonl_file: Path) -> None:
    adapter = JsonlAdapter(jsonl_file)
    for name in ("write", "save", "update", "dispatch", "schedule", "modify"):
        with pytest.raises(ReadOnlyError):
            getattr(adapter, name)()


def test_csv_write_methods_raise(csv_file: Path) -> None:
    adapter = CsvAdapter(csv_file)
    for name in ("write", "save", "update"):
        with pytest.raises(ReadOnlyError):
            getattr(adapter, name)()


def test_jsonl_opens_readonly(jsonl_file: Path, salt: str) -> None:
    adapter = JsonlAdapter(jsonl_file)
    envs = adapter.load(salt)
    assert len(envs) == 40
    # file still only readable content; adapter did not rewrite it
    text = jsonl_file.read_text(encoding="utf-8")
    assert "Alice Example" in text  # source may contain names; envelopes must not
