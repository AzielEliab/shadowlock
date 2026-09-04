"""Command-line interface for ShadowLock.

    shadowlock version
    shadowlock ui [--host 127.0.0.1] [--port 8764]
    shadowlock doctor [--verify] [--json]
    shadowlock import FILE.json
    shadowlock export FILE.json
    shadowlock attach [--host 127.0.0.1] [--port 8800]
    shadowlock observe --azos [--stdout]
    shadowlock observe --in jobs.jsonl --format jsonl|csv --out report.json
    shadowlock observe --in jobs.jsonl --stdout

``--out`` writes the anonymous summary JSON only (aggregates, hashed ids).
Input files are opened read-only. Optional ``--airgap`` refuses proxy env vars.
``attach`` / ``observe --azos`` OS-hook into AZ-OS under ethics policy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from shadowlock import __version__
from shadowlock.adapters import CsvAdapter, JsonlAdapter
from shadowlock.errors import AirgapError, EthicsError, HookError, SessionForgottenError
from shadowlock.session import ShadowLockSession, assert_airgap


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shadowlock",
        description=(
            "ShadowLock — a read-only, zero-retention outcome mirror "
            "(Aziel Eliab). OS-hooks into AZ-OS for process/job observation "
            "under ethics policy. Observes; does not control. "
            "Change is optional. Truth is not. "
            "Local UI: `shadowlock ui` at http://127.0.0.1:8764."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_ui = sub.add_parser("ui", help="Run the localhost UI (127.0.0.1:8764).")
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8764, help="Bind port (default 8764).")

    p_obs = sub.add_parser(
        "observe",
        help="Read a job file, sample 1 in 5, print or write an anonymous report.",
    )
    p_obs.add_argument(
        "--in",
        dest="inp",
        default=None,
        help="Input JSONL or CSV file (optional when --azos).",
    )
    p_obs.add_argument(
        "--format",
        choices=("jsonl", "csv"),
        default=None,
        help="Input format (default: infer from extension).",
    )
    p_obs.add_argument(
        "--out",
        dest="out",
        default=None,
        help="Write anonymous summary JSON (aggregates, no raw ids/names).",
    )
    p_obs.add_argument(
        "--stdout",
        action="store_true",
        help="Print the anonymous summary JSON to stdout.",
    )
    p_obs.add_argument(
        "--salt",
        default=None,
        help="Optional session salt (hex/string). Default: random, not retained.",
    )
    p_obs.add_argument(
        "--airgap",
        action="store_true",
        help="Refuse to run if HTTP(S)_PROXY / ALL_PROXY (or lowercase) are set.",
    )
    p_obs.add_argument(
        "--azos",
        action="store_true",
        help="Attach via AZ-OS (loopback 127.0.0.1:8800) under ethics policy.",
    )
    p_obs.add_argument(
        "--azos-host",
        default="127.0.0.1",
        help="AZ-OS loopback host (default 127.0.0.1).",
    )
    p_obs.add_argument(
        "--azos-port",
        type=int,
        default=8800,
        help="AZ-OS loopback port (default 8800).",
    )
    p_obs.add_argument(
        "--hosted",
        action="store_true",
        help="Use hosted AZ-OS overlay labels (refused with --airgap).",
    )
    p_obs.add_argument(
        "--actor",
        default="operator",
        help="Named actor for the AZ-OS ethics proposal (not a privilege).",
    )

    p_att = sub.add_parser(
        "attach",
        help="OS-hook into AZ-OS. Ethics-gated attach receipt. Does not control.",
    )
    p_att.add_argument("--host", default="127.0.0.1", help="AZ-OS host (default 127.0.0.1).")
    p_att.add_argument("--port", type=int, default=8800, help="AZ-OS port (default 8800).")
    p_att.add_argument(
        "--hosted",
        action="store_true",
        help="Use hosted AZ-OS overlay labels (refused with --airgap).",
    )
    p_att.add_argument(
        "--airgap",
        action="store_true",
        help="Refuse to run if HTTP(S)_PROXY / ALL_PROXY (or lowercase) are set.",
    )
    p_att.add_argument("--actor", default="operator", help="Named actor (not a privilege).")
    p_att.add_argument(
        "--in",
        dest="inp",
        default=None,
        help="Optional extra job file to include after attach.",
    )
    p_att.add_argument(
        "--format",
        choices=("jsonl", "csv"),
        default=None,
        help="Input format when --in is set (default: infer).",
    )

    p_doc = sub.add_parser(
        "doctor",
        help="Check that ShadowLock can run. Speaks in plain words. No network.",
    )
    p_doc.add_argument(
        "--verify",
        action="store_true",
        help="Also compare a sample job and check names were dropped.",
    )
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print doctor results as JSON.")

    p_imp = sub.add_parser("import", help="Read a JSON file. Does not keep a hidden copy.")
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Write a JSON file you name. Author Aziel Eliab.")
    p_exp.add_argument("path")

    return parser


def _adapter_for(path: Path, fmt: str | None):
    kind = fmt
    if kind is None:
        suf = path.suffix.lower()
        if suf in {".csv"}:
            kind = "csv"
        else:
            kind = "jsonl"
    if kind == "csv":
        return CsvAdapter(path)
    return JsonlAdapter(path)


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.cmd == "version":
        sys.stdout.write(f"shadowlock {__version__}\n")
        return 0

    if args.cmd == "ui":
        from shadowlock.ui import serve

        serve(host=args.host, port=args.port)
        return 0

    if args.cmd == "observe":
        if args.airgap:
            try:
                assert_airgap()
            except AirgapError as exc:
                sys.stderr.write(f"shadowlock: {exc}\n")
                return 2
        if not args.out and not args.stdout:
            sys.stderr.write("shadowlock: pass --out FILE or --stdout\n")
            return 2
        if getattr(args, "azos", False):
            return _observe_azos(args)
        if not args.inp:
            sys.stderr.write("shadowlock: pass --in FILE or --azos\n")
            return 2
        path = Path(args.inp)
        if not path.is_file():
            sys.stderr.write(f"shadowlock: input not found: {path}\n")
            return 2
        adapter = _adapter_for(path, args.format)
        try:
            with ShadowLockSession(salt=args.salt, airgap=args.airgap) as session:
                report = session.observe(adapter)
                payload = report.to_json()
        except (AirgapError, SessionForgottenError) as exc:
            sys.stderr.write(f"shadowlock: {exc}\n")
            return 2
        if args.stdout:
            sys.stdout.write(payload + "\n")
        if args.out:
            out_path = Path(args.out)
            out_path.write_text(payload + "\n", encoding="utf-8")
        return 0

    if args.cmd == "attach":
        return _attach_azos(args)

    if args.cmd == "doctor":
        from shadowlock.doctor import run_doctor

        return run_doctor(
            as_json=getattr(args, "as_json", False),
            verify=getattr(args, "verify", False),
        )

    if args.cmd == "import":
        from shadowlock.jsonio import import_json

        try:
            rec = import_json(args.path)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"shadowlock: {exc}\n")
            return 2
        # Do not dump the document: keys and ok only.
        shown = {k: rec[k] for k in rec if k != "document"}
        sys.stdout.write(json.dumps(shown, indent=2, ensure_ascii=False) + "\n")
        return 0

    if args.cmd == "export":
        from shadowlock.jsonio import export_json

        try:
            rec = export_json(args.path)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"shadowlock: {exc}\n")
            return 2
        sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return 0

    return 2


def _extra_jobs(path_s: str | None, fmt: str | None) -> list[dict]:
    if not path_s:
        return []
    path = Path(path_s)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    # Re-read raw records for the hook (ids hashed again at observe).
    text = path.read_text(encoding="utf-8")
    if (fmt or path.suffix.lower()) == "csv" or path.suffix.lower() == ".csv":
        import csv
        from io import StringIO

        return list(csv.DictReader(StringIO(text)))
    jobs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if isinstance(rec, dict):
            jobs.append(rec)
    return jobs


def _ethics_from_args(args: argparse.Namespace) -> dict:
    from shadowlock.ethics import DEFAULT_OBSERVE_PROPOSAL

    ethics = dict(DEFAULT_OBSERVE_PROPOSAL)
    ethics["actor"] = getattr(args, "actor", None) or "operator"
    return ethics


def _write_observe(args: argparse.Namespace, payload: str) -> None:
    if getattr(args, "stdout", False):
        sys.stdout.write(payload + "\n")
    if getattr(args, "out", None):
        Path(args.out).write_text(payload + "\n", encoding="utf-8")


def _attach_azos(args: argparse.Namespace) -> int:
    from shadowlock.azos_hook import LocalObserver

    try:
        extra = _extra_jobs(getattr(args, "inp", None), getattr(args, "format", None))
        observer = LocalObserver(
            host=args.host,
            port=args.port,
            hosted=bool(getattr(args, "hosted", False)),
            airgap=bool(getattr(args, "airgap", False)),
        )
        receipt = observer.attach(ethics=_ethics_from_args(args), extra_jobs=extra)
    except FileNotFoundError as exc:
        sys.stderr.write(f"shadowlock: input not found: {exc}\n")
        return 2
    except (AirgapError, EthicsError, HookError) as exc:
        sys.stderr.write(f"shadowlock: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(receipt.as_dict(), indent=2, ensure_ascii=False) + "\n")
    return 0


def _observe_azos(args: argparse.Namespace) -> int:
    from shadowlock.azos_hook import LocalObserver

    try:
        extra = _extra_jobs(args.inp, args.format)
        observer = LocalObserver(
            host=getattr(args, "azos_host", "127.0.0.1"),
            port=getattr(args, "azos_port", 8800),
            hosted=bool(getattr(args, "hosted", False)),
            airgap=bool(args.airgap),
            salt=args.salt,
        )
        observer.attach(ethics=_ethics_from_args(args), extra_jobs=extra)
        report = observer.observe(salt=args.salt)
        payload = report.to_json()
    except FileNotFoundError as exc:
        sys.stderr.write(f"shadowlock: input not found: {exc}\n")
        return 2
    except (AirgapError, EthicsError, HookError, SessionForgottenError) as exc:
        sys.stderr.write(f"shadowlock: {exc}\n")
        return 2
    _write_observe(args, payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
