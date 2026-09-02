"""File import/export. No hidden .shadowlock-state.json store."""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock.cli import main
from shadowlock.jsonio import export_json, import_json


def test_import_does_not_write_hidden_state(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "in.json"
    src.write_text(json.dumps({"product": "shadowlock", "author": "Aziel Eliab", "ok": True}), encoding="utf-8")
    rec = import_json(src)
    assert rec["ok"] is True
    assert rec["author"] == "Aziel Eliab"
    assert rec["document"]["ok"] is True
    names = {p.name for p in tmp_path.iterdir()}
    assert names == {"in.json"}
    assert not (tmp_path / ".shadowlock-state.json").exists()


def test_export_writes_named_file_with_author(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    dest = tmp_path / "out.json"
    rec = export_json(dest, payload={"hello": True})
    assert rec["ok"] is True
    assert rec["author"] == "Aziel Eliab"
    doc = json.loads(dest.read_text(encoding="utf-8"))
    assert doc["author"] == "Aziel Eliab"
    assert doc["product"] == "ShadowLock"
    assert doc["payload"]["hello"] is True
    names = {p.name for p in tmp_path.iterdir()}
    assert names == {"out.json"}


def test_cli_import_export(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "in.json"
    src.write_text(json.dumps({"observed": {"id": "WO-0001"}, "ok": True}), encoding="utf-8")
    assert main(["import", str(src)]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["ok"] is True
    assert "document" not in data
    dest = tmp_path / "report.json"
    assert main(["export", str(dest)]) == 0
    rec = json.loads(capsys.readouterr().out)
    assert rec["author"] == "Aziel Eliab"
    doc = json.loads(dest.read_text(encoding="utf-8"))
    assert doc["author"] == "Aziel Eliab"
    assert not (tmp_path / ".shadowlock-state.json").exists()
