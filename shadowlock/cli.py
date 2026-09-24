"""Command-line interface for ShadowLock.

Human text is the default. Add ``--json`` for the same machine payload
the commands already returned. ``observe --stdout`` still prints that JSON.

    shadowlock
    shadowlock ui [--host 127.0.0.1] [--port 8764]
    shadowlock doctor [--verify] [--json]
    shadowlock observe --in jobs.jsonl
    shadowlock observe --in jobs.jsonl --json
    shadowlock import FILE.json [--json]
    shadowlock export FILE.json [--json]
    shadowlock attach [--json]
    shadowlock observe --azos --stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from shadowlock import __version__
from shadowlock.adapters import CsvAdapter, JsonlAdapter
from shadowlock.errors import AirgapError, EthicsError, HookError, SessionForgottenError
from shadowlock.session import ShadowLockSession, assert_airgap

WELCOME = """\
ShadowLock compares a finished job to a guess, then forgets the file.

Open the local page:
  shadowlock ui

Or check that it can run:
  shadowlock doctor

Other starts:
  shadowlock observe --in jobs.jsonl
  shadowlock --help

Author: Aziel Eliab
"""

HELP = """\
usage: shadowlock [<command>] [options]

ShadowLock compares a finished job to a guess, then forgets the file.
Author: Aziel Eliab.

commands:
  ui         Open the local page (http://127.0.0.1:8764)
  doctor     Check that ShadowLock can run
  observe    Compare a job file and print a short summary
  version    Print the package version

advanced:
  attach     Attach to AZ-OS on this computer (127.0.0.1:8800)
  import     Read a JSON file you name
  export     Write a JSON file you name

examples:
  shadowlock
  shadowlock ui
  shadowlock doctor
  shadowlock observe --in jobs.jsonl
  shadowlock observe --in jobs.jsonl --json
  shadowlock attach --json

Human text is the default. Add --json for machine output.
observe also accepts --stdout for that same JSON.
Run shadowlock <command> --help for one command.
"""


class RootParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        return HELP

    def error(self, message: str) -> None:
        choice = _invalid_choice(message)
        if choice is not None:
            self.exit(
                2,
                f'Unknown command "{choice}". Try: shadowlock ui   or   shadowlock --help\n',
            )
        self.exit(2, f"shadowlock: {message}\nTry: shadowlock --help\n")


class SubParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        prog = self.prog
        if "required" in message and "path" in message:
            example = "report.json" if prog.endswith("export") else "examples/job.json"
            text = f"{prog} needs a file.\nTry: {prog} {example}\n"
        elif message.startswith("unrecognized arguments"):
            text = f"Unknown option for {prog}.\nTry: {prog} --help\n"
        else:
            text = f"{prog}: {message}\nTry: {prog} --help\n"
        self.exit(2, text)


def _invalid_choice(message: str) -> str | None:
    marker = "invalid choice: '"
    if marker not in message:
        return None
    start = message.index(marker) + len(marker)
    end = message.find("'", start)
    if end < 0:
        return None
    return message[start:end]


def _build_parser() -> argparse.ArgumentParser:
    parser = RootParser(prog="shadowlock")
    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=SubParser)

    sub.add_parser("version", help="Print the package version.")

    p_ui = sub.add_parser(
        "ui",
        help="Open the local page at http://127.0.0.1:8764.",
        description="Open the local page. Loopback only.",
        epilog="Example: shadowlock ui",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8764, help="Bind port (default 8764).")

    p_obs = sub.add_parser(
        "observe",
        help="Compare a job file and print a short summary.",
        description=(
            "Compare a job file to a guess and print a short summary. "
            "Add --json or --stdout for the anonymous JSON report."
        ),
        epilog=(
            "examples:\n"
            "  shadowlock observe --in jobs.jsonl\n"
            "  shadowlock observe --in jobs.jsonl --json\n"
            "  shadowlock observe --azos --stdout"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        "--json",
        action="store_true",
        dest="as_json",
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
        help="Attach to AZ-OS on this computer. Ethics-gated. Observation only.",
        description="Attach to AZ-OS on this computer under the ethics check.",
        epilog="examples:\n  shadowlock attach\n  shadowlock attach --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    p_att.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the attach receipt as JSON.",
    )

    p_doc = sub.add_parser(
        "doctor",
        help="Check that ShadowLock can run.",
        description="Check that ShadowLock can run. Plain lines. No network.",
        epilog="examples:\n  shadowlock doctor\n  shadowlock doctor --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_doc.add_argument(
        "--verify",
        action="store_true",
        help="Also compare a sample job and check names were dropped.",
    )
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print doctor results as JSON.")

    p_imp = sub.add_parser(
        "import",
        help="Read a JSON file you name.",
        description="Read a JSON file you name. Does not keep a hidden copy.",
        epilog="examples:\n  shadowlock import examples/job.json\n  shadowlock import examples/job.json --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_imp.add_argument("path")
    p_imp.add_argument("--json", action="store_true", dest="as_json", help="Print the import record as JSON.")

    p_exp = sub.add_parser(
        "export",
        help="Write a JSON file you name.",
        description="Write a JSON file you name. Author Aziel Eliab.",
        epilog="examples:\n  shadowlock export report.json\n  shadowlock export report.json --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_exp.add_argument("path")
    p_exp.add_argument("--json", action="store_true", dest="as_json", help="Print the export record as JSON.")

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


def _die(reason: str, hint: str) -> int:
    sys.stderr.write(f"shadowlock: {reason}\nTry: {hint}\n")
    return 2


def _money(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


def format_report_human(data: dict[str, Any]) -> str:
    ledger = data.get("ledger") if isinstance(data.get("ledger"), dict) else {}
    lines = [
        "Compared the jobs in this file to a guess.",
        f"Jobs looked at: {data.get('observed', '—')}",
        f"Jobs sampled: {data.get('sampled', '—')}",
        f"Money made: {_money(ledger.get('money_made'))}",
        f"Money lost: {_money(ledger.get('money_lost'))}",
        f"Left on the table: {_money(ledger.get('money_left_on_table'))}",
        f"Net gap: {_money(ledger.get('net_variance'))}",
        "",
        "Names are left out. ShadowLock does not keep a copy.",
        "Full JSON: add --json",
    ]
    return "\n".join(lines) + "\n"


def format_attach_human(data: dict[str, Any]) -> str:
    ethics = data.get("ethics") if isinstance(data.get("ethics"), dict) else {}
    attached = bool(data.get("attached"))
    passed = ethics.get("passed")
    if attached and passed is True:
        head = "Attached to AZ-OS. The ethics check passed."
    elif attached:
        head = "Attached to AZ-OS."
    else:
        head = "AZ-OS attach did not complete."
    count = data.get("job_count")
    lines = [
        head,
        f"Protocol: {data.get('protocol') or '—'}",
        f"Jobs included: {0 if count is None else count}",
    ]
    if data.get("kernel") is False:
        lines.append("Observation only.")
    author = data.get("author")
    if author:
        lines.append(f"Author: {author}")
    lines.extend(["", "Next: shadowlock ui   or   shadowlock observe --azos", "JSON: shadowlock attach --json"])
    return "\n".join(lines) + "\n"


def format_import_human(rec: dict[str, Any]) -> str:
    keys = rec.get("keys") or []
    shown = ", ".join(str(k) for k in keys) if keys else "(none)"
    return (
        f"Read {rec.get('imported')}.\n"
        f"Keys: {shown}\n"
        "No copy was saved.\n"
        "\n"
        "Next: shadowlock ui\n"
    )


def format_export_human(rec: dict[str, Any]) -> str:
    return (
        f"Wrote {rec.get('exported')}.\n"
        f"Author: {rec.get('author')}\n"
        "\n"
        "Next: shadowlock ui\n"
    )


def _wants_json(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "stdout", False) or getattr(args, "as_json", False))


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    if not argv:
        sys.stdout.write(WELCOME)
        return 0
    if argv[0] in {"-h", "--help", "help"}:
        sys.stdout.write(HELP)
        return 0
    if argv[0] in {"-V", "--version"}:
        sys.stdout.write(f"shadowlock {__version__}\n")
        return 0

    try:
        args = _build_parser().parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 2

    if getattr(args, "cmd", None) is None:
        sys.stdout.write(WELCOME)
        return 0

    if args.cmd == "version":
        sys.stdout.write(f"shadowlock {__version__}\n")
        return 0

    if args.cmd == "ui":
        from shadowlock.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except OSError as exc:
            return _die(str(exc), "shadowlock ui --port 8765")
        return 0

    if args.cmd == "observe":
        if args.airgap:
            try:
                assert_airgap()
            except AirgapError as exc:
                return _die(str(exc), "unset the proxy variables, then run the command again")
        if getattr(args, "azos", False):
            return _observe_azos(args)
        if not args.inp:
            return _die(
                "No job file given.",
                "shadowlock observe --in jobs.jsonl   or   shadowlock observe --azos",
            )
        path = Path(args.inp)
        if not path.is_file():
            return _die(
                f"Input not found: {path}",
                "shadowlock observe --in jobs.jsonl",
            )
        adapter = _adapter_for(path, args.format)
        try:
            with ShadowLockSession(salt=args.salt, airgap=args.airgap) as session:
                report = session.observe(adapter)
                payload = report.to_json()
        except (AirgapError, SessionForgottenError) as exc:
            return _die(str(exc), "shadowlock doctor")
        _emit_report(args, payload)
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
        except FileNotFoundError:
            return _die(f"File not found: {args.path}", "shadowlock import examples/job.json")
        except json.JSONDecodeError:
            return _die("That file is not valid JSON.", "shadowlock import examples/job.json")
        except Exception as exc:  # noqa: BLE001
            return _die(str(exc), "shadowlock import examples/job.json")
        shown = {k: rec[k] for k in rec if k != "document"}
        if getattr(args, "as_json", False):
            sys.stdout.write(json.dumps(shown, indent=2, ensure_ascii=False) + "\n")
        else:
            sys.stdout.write(format_import_human(shown))
        return 0

    if args.cmd == "export":
        from shadowlock.jsonio import export_json

        try:
            rec = export_json(args.path)
        except OSError as exc:
            return _die(str(exc), "shadowlock export report.json")
        except Exception as exc:  # noqa: BLE001
            return _die(str(exc), "shadowlock export report.json")
        if getattr(args, "as_json", False):
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        else:
            sys.stdout.write(format_export_human(rec))
        return 0

    return _die(f'Unknown command "{args.cmd}".', "shadowlock --help")


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


def _emit_report(args: argparse.Namespace, payload: str) -> None:
    if _wants_json(args):
        sys.stdout.write(payload + "\n")
    if getattr(args, "out", None):
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    if not _wants_json(args):
        text = format_report_human(json.loads(payload))
        if getattr(args, "out", None):
            text += f"Wrote {args.out}\n"
        sys.stdout.write(text)


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
        return _die(f"Input not found: {exc}", "shadowlock attach --in jobs.jsonl")
    except (AirgapError, EthicsError, HookError) as exc:
        return _die(str(exc), "shadowlock doctor")
    data = receipt.as_dict()
    if getattr(args, "as_json", False):
        sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(format_attach_human(data))
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
        return _die(f"Input not found: {exc}", "shadowlock observe --in jobs.jsonl")
    except (AirgapError, EthicsError, HookError, SessionForgottenError) as exc:
        return _die(str(exc), "shadowlock doctor")
    _emit_report(args, payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
