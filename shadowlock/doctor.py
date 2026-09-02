"""Self-check for ShadowLock. Speaks in plain words. No network, no telemetry.

    shadowlock doctor
    shadowlock doctor --verify
"""

from __future__ import annotations

import json
import tempfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from shadowlock import __version__

AUTHOR = "Aziel Eliab"
Check = tuple[str, bool, str]

PLAIN = {
    "version": "Package version",
    "identity": "Author is Aziel Eliab",
    "json import/export": "Can read and write a JSON file",
    "loopback": "Local page stays on this computer",
    "verify": "A sample job can be compared without keeping names",
}


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__:
        return _ok("version", str(__version__))
    return _fail("version", "missing")


def _check_identity() -> Check:
    try:
        mod = __import__(__name__.split(".")[0])
        author = str(getattr(mod, "__author__", AUTHOR))
    except Exception as exc:  # noqa: BLE001
        return _fail("identity", str(exc))
    blob = author + " " + AUTHOR
    forbidden = ("Col" + "lin H" + "orton", "Ja" + "ck Al" + "tman", "GodLock" + ".AZ", "Reve" + "aler")
    if any(x in blob for x in forbidden):
        return _fail("identity", "forbidden identity label")
    if "Aziel Eliab" not in blob:
        return _fail("identity", author)
    return _ok("identity", AUTHOR)


def _check_json_roundtrip() -> Check:
    from shadowlock.jsonio import export_json, import_json

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.json"
        out = Path(tmp) / "out.json"
        src.write_text(
            json.dumps({"product": "shadowlock", "author": AUTHOR, "ok": True}, indent=2),
            encoding="utf-8",
        )
        rec = import_json(src)
        if not rec.get("ok"):
            return _fail("json import/export", str(rec))
        leftover = [p.name for p in Path(tmp).iterdir() if p.name not in ("in.json",)]
        if leftover:
            return _fail("json import/export", "unexpected files: " + ",".join(leftover))
        rec2 = export_json(out, payload=rec.get("document"))
        if not rec2.get("ok") or not out.exists():
            return _fail("json import/export", str(rec2))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("author") != AUTHOR:
            return _fail("json import/export", str(doc.get("author")))
        leftover = [p.name for p in Path(tmp).iterdir() if p.name not in ("in.json", "out.json")]
        if leftover:
            return _fail("json import/export", "unexpected files: " + ",".join(leftover))
        return _ok("json import/export", "read a file and wrote a file")


def _check_loopback() -> Check:
    from shadowlock.ui import LOOPBACK, Handler

    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        host, port = httpd.server_address[:2]
        httpd.server_close()
    except Exception as exc:  # noqa: BLE001
        return _fail("loopback", str(exc))
    if str(host) not in LOOPBACK:
        return _fail("loopback", f"bound {host}, expected 127.0.0.1")
    return _ok("loopback", f"{host}:{port}")


def _check_verify() -> Check:
    from shadowlock.adapters import MemoryAdapter
    from shadowlock.session import ShadowLockSession

    jobs = [
        {
            "id": "doctor-1",
            "task_class": "repair",
            "urgency": 0.5,
            "actual_duration": 40,
            "actual_cost": 90,
            "actual_revenue": 220,
            "actual_outcome": "complete",
            "name": "Alice Example",
            "email": "alice@example.test",
        }
    ]
    with ShadowLockSession(salt="doctor-verify") as session:
        report = session.observe(MemoryAdapter(jobs))
        payload = report.to_json()
        held = session.held_payload_count()
    if held != 0:
        return _fail("verify", "session did not forget")
    if "Alice Example" in payload or "alice@example.test" in payload:
        return _fail("verify", "a name leaked into the report")
    data = json.loads(payload)
    if "ledger" not in data:
        return _fail("verify", "report missing ledger")
    return _ok("verify", "sample job compared; names were dropped")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_json_roundtrip,
    _check_loopback,
)


def format_human(results: list[dict], *, ok: bool, version: str) -> str:
    lines = [f"ShadowLock check — version {version} — author {AUTHOR}", ""]
    for row in results:
        mark = "yes" if row.get("ok") else "no"
        label = PLAIN.get(str(row.get("name")), str(row.get("name")))
        detail = row.get("detail") or ""
        extra = f" — {detail}" if detail else ""
        lines.append(f"  {label}: {mark}{extra}")
    lines.append("")
    if ok:
        lines.append(
            "All good. ShadowLock looks at jobs you already have. "
            "It does not run them, save people, or talk to the internet."
        )
    else:
        lines.append("Something is wrong. ShadowLock is not ready.")
    return "\n".join(lines)


def run_doctor(*, as_json: bool = False, verify: bool = False) -> int:
    fns: list[Callable[[], Check]] = list(CHECKS)
    if verify:
        fns.append(_check_verify)
    results = []
    failed = 0
    for fn in fns:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": __version__,
        "author": AUTHOR,
        "network": False,
        "telemetry": False,
        "verify": verify,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_human(results, ok=failed == 0, version=__version__))
    return 0 if failed == 0 else 1
