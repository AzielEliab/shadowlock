"""Softwares link record: one path for every bucket, readable by 4DMap."""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path

import pytest

from shadowlock.catalog import software_cards
from shadowlock.cli import main
from shadowlock.links import link_software, links_path, public_view
from shadowlock.ui import make_server


def test_catalog_buckets_match_suite_sort() -> None:
    cards = software_cards()
    assert len(cards) == 42
    kinds = [card["kind"] for card in cards]
    assert kinds == sorted(kinds, key=lambda kind: {"plain": 0, "gate": 1, "lock": 2}[kind])
    by_slug = {card["slug"]: card for card in cards}
    assert by_slug["staticclock"]["bucket"] == "plain"
    assert by_slug["chronolock"]["bucket"] == "lock"
    assert by_slug["decisiongate"]["bucket"] == "gate"
    assert by_slug["shadowlock"]["kind"] == "lock"
    assert sum(card["bucket"] == "plain" for card in cards) == 26
    assert sum(card["bucket"] == "gate" for card in cards) == 1
    assert sum(card["bucket"] == "lock" for card in cards) == 15


def test_link_record_fields_and_empty_file(tmp_path: Path, monkeypatch) -> None:
    dest = tmp_path / "links.json"
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(dest))
    view = public_view()
    assert view["ok"] is True
    assert view["links"] == []
    assert view["exists"] is False
    assert not dest.exists()
    assert links_path() == dest

    row = link_software("azbrowser", business_label="Front desk")
    assert row["slug"] == "azbrowser"
    assert row["kind"] == "plain"
    assert row["bucket"] == "plain"
    assert row["input_id"] == "azbrowser:inputs"
    assert row["input_path"] == "azbrowser/inputs"
    assert row["business_label"] == "Front desk"
    assert row["linked_at"].endswith("Z")
    saved = json.loads(dest.read_text(encoding="utf-8"))
    assert saved["author"] == "Aziel Eliab"
    assert saved["links"][0]["slug"] == "azbrowser"
    assert "actual_revenue" not in dest.read_text(encoding="utf-8")

    gate = link_software("decisiongate", shared_input="queue/decisions.json")
    lock = link_software("chronolock", input_id="clock-1", input_path="chronolock/jobs")
    assert gate["kind"] == "gate"
    assert gate["input_id"] == "queue/decisions.json"
    assert gate["input_path"] == "queue/decisions.json"
    assert lock["kind"] == "lock"
    assert lock["input_path"] == "chronolock/jobs"
    again = link_software("azbrowser", business_label="Front desk")
    slugs = [item["slug"] for item in public_view()["links"]]
    assert slugs.count("azbrowser") == 1
    assert again["linked_at"] >= row["linked_at"]


def test_unknown_slug_is_refused(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(tmp_path / "links.json"))
    with pytest.raises(ValueError, match="Unknown Softwares slug"):
        link_software("not-a-software")
    assert not (tmp_path / "links.json").exists()


def test_cli_links_human_and_json(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(tmp_path / "links.json"))
    assert main(["links"]) == 0
    out = capsys.readouterr().out
    assert "Nothing linked yet." in out
    assert "shadowlock ui" in out
    link_software("4dmap", business_label="Map desk")
    assert main(["links", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["links"][0]["slug"] == "4dmap"
    assert data["links"][0]["kind"] == "plain"
    assert data["path"].endswith("links.json")


def test_ui_link_api_roundtrip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(tmp_path / "links.json"))
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/links", timeout=5) as resp:
            empty = json.loads(resp.read().decode("utf-8"))
        assert empty["links"] == []
        assert empty["exists"] is False
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/software", timeout=5) as resp:
            catalog = json.loads(resp.read().decode("utf-8"))
        assert catalog["count"] == 42
        assert {card["bucket"] for card in catalog["software"]} == {"plain", "gate", "lock"}
        body = json.dumps({"slug": "peacelock", "business_label": "Review"}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/links",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            linked = json.loads(resp.read().decode("utf-8"))
        assert linked["link"]["kind"] == "lock"
        assert linked["link"]["input_id"] == "peacelock:inputs"
        bad = json.dumps({"slug": "nope"}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/links",
            data=bad,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(req, timeout=5)
        assert caught.value.code == 400
        err = json.loads(caught.value.read().decode("utf-8"))
        assert "Unknown Softwares slug" in err["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
