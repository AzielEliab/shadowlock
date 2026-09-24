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
    assert "AZ-OS" in text


def test_cli_observe_requires_in_or_azos(capsys) -> None:
    rc = main(["observe", "--stdout"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "--in" in err or "--azos" in err


def test_bare_command_welcomes(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "shadowlock ui" in out
    assert "shadowlock doctor" in out
    assert "Aziel Eliab" in out
    assert "required" not in out.lower()


def test_help_is_short(capsys) -> None:
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "commands:" in out
    assert "advanced:" in out
    assert "changelog" not in out.lower()
    assert "shadowlock ui" in out


def test_unknown_command_has_next_step(capsys) -> None:
    assert main(["bogus"]) == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "shadowlock --help" in err


def test_import_missing_path_has_next_step(capsys) -> None:
    assert main(["import"]) == 2
    err = capsys.readouterr().err
    assert "needs a file" in err
    assert "Try:" in err


def test_observe_human_default(jsonl_file: Path, capsys) -> None:
    rc = main(["observe", "--in", str(jsonl_file), "--salt", "cli-salt"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Jobs looked at:" in out
    assert "Money made:" in out
    assert "Alice Example" not in out
    assert "efficiency_score" not in out
    assert not out.lstrip().startswith("{")


def test_observe_json_flag_unchanged(jsonl_file: Path, capsys) -> None:
    rc = main(["observe", "--in", str(jsonl_file), "--format", "jsonl", "--json", "--salt", "cli-salt"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "ledger" in data
    assert "efficiency_score" in data["ledger"]


def test_cli_attach_without_azos_exits_2(jsonl_file: Path, capsys) -> None:
    rc = main(["attach", "--host", "127.0.0.1", "--port", "1", "--in", str(jsonl_file)])
    assert rc == 2
    err = capsys.readouterr().err.lower()
    assert "azos" in err or "attach" in err or "shadowlock" in err
