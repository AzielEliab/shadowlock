"""forget() drops job payloads; observe after forget raises."""

from __future__ import annotations

import pytest

from shadowlock.adapters import MemoryAdapter
from shadowlock.errors import SessionForgottenError
from shadowlock.session import ShadowLockSession


def test_forget_clears_session_jobs(jobs: list[dict], salt: str) -> None:
    session = ShadowLockSession(salt=salt)
    report = session.observe(MemoryAdapter(jobs))
    assert report.sampled >= 1
    assert session.held_payload_count() == report.sampled
    payloads = list(session._envelopes)
    assert payloads
    session.forget()
    assert session.held_payload_count() == 0
    assert session._envelopes == []
    assert session.forgotten is True
    # prior rows gone too
    assert session._prior._rows == []


def test_observe_after_forget_raises(jobs: list[dict], salt: str) -> None:
    session = ShadowLockSession(salt=salt)
    session.observe(MemoryAdapter(jobs))
    session.forget()
    with pytest.raises(SessionForgottenError):
        session.observe(MemoryAdapter(jobs))


def test_context_manager_forgets(jobs: list[dict], salt: str) -> None:
    with ShadowLockSession(salt=salt) as session:
        session.observe(MemoryAdapter(jobs))
        assert session.held_payload_count() >= 1
    assert session.forgotten is True
    assert session.held_payload_count() == 0
