"""Session does not create a data directory or sqlite / .shadowlock store."""

from __future__ import annotations

from pathlib import Path

from shadowlock.adapters import MemoryAdapter
from shadowlock.session import ShadowLockSession


def test_session_does_not_create_data_directory(jobs: list[dict], salt: str, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    session = ShadowLockSession(salt=salt)
    session.observe(MemoryAdapter(jobs))
    names = {p.name for p in tmp_path.iterdir()}
    assert ".shadowlock" not in names
    assert "shadowlock.db" not in names
    assert not (tmp_path / ".shadowlock").exists()
    # no sqlite files anywhere under cwd
    sqlite = list(tmp_path.rglob("*.sqlite")) + list(tmp_path.rglob("*.db"))
    assert sqlite == []


def test_package_source_has_no_persistence() -> None:
    import shadowlock
    import inspect
    from pathlib import Path as P

    root = P(inspect.getfile(shadowlock)).resolve().parent
    blob = ""
    for py in root.glob("*.py"):
        blob += py.read_text(encoding="utf-8")
    for banned in ("sqlite3", "requests", "httpx", "fastapi"):
        assert banned not in blob, banned
