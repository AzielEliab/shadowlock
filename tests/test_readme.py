"""README stays kid-plain, cites DOI, author Aziel Eliab only."""

from pathlib import Path


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
    assert "Collin" not in text
    assert "Horton" not in text
