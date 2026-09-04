"""README stays kid-plain, cites DOI, author Aziel Eliab only."""

from pathlib import Path


def test_skill_azos_hook_no_disclaimer() -> None:
    text = Path("SKILL.md").read_text(encoding="utf-8")
    assert "Aziel Eliab" in text
    assert "AZ-OS" in text
    assert "No OS hook" not in text
    assert "0.2.0" in text
    worker = Path("workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
    assert "No OS hook" not in worker
    assert "0.2.0" in worker
    assert "azos-shadowlock-hook/1" in worker


def test_readme_three_steps_and_doi() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    assert "Aziel Eliab" in text
    assert "10.5281/zenodo.21435707" in text
    assert "Import JSON file" in text
    assert "Export JSON report" in text
    assert "shadowlock doctor" in text
    assert "Quick start (three steps)" in text
    assert "THIS IS NOT" in text
    assert "truth score" in text.lower() or "dispatcher" in text.lower()
    assert "AZ-OS" in text
    assert "Attach via AZ-OS" in text
    assert "No OS hook" not in text
    assert "no OS hook" not in text
    assert "Collin" not in text
    assert "Horton" not in text
