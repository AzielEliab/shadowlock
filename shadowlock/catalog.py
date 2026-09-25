"""Suite Softwares catalog shipped with ShadowLock.

Buckets follow the suite sort law: plain A–Z, then gate A–Z, then lock A–Z.
Clock is not Lock. Author: Aziel Eliab.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

BUCKETS = ("plain", "gate", "lock")


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    raw = files("shadowlock").joinpath("software_catalog.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    software = data.get("software")
    if not isinstance(software, list):
        raise ValueError("software catalog is missing its list")
    return data


def software_cards() -> list[dict[str, Any]]:
    cards = []
    for row in load_catalog()["software"]:
        if not isinstance(row, dict):
            continue
        bucket = str(row.get("bucket") or "")
        cards.append(
            {
                "name": str(row.get("name") or ""),
                "slug": str(row.get("slug") or ""),
                "bucket": bucket,
                "kind": bucket,
            }
        )
    return cards


def card_for(slug: str) -> dict[str, Any] | None:
    key = (slug or "").strip().lower()
    if not key:
        return None
    for card in software_cards():
        if card["slug"] == key:
            return card
    return None
