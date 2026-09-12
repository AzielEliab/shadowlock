"""Worker homepage brand mark.

Public mark is /sigil.png with empty alt and no words on the mark.
Scrub public “everblooming sigil” stamp/title on the mark only.
Keep non-UI verify strings (X-Aziel-Sigil header). Identity is Aziel Eliab only.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "workers/download-tracker/src/page.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
TOML = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
WORKER_README = (ROOT / "workers/download-tracker/README.md").read_text(encoding="utf-8")
SIGIL = ROOT / "workers/download-tracker/public/sigil.png"

BRANDMARK = (
    '<img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async">'
)


def test_brandmark_empty_alt_no_public_stamp() -> None:
    assert BRANDMARK in PAGE
    assert 'alt="Everblooming' not in PAGE
    assert 'alt="everblooming' not in PAGE
    assert "Everblooming sigil" not in PAGE
    assert "everblooming sigil" not in PAGE.lower()
    assert 'class="stamp"' not in PAGE
    assert "Aziel Eliab" in PAGE
    assert "Collin" not in PAGE
    assert "Horton" not in PAGE


def test_keep_non_ui_verify_strings() -> None:
    assert '"X-Aziel-Sigil": "Everblooming"' in PAGE
    assert "serveSigil" in INDEX
    assert "/sigil.png" in TOML


def test_official_sigil_png_size() -> None:
    assert SIGIL.is_file()
    assert SIGIL.stat().st_size == 75035


def test_worker_readme_no_public_everblooming_stamp() -> None:
    assert "Everblooming sigil" not in WORKER_README
    assert "/sigil.png" in WORKER_README
