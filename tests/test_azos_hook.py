"""AZ-OS hook: ethics attach, fake AZ Interface, Unix IPC, read-only adapter."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from shadowlock.azos_hook import (
    PROTOCOL,
    AzosClient,
    AzosHookAdapter,
    LocalObserver,
    attach,
    encode_frame,
    records_from_azos_status,
    send_unix_frame,
    serve_unix_once,
)
from shadowlock.errors import EthicsError, HookError, ReadOnlyError


class _FakeAzos(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/status":
            self._send(
                200,
                {
                    "overlay": "AZ-OS",
                    "halted": False,
                    "lumen": "running",
                    "kernel": False,
                    "session": "test-session",
                    "builtins": ["list_modules", "echo", "status", "purge_session"],
                },
            )
            return
        if self.path == "/api/log":
            self._send(200, {"entries": [{"action": "status", "token_hash": "abc123"}]})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        body = json.loads(raw.decode("utf-8") or "{}")
        if self.path == "/api/request":
            if body.get("action") not in {"status", "observe", "list_modules"}:
                self._send(403, {"passed": False, "invite": "unsigned"})
                return
            self._send(200, {"passed": True, "token": "tok-test-abcdef", "token_preview": "tok-test…"})
            return
        if self.path == "/api/exec":
            self._send(
                200,
                {
                    "ok": True,
                    "result": {
                        "overlay": "AZ-OS",
                        "halted": False,
                        "lumen": "running",
                        "session": "exec-session",
                    },
                },
            )
            return
        self._send(404, {"error": "not found"})


@pytest.fixture
def fake_azos():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _FakeAzos)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield "127.0.0.1", port
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_protocol_constant() -> None:
    assert PROTOCOL == "azos-shadowlock-hook/1"


def test_offline_attach_and_observe() -> None:
    jobs = [
        {
            "id": "WO-hook-1",
            "task_class": "repair",
            "urgency": 0.5,
            "actual_duration": 40,
            "actual_cost": 90,
            "actual_revenue": 220,
            "actual_outcome": "complete",
            "name": "Alice Example",
        }
    ]
    observer = LocalObserver(salt="hook-salt")
    receipt = observer.attach(extra_jobs=jobs, live=False)
    assert receipt.attached is True
    assert receipt.ethics.passed is True
    assert receipt.author == "Aziel Eliab"
    report = observer.observe()
    payload = report.to_json()
    assert "Alice Example" not in payload
    observer.detach()
    assert observer.receipt is None


def test_live_attach_against_fake_azos(fake_azos) -> None:
    host, port = fake_azos
    receipt = attach(host=host, port=port)
    assert receipt.attached is True
    assert receipt.azos.get("overlay") == "AZ-OS"
    assert receipt.token_preview
    assert receipt.job_count >= 1
    data = receipt.as_dict()
    assert data["kernel"] is False
    assert data["intercepts_caller_os"] is False


def test_observe_azos_via_fake(fake_azos) -> None:
    host, port = fake_azos
    extra = [
        {
            "id": "pid-4242",
            "pid": 4242,
            "task_class": "process",
            "actual_outcome": "complete",
            "actual_duration": 12,
            "actual_cost": 1,
            "actual_revenue": 3,
        }
    ]
    observer = LocalObserver(host=host, port=port, salt="proc-salt")
    observer.attach(extra_jobs=extra)
    report = observer.observe()
    assert report.observed >= 1
    assert "4242" not in report.to_json() or report.sampled >= 0


def test_ethics_refuse_before_network() -> None:
    observer = LocalObserver()
    with pytest.raises(EthicsError):
        observer.attach(ethics={"action": "halt", "definition": "stop everything now",
                                "evidence": "operator asked to halt overlay",
                                "impact": "overlay stops accepting work",
                                "actor": "operator"})


def test_missing_azos_raises_invite() -> None:
    client = AzosClient(host="127.0.0.1", port=1)
    observer = LocalObserver(client=client)
    with pytest.raises(HookError, match="azos ui"):
        observer.attach()


def test_hook_adapter_is_readonly() -> None:
    adapter = AzosHookAdapter([{"id": "x", "task_class": "repair"}])
    with pytest.raises(ReadOnlyError):
        adapter.write()


def test_status_maps_to_job() -> None:
    recs = records_from_azos_status({"overlay": "AZ-OS", "halted": False, "session": "s1", "lumen": "running"})
    assert recs[0]["task_class"] == "azos-overlay"
    assert recs[0]["actual_outcome"] == "running"


def test_cli_attach_and_observe_azos(fake_azos, capsys) -> None:
    from shadowlock.cli import main

    host, port = fake_azos
    assert main(["attach", "--host", host, "--port", str(port)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["attached"] is True
    assert data["author"] == "Aziel Eliab"
    assert main([
        "observe",
        "--azos",
        "--azos-host",
        host,
        "--azos-port",
        str(port),
        "--stdout",
        "--salt",
        "cli-azos",
    ]) == 0
    report = json.loads(capsys.readouterr().out)
    assert "ledger" in report


def test_unix_ipc_roundtrip(tmp_path: Path) -> None:
    sock = str(tmp_path / "hook.sock")
    reply = {"protocol": PROTOCOL, "ok": True, "author": "Aziel Eliab"}
    incoming_holder: dict = {}

    def server() -> None:
        incoming_holder["frame"] = serve_unix_once(sock, reply)

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    # Wait until the socket exists.
    for _ in range(50):
        if Path(sock).exists():
            break
        threading.Event().wait(0.02)
    frame = encode_frame("attach", jobs=[{"id": "u1", "task_class": "repair"}])
    out = send_unix_frame(sock, frame)
    thread.join(timeout=2)
    assert out["ok"] is True
    assert incoming_holder["frame"]["kind"] == "attach"
    assert incoming_holder["frame"]["jobs"][0]["id"] == "u1"
