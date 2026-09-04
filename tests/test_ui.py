"""Local UI: loopback only, GET / contains ShadowLock. No disk writes."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from shadowlock.cli import _build_parser
from shadowlock.ui import DEFAULT_HOST, DEFAULT_PORT, LOOPBACK, make_server


def test_cli_ui_defaults() -> None:
    args = _build_parser().parse_args(["ui"])
    assert args.host == "127.0.0.1"
    assert args.host == DEFAULT_HOST
    assert args.port == 8764
    assert args.port == DEFAULT_PORT


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def test_ui_get_root_200_contains_shadowlock() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            assert resp.status == 200
            html = resp.read()
        assert b"ShadowLock" in html
        assert b"127.0.0.1" in html
        assert b"Import JSON file" in html
        assert b"Export JSON report" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["ok"] is True
        assert payload["bind_host"] == "127.0.0.1"
        assert payload["azos_hook"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_page_has_file_import_and_export() -> None:
    from shadowlock.ui import PAGE

    assert "Import JSON file" in PAGE
    assert "Attach via AZ-OS" in PAGE
    assert 'type="file"' in PAGE
    assert "Export JSON report" in PAGE
    assert "Aziel Eliab" in PAGE
    assert "Simple" in PAGE
    assert "Advanced" in PAGE
    assert "No OS hook" not in PAGE


def test_ui_observe_drops_names() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps({
            "observed": {
                "id": "WO-0001",
                "task_class": "repair",
                "urgency": 0.5,
                "actual_duration": 40,
                "actual_cost": 90,
                "actual_revenue": 220,
                "actual_outcome": "complete",
                "name": "Alice Example",
            },
            "counterfactual": {"duration": [25, 45], "cost": [70, 110], "revenue": [180, 260]},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/observe",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            report = json.loads(resp.read().decode("utf-8"))
        assert report["author"] == "Aziel Eliab"
        dumped = json.dumps(report)
        assert "Alice Example" not in dumped
        assert "ledger" in report["report"]
        hook_body = json.dumps({
            "live": False,
            "jobs": [{
                "id": "WO-hook",
                "task_class": "repair",
                "urgency": 0.5,
                "actual_duration": 40,
                "actual_cost": 90,
                "actual_revenue": 220,
                "actual_outcome": "complete",
                "name": "Alice Example",
            }],
            "counterfactual": {"duration": [25, 45], "cost": [70, 110], "revenue": [180, 260]},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/attach",
            data=hook_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            hooked = json.loads(resp.read().decode("utf-8"))
        assert hooked["attached"] is True
        assert hooked["author"] == "Aziel Eliab"
        assert "Alice Example" not in json.dumps(hooked)
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
