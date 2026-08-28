"""Optional --airgap refuses proxy environment variables."""

from __future__ import annotations

import pytest

from shadowlock.cli import main
from shadowlock.errors import AirgapError
from shadowlock.session import ShadowLockSession, assert_airgap


def test_airgap_refuses_proxy_env(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    with pytest.raises(AirgapError):
        assert_airgap()
    with pytest.raises(AirgapError):
        ShadowLockSession(airgap=True)


def test_airgap_ok_without_proxy(monkeypatch) -> None:
    for k in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "FTP_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "ftp_proxy",
    ):
        monkeypatch.delenv(k, raising=False)
    assert_airgap()
    ShadowLockSession(airgap=True)


def test_cli_airgap(monkeypatch, jsonl_file, capsys) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    rc = main(["observe", "--in", str(jsonl_file), "--stdout", "--airgap"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "air-gap" in err.lower() or "proxy" in err.lower()
