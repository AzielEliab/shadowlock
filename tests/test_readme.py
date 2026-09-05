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


FULL_AI_CLIENTS = (
    "ChatGPT (GPT Actions / OpenAI)",
    "Grok (xAI)",
    "Venice",
    "Claude (Anthropic)",
    "Cursor (MCP)",
    "Glama (MCP)",
    "Perplexity",
    "Microsoft Copilot / Bing",
    "Google Gemini / Vertex",
    "Mistral",
    "Meta AI",
    "Apple Intelligence surfaces",
    "Amazon Q tooling",
    "DuckAssist",
    "You.com",
    "Cohere",
)


def test_readme_and_skill_list_full_ai_clients() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    skill = Path("SKILL.md").read_text(encoding="utf-8")
    worker = Path("workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
    page = Path("workers/download-tracker/src/page.js").read_text(encoding="utf-8")
    assert "## Use with AI assistants" in readme
    assert "## Use with Grok, ChatGPT, Venice" not in readme
    assert "use with Grok, ChatGPT, Venice" not in worker
    assert "Use with AI assistants" in worker
    for client in FULL_AI_CLIENTS:
        assert client in readme
        assert client in skill
        assert client in worker
        assert client in page
    assert "Aziel Eliab only" in readme or "Aziel Eliab" in readme


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
