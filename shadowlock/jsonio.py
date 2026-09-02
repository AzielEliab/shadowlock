"""JSON import/export. Reads and writes only the paths you name. No hidden store.

Author: Aziel Eliab.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowlock import __version__

AUTHOR = "Aziel Eliab"
PRODUCT = "ShadowLock"
PACKAGE = "shadowlock"
MAX_BYTES = 1 * 1024 * 1024


def _as_path(path: str | Path) -> Path:
    return Path(path)


def import_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON object from ``path``. Does not write a sidecar file."""
    pth = _as_path(path)
    raw = pth.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError("file too large")
    doc = json.loads(raw.decode("utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("JSON object required")
    return {
        "ok": True,
        "imported": str(pth),
        "keys": sorted(str(k) for k in doc.keys()),
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
        "document": doc,
    }


def export_json(path: str | Path, payload: Any | None = None) -> dict[str, Any]:
    """Write a JSON document to ``path``. Caller names the file; nothing else is stored."""
    pth = _as_path(path)
    doc = {
        "product": PRODUCT,
        "package": PACKAGE,
        "version": __version__,
        "author": AUTHOR,
        "payload": {} if payload is None else payload,
    }
    pth.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "exported": str(pth),
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
    }
