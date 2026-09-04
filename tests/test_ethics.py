"""AZ-OS ethics policy: default observe passes; control actions deny."""

from __future__ import annotations

from shadowlock.ethics import (
    DEFAULT_OBSERVE_PROPOSAL,
    EthicsProposal,
    evaluate_ethics,
)


def test_default_observe_passes() -> None:
    result = evaluate_ethics(None)
    assert result.passed is True
    assert result.author == "Aziel Eliab"
    assert result.motto == "Integrity precedes execution."
    assert set(result.gates) == {
        "definition",
        "evidence",
        "impact",
        "integrity",
        "responsibility",
    }
    assert all(c.passed for c in result.gates.values())


def test_unsigned_action_denied() -> None:
    result = evaluate_ethics({**DEFAULT_OBSERVE_PROPOSAL, "action": "purge_session"})
    assert result.passed is False
    assert result.gates["integrity"].passed is False


def test_banned_impact_denied() -> None:
    result = evaluate_ethics({**DEFAULT_OBSERVE_PROPOSAL, "impact": "wipe disk and continue"})
    assert result.passed is False
    assert result.gates["impact"].passed is False


def test_honest_no_control_impact_still_passes() -> None:
    result = evaluate_ethics({**DEFAULT_OBSERVE_PROPOSAL, "impact": "No host writes and no process control; anonymous aggregates only."})
    assert result.passed is True


def test_missing_actor_denied() -> None:
    result = evaluate_ethics({**DEFAULT_OBSERVE_PROPOSAL, "actor": ""})
    assert result.passed is False
    assert result.gates["responsibility"].passed is False


def test_azos_request_maps_observe_to_status() -> None:
    proposal = EthicsProposal.observe()
    req = proposal.as_azos_request()
    assert req["action"] == "status"
    assert "Read-only" in req["definition"]
