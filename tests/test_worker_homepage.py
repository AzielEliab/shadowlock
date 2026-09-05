"""Hosted Worker homepage is a complete ShadowLock product UI."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "workers/download-tracker/src/page.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
TOML = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")


def test_title_and_identity():
    assert "ShadowLock — Aziel Eliab" in PAGE
    assert "Aziel Eliab" in PAGE
    assert "Apache-2.0" in PAGE
    assert "Forks are welcome" in PAGE
    assert "Everblooming sigil" in PAGE
    assert "/sigil.png" in PAGE
    assert "Collin" not in PAGE
    assert "Horton" not in PAGE
    assert "No OS hook" not in PAGE
    assert "No OS hook" not in INDEX
    assert "No OS hook" not in RUNTIME


def test_seo_cite_jsonld():
    assert "application/ld+json" in PAGE
    assert "SoftwareApplication" in PAGE
    assert 'name: "ShadowLock"' in PAGE or '"name": "ShadowLock"' in PAGE
    assert "og:title" in PAGE
    assert "/cite.json" in PAGE
    assert "/robots.txt" in TOML
    assert "/sitemap.xml" in TOML
    assert "/llms.txt" in TOML
    assert "/sigil.png" in TOML
    assert "doi: null" in PAGE
    assert "No DOI invented" in PAGE
    assert "historical_doi_tombstoned" in PAGE


def test_workspace_calls_real_ops():
    assert "POST /v1/observe" in PAGE
    assert "POST /v1/hook" in PAGE
    assert 'fetch("/v1/observe"' in PAGE or "postJson(\"/v1/observe\"" in PAGE
    assert 'postJson("/v1/hook"' in PAGE
    assert "Import JSON file" in PAGE
    assert "Export JSON report" in PAGE
    assert "Show report" in PAGE
    assert "Attach via AZ-OS" in PAGE
    assert "Load sample" in PAGE
    assert "Interactive workspace" in PAGE
    assert "ledger-made" in PAGE
    assert "hashed ids" in PAGE


def test_download_install_kept():
    assert "/download" in PAGE
    assert "One-click install" in PAGE
    assert "install.sh" in PAGE
    assert "shadowlock ui" in PAGE
    assert "SHADOWLOCK_DOWNLOADS" in PAGE
    assert "github.com/AzielEliab/shadowlock" in PAGE


def test_observe_accepts_jobs():
    assert "observeRecords" in RUNTIME
    assert "jobs a non-empty array" in RUNTIME
    assert "or {jobs}" in RUNTIME


def test_worker_wires_product_page():
    assert 'from "./page.js"' in INDEX
    assert "handleSeo" in INDEX
    assert "serveSigil" in INDEX
    assert "renderHome" in INDEX
    assert "ShadowLock downloads" not in INDEX
    assert "ShadowLock downloads" not in PAGE
