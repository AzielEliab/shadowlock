"""doctor speaks in plain words. Author Aziel Eliab. No hidden store."""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock.cli import main
from shadowlock.doctor import run_doctor


def test_doctor_plain_words(capsys) -> None:
    assert run_doctor() == 0
    out = capsys.readouterr().out
    assert "Aziel Eliab" in out
    assert "All good" in out
    assert "yes" in out
    assert "JSON" in out
    assert "does not run them" in out


def test_doctor_verify(capsys) -> None:
    assert run_doctor(verify=True) == 0
    out = capsys.readouterr().out
    assert "sample job" in out.lower() or "names were dropped" in out.lower() or "compared" in out.lower()
    assert "Aziel Eliab" in out


def test_doctor_json(capsys) -> None:
    assert run_doctor(as_json=True, verify=True) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["author"] == "Aziel Eliab"
    assert data["network"] is False
    assert data["telemetry"] is False
    names = {c["name"] for c in data["checks"]}
    assert "identity" in names
    assert "verify" in names
    assert "azos hook" in names
    assert all(c["ok"] for c in data["checks"])


def test_cli_doctor(capsys) -> None:
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "Aziel Eliab" in out
    assert "All good" in out
