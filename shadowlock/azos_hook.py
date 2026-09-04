"""AZ-OS hook: IPC/API attach + local observer.

ShadowLock OS-hooks into AZ-OS for process/job observation under
ethics policy. It does not intercept the caller kernel, does not
ptrace, and does not control processes.

IPC:
  * Loopback HTTP to AZ Interface (127.0.0.1:8800) — the AZ-OS API.
  * Optional Unix-domain JSON frame for a local observer socket.

The hosted AZ-OS Worker is overlay labels only (not a remote shell).
Air-gap refuses hosted attach.

Author: Aziel Eliab.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, Sequence
from urllib.parse import urlparse

from shadowlock.adapters import MemoryAdapter, ReadOnlyAdapter, record_to_envelope
from shadowlock.envelope import JobEnvelope
from shadowlock.errors import AirgapError, EthicsError, HookError
from shadowlock.ethics import (
    AUTHOR,
    AZOS_SAFE_ATTACH_ACTION,
    DEFAULT_OBSERVE_PROPOSAL,
    MOTTO,
    EthicsProposal,
    EthicsResult,
    evaluate_ethics,
)
from shadowlock.report import Report
from shadowlock.session import ShadowLockSession, assert_airgap

PROTOCOL = "azos-shadowlock-hook/1"
PRODUCT = "ShadowLock"
AZOS_LOOPBACK_HOST = "127.0.0.1"
AZOS_LOOPBACK_PORT = 8800
AZOS_HOSTED = "https://azos-download-tracker.vibelock.workers.dev"
USER_AGENT = "Mozilla/5.0"
INVITE = (
    "AZ-OS is not running on this computer. "
    "Install and run `azos ui` (http://127.0.0.1:8800), then attach again. "
    "Author Aziel Eliab. Integrity precedes execution."
)


def _json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def encode_frame(
    kind: str,
    *,
    ethics: Mapping[str, Any] | None = None,
    jobs: Sequence[Mapping[str, Any]] | None = None,
    processes: Sequence[Mapping[str, Any]] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one hook frame (HTTP body or Unix JSON line)."""
    frame: dict[str, Any] = {
        "protocol": PROTOCOL,
        "kind": kind,
        "product": "shadowlock",
        "author": AUTHOR,
        "ethics": dict(ethics or DEFAULT_OBSERVE_PROPOSAL),
    }
    if jobs is not None:
        frame["jobs"] = [dict(j) for j in jobs]
    if processes is not None:
        frame["processes"] = [dict(p) for p in processes]
    if extra:
        frame.update(dict(extra))
    return frame


def decode_frame(raw: Any) -> dict[str, Any]:
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        raw = json.loads(raw or "{}")
    if not isinstance(raw, dict):
        raise HookError("hook frame must be a JSON object")
    return raw


def records_from_frame(frame: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Collect job/process records from a hook frame. PII is dropped later."""
    out: list[dict[str, Any]] = []
    for key in ("jobs", "processes", "records"):
        block = frame.get(key)
        if isinstance(block, list):
            for rec in block:
                if isinstance(rec, Mapping):
                    out.append(dict(rec))
    observed = frame.get("observed")
    if isinstance(observed, Mapping):
        out.append(dict(observed))
    elif isinstance(observed, list):
        for rec in observed:
            if isinstance(rec, Mapping):
                out.append(dict(rec))
    return out


def records_from_azos_status(status: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Map an AZ-OS overlay status receipt into one job-shaped record."""
    overlay = str(status.get("overlay") or status.get("overlay_name") or "AZ-OS")
    session = str(status.get("session") or status.get("product") or overlay)
    halted = bool(status.get("halted"))
    lumen = str(status.get("lumen") or "unknown")
    return [
        {
            "id": f"azos-overlay:{session}",
            "task_class": "azos-overlay",
            "urgency": 1.0 if halted else 0.25,
            "actual_outcome": "halted" if halted else "running",
            "actual_duration": 0,
            "actual_cost": 0,
            "actual_revenue": 0,
            "context_signals": {
                "overlay": overlay,
                "lumen": lumen,
                "kernel": bool(status.get("kernel")),
                "source": "azos-status",
            },
        }
    ]


def records_from_azos_log(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Map AZ-OS exec-log rows into job-shaped records. No raw tokens."""
    out: list[dict[str, Any]] = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        action = str(entry.get("action") or entry.get("name") or "exec")
        hid = str(entry.get("token_hash") or entry.get("id") or f"log-{i}")
        out.append(
            {
                "id": f"azos-log:{hid}",
                "task_class": "azos-exec",
                "urgency": 0.5,
                "actual_outcome": action,
                "actual_duration": 0,
                "actual_cost": 0,
                "actual_revenue": 0,
                "context_signals": {
                    "source": "azos-log",
                    "action": action,
                },
            }
        )
    return out


def send_unix_frame(path: str, frame: Mapping[str, Any], *, timeout: float = 2.0) -> dict[str, Any]:
    """One JSON request / JSON reply over a Unix-domain socket."""
    payload = _json_bytes(dict(frame)) + b"\n"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(path)
        sock.sendall(payload)
        chunks: list[bytes] = []
        while True:
            try:
                piece = sock.recv(65536)
            except TimeoutError as exc:
                raise HookError(f"unix hook timeout: {path}") from exc
            if not piece:
                break
            chunks.append(piece)
            if b"\n" in piece:
                break
        raw = b"".join(chunks).split(b"\n", 1)[0]
        if not raw:
            raise HookError("unix hook returned an empty frame")
        return decode_frame(raw)
    except OSError as exc:
        raise HookError(f"unix hook failed: {exc}") from exc
    finally:
        sock.close()


def serve_unix_once(path: str, reply: Mapping[str, Any], *, timeout: float = 2.0) -> dict[str, Any]:
    """Accept one Unix client, read a frame, write ``reply``. Test/local IPC."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.bind(path)
        sock.listen(1)
        conn, _addr = sock.accept()
        try:
            conn.settimeout(timeout)
            chunks: list[bytes] = []
            while True:
                piece = conn.recv(65536)
                if not piece:
                    break
                chunks.append(piece)
                if b"\n" in piece:
                    break
            incoming = decode_frame(b"".join(chunks).split(b"\n", 1)[0])
            conn.sendall(_json_bytes(dict(reply)) + b"\n")
            return incoming
        finally:
            conn.close()
    except OSError as exc:
        raise HookError(f"unix hook listen failed: {exc}") from exc
    finally:
        sock.close()


class AzosClient:
    """Stdlib HTTP client for AZ Interface (loopback) or hosted labels."""

    def __init__(
        self,
        host: str = AZOS_LOOPBACK_HOST,
        port: int = AZOS_LOOPBACK_PORT,
        *,
        hosted: bool = False,
        timeout: float = 2.0,
        opener: Any | None = None,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.hosted = bool(hosted)
        self.timeout = timeout
        self._opener = opener

    def base_url(self) -> str:
        if self.hosted:
            return AZOS_HOSTED.rstrip("/")
        return f"http://{self.host}:{self.port}"

    def _open(self, req: urllib.request.Request):
        if self._opener is not None:
            return self._opener.open(req, timeout=self.timeout)
        return urllib.request.urlopen(req, timeout=self.timeout)

    def request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = self.base_url() + path
        data = None if body is None else _json_bytes(body)
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self._open(req) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                parsed = json.loads(raw)
        except urllib.error.HTTPError as exc:
            try:
                parsed = json.loads(exc.read().decode("utf-8") or "{}")
            except (OSError, json.JSONDecodeError):
                parsed = {"error": str(exc)}
            if not isinstance(parsed, dict):
                parsed = {"error": str(exc)}
            parsed.setdefault("http_status", exc.code)
            if exc.code >= 500:
                raise HookError(f"AZ-OS HTTP {exc.code} at {path}") from exc
            return parsed
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            raise HookError(INVITE) from exc
        except json.JSONDecodeError as exc:
            raise HookError("AZ-OS returned non-JSON") from exc
        if not isinstance(parsed, dict):
            raise HookError("AZ-OS returned a non-object")
        return parsed

    def status(self) -> dict[str, Any]:
        if self.hosted:
            return self.request("POST", "/v1/status", {})
        try:
            return self.request("GET", "/api/status")
        except HookError:
            return self.request("POST", "/v1/status", {})

    def request_token(self, proposal: EthicsProposal) -> dict[str, Any]:
        return self.request("POST", "/api/request", proposal.as_azos_request())

    def exec_status(self, token: str | None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": AZOS_SAFE_ATTACH_ACTION}
        if token:
            body["token"] = token
        return self.request("POST", "/api/exec", body)

    def log(self) -> list[dict[str, Any]]:
        payload = self.request("GET", "/api/log")
        entries = payload.get("entries")
        if isinstance(entries, list):
            return [e for e in entries if isinstance(e, dict)]
        return []


@dataclass
class AttachReceipt:
    attached: bool
    ethics: EthicsResult
    azos: dict[str, Any] = field(default_factory=dict)
    jobs: list[dict[str, Any]] = field(default_factory=list)
    invite: str | None = None
    token_preview: str | None = None
    protocol: str = PROTOCOL
    author: str = AUTHOR
    product: str = PRODUCT

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.attached,
            "attached": self.attached,
            "protocol": self.protocol,
            "author": self.author,
            "product": self.product,
            "motto": MOTTO,
            "ethics": self.ethics.as_dict(),
            "azos": dict(self.azos),
            "job_count": len(self.jobs),
            "invite": self.invite,
            "token_preview": self.token_preview,
            "kernel": False,
            "intercepts_caller_os": False,
        }


class AzosHookAdapter(ReadOnlyAdapter):
    """Read-only jobs already collected through an AZ-OS attach."""

    def __init__(self, records: Sequence[Mapping[str, Any]]):
        self._records = [dict(r) for r in records]

    def iter_jobs(self, salt: str) -> Iterator[JobEnvelope]:
        for rec in self._records:
            yield record_to_envelope(rec, salt)


class LocalObserver:
    """Attach to AZ-OS, then observe jobs/processes under ethics policy."""

    def __init__(
        self,
        *,
        host: str = AZOS_LOOPBACK_HOST,
        port: int = AZOS_LOOPBACK_PORT,
        hosted: bool = False,
        airgap: bool = False,
        timeout: float = 2.0,
        client: AzosClient | None = None,
        salt: str | None = None,
    ) -> None:
        if airgap:
            assert_airgap()
        if airgap and hosted:
            raise AirgapError("air-gap refuses hosted AZ-OS attach")
        parsed = urlparse(host) if "://" in host else None
        if parsed and parsed.hostname:
            host = parsed.hostname
        self.host = host
        self.port = int(port)
        self.hosted = bool(hosted)
        self.airgap = bool(airgap)
        self.salt = salt
        self.client = client or AzosClient(
            host=self.host, port=self.port, hosted=self.hosted, timeout=timeout
        )
        self.receipt: AttachReceipt | None = None

    def attach(
        self,
        ethics: Mapping[str, Any] | None = None,
        extra_jobs: Sequence[Mapping[str, Any]] | None = None,
        *,
        live: bool = True,
    ) -> AttachReceipt:
        proposal = EthicsProposal.from_mapping(ethics)
        result = evaluate_ethics(proposal.as_dict())
        if not result.passed:
            self.receipt = AttachReceipt(
                attached=False,
                ethics=result,
                invite="ethics policy refused this observation",
            )
            raise EthicsError("AZ-OS ethics policy refused this observation")

        jobs: list[dict[str, Any]] = []
        if extra_jobs:
            jobs.extend(dict(j) for j in extra_jobs)

        azos: dict[str, Any] = {}
        token_preview = None
        invite = None
        attached = not live

        if live:
            try:
                status = self.client.status()
                azos = dict(status)
                if status.get("halted"):
                    raise HookError("AZ-OS overlay is halted; observation is refused")
                jobs.extend(records_from_azos_status(status))
                attached = True
                if not self.hosted:
                    try:
                        token_body = self.client.request_token(proposal)
                    except HookError:
                        token_body = {}
                    azos["request"] = {
                        k: token_body[k]
                        for k in token_body
                        if k in {"passed", "gates", "http_status"}
                    }
                    if token_body.get("passed") or token_body.get("token"):
                        token = token_body.get("token")
                        token_preview = token_body.get("token_preview")
                        if isinstance(token, str) and token:
                            token_preview = token[:8] + "…"
                        try:
                            exec_out = self.client.exec_status(
                                str(token) if token else None
                            )
                            result_obj = exec_out.get("result")
                            if isinstance(result_obj, dict):
                                jobs.extend(records_from_azos_status(result_obj))
                                azos.setdefault("exec", result_obj)
                        except HookError:
                            pass
                    elif token_body.get("invite"):
                        invite = str(token_body.get("invite"))
                    try:
                        jobs.extend(records_from_azos_log(self.client.log()))
                    except HookError:
                        pass
            except HookError as exc:
                self.receipt = AttachReceipt(
                    attached=False,
                    ethics=result,
                    azos=azos,
                    jobs=jobs,
                    invite=str(exc),
                )
                raise

        if not attached and live:
            self.receipt = AttachReceipt(
                attached=False,
                ethics=result,
                azos=azos,
                jobs=jobs,
                invite=invite or INVITE,
                token_preview=token_preview,
            )
            raise HookError(invite or INVITE)

        self.receipt = AttachReceipt(
            attached=True,
            ethics=result,
            azos=azos,
            jobs=jobs,
            token_preview=token_preview,
        )
        return self.receipt

    def observe(
        self,
        extra_jobs: Sequence[Mapping[str, Any]] | None = None,
        *,
        salt: str | None = None,
    ) -> Report:
        if self.receipt is None or not self.receipt.attached:
            raise HookError("attach via AZ-OS before observe")
        records = list(self.receipt.jobs)
        if extra_jobs:
            records.extend(dict(j) for j in extra_jobs)
        adapter: ReadOnlyAdapter
        if records:
            adapter = AzosHookAdapter(records)
        else:
            adapter = MemoryAdapter([])
        with ShadowLockSession(
            salt=salt if salt is not None else self.salt,
            airgap=self.airgap,
        ) as session:
            return session.observe(adapter)

    def detach(self) -> None:
        self.receipt = None


def attach(
    *,
    host: str = AZOS_LOOPBACK_HOST,
    port: int = AZOS_LOOPBACK_PORT,
    hosted: bool = False,
    airgap: bool = False,
    ethics: Mapping[str, Any] | None = None,
    extra_jobs: Sequence[Mapping[str, Any]] | None = None,
    live: bool = True,
    client: AzosClient | None = None,
) -> AttachReceipt:
    observer = LocalObserver(
        host=host, port=port, hosted=hosted, airgap=airgap, client=client
    )
    return observer.attach(ethics=ethics, extra_jobs=extra_jobs, live=live)
