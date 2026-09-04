"""CLI version + observe on a fixture jsonl."""

from __future__ import annotations

import json
from pathlib import Path

from shadowlock import __version__
from shadowlock.cli import main


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"shadowlock {__version__}"


def test_cli_observe_stdout(jsonl_file: Path, capsys) -> None:
    rc = main(["observe", "--in", str(jsonl_file), "--format", "jsonl", "--stdout", "--salt", "cli-salt"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "ledger" in data
    for key in ("money_made", "money_lost", "money_left_on_table", "net_variance", "efficiency_score"):
        assert key in data["ledger"]
    assert "Alice Example" not in out
    assert "alice@example.test" not in out


def test_cli_observe_out_file(jsonl_file: Path, tmp_path: Path, capsys) -> None:
    dest = tmp_path / "report.json"
    rc = main(["observe", "--in", str(jsonl_file), "--out", str(dest), "--salt", "cli-salt"])
    assert rc == 0
    payload = dest.read_text(encoding="utf-8")
    data = json.loads(payload)
    assert data["observed"] == 40
    assert "sampled_hashed_ids" in data
    assert "Alice Example" not in payload


def test_help_lists_ui_and_version() -> None:
    from shadowlock.cli import _build_parser

    text = _build_parser().format_help()
    assert "ui" in text
    assert "version" in text
    assert "127.0.0.1:8764" in text or "shadowlock ui" in text


def test_help_lists_doctor_import_export() -> None:
    from shadowlock.cli import _build_parser

    text = _build_parser().format_help()
    assert "doctor" in text
    assert "import" in text
    assert "export" in text
    assert "attach" in text
    assert "azos" in text


def test_cli_observe_requires_in_or_azos(capsys) -> None:
    rc = main(["observe", "--stdout"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "--in" in err or "--azos" in err


def test_cli_attach_without_azos_exits_2(jsonl_file: Path, capsys) -> None:
    rc = main(["attach", "--host", "127.0.0.1", "--port", "1", "--in", str(jsonl_file)])
    assert rc == 2
    err = capsys.readouterr().err.lower()
    assert "azos" in err or "attach" in err or "shadowlock" in err
