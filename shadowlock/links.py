"""Local Softwares link record.

ShadowLock writes this file. 4DMap is a separate Softwares and may
optionally read it. 4DMap is not part of this install.
Job payloads are not stored here.

Default path: ~/.shadowlock/links.json
Override with SHADOWLOCK_LINKS.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shadowlock import __version__
from shadowlock.catalog import card_for

AUTHOR = "Aziel Eliab"
PRODUCT = "ShadowLock"
_LOCK = threading.Lock()
_MAX_HANDLE = 240
_MAX_LABEL = 80


def links_path() -> Path:
    override = os.environ.get("SHADOWLOCK_LINKS")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".shadowlock" / "links.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _handle(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    if len(text) > _MAX_HANDLE or any(ch in text for ch in "\n\r\x00"):
        raise ValueError("Use a single line for the input id or path.")
    return text


def _label(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    if len(text) > _MAX_LABEL or any(ch in text for ch in "\n\r\x00"):
        raise ValueError("Use a short single-line business label.")
    return text


def empty_record() -> dict[str, Any]:
    return {
        "product": PRODUCT,
        "author": AUTHOR,
        "version": __version__,
        "links": [],
    }


def read_record() -> dict[str, Any]:
    path = links_path()
    if not path.is_file():
        return empty_record()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("links"), list):
        raise ValueError(f"Link file is not a ShadowLock record: {path}")
    return data


def public_view() -> dict[str, Any]:
    path = links_path()
    try:
        record = read_record()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "ok": False,
            "author": AUTHOR,
            "product": PRODUCT,
            "path": str(path),
            "exists": path.is_file(),
            "links": [],
            "error": str(exc),
        }
    return {
        "ok": True,
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
        "path": str(path),
        "exists": path.is_file(),
        "links": list(record.get("links") or []),
    }


def _write(record: dict[str, Any]) -> None:
    path = links_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def link_software(
    slug: str,
    *,
    input_id: Any = None,
    input_path: Any = None,
    business_label: Any = None,
    shared_input: Any = None,
) -> dict[str, Any]:
    card = card_for(slug)
    if card is None:
        raise ValueError(
            f'Unknown Softwares slug "{slug}". Choose a product from the list, then link it.'
        )
    default_id = f"{card['slug']}:inputs"
    default_path = f"{card['slug']}/inputs"
    shared = None if shared_input is None else str(shared_input).strip()
    if shared:
        if input_id is None or not str(input_id).strip():
            input_id = shared
        if input_path is None or not str(input_path).strip():
            input_path = shared
    row = {
        "slug": card["slug"],
        "kind": card["kind"],
        "bucket": card["bucket"],
        "name": card["name"],
        "input_id": _handle(input_id, default_id),
        "input_path": _handle(input_path, default_path),
        "linked_at": _now(),
        "business_label": _label(business_label, card["name"]),
    }
    with _LOCK:
        record = read_record()
        links = [item for item in record.get("links") or [] if isinstance(item, dict)]
        replaced = False
        for index, item in enumerate(links):
            if item.get("slug") == row["slug"] and item.get("input_id") == row["input_id"]:
                links[index] = row
                replaced = True
                break
        if not replaced:
            links.append(row)
        record = {
            "product": PRODUCT,
            "author": AUTHOR,
            "version": __version__,
            "links": links,
        }
        _write(record)
    return row


def unlink_software(slug: str, input_id: str | None = None) -> int:
    key = (slug or "").strip().lower()
    if not key:
        raise ValueError("Choose the linked product to remove.")
    with _LOCK:
        record = read_record()
        links = [item for item in record.get("links") or [] if isinstance(item, dict)]
        kept = []
        removed = 0
        for item in links:
            same_slug = item.get("slug") == key
            same_input = input_id is None or item.get("input_id") == input_id
            if same_slug and same_input:
                removed += 1
                continue
            kept.append(item)
        record["links"] = kept
        record["product"] = PRODUCT
        record["author"] = AUTHOR
        record["version"] = __version__
        if links_path().is_file() or kept:
            _write(record)
    return removed


def format_links_human(view: dict[str, Any]) -> str:
    path = view.get("path") or str(links_path())
    lines = [f"Link file: {path}"]
    if view.get("error"):
        lines.append(str(view["error"]))
        lines.append("Next: shadowlock ui")
        return "\n".join(lines) + "\n"
    links = view.get("links") or []
    if not links:
        lines.append("Nothing linked yet.")
        lines.append("Next: shadowlock ui")
        lines.append("4DMap is a separate Softwares. It may optionally read this file. It has its own install.")
        return "\n".join(lines) + "\n"
    lines.append("")
    for item in links:
        kind = item.get("kind") or item.get("bucket") or ""
        lines.append(f"{item.get('business_label') or item.get('name') or item.get('slug')} ({kind})")
        lines.append(f"  Slug: {item.get('slug')}")
        lines.append(f"  Input id: {item.get('input_id')}")
        lines.append(f"  Input path: {item.get('input_path')}")
        lines.append(f"  Linked: {item.get('linked_at')}")
        lines.append("")
    lines.append("4DMap is a separate Softwares. It may optionally read this file. It has its own install.")
    return "\n".join(lines).rstrip() + "\n"
