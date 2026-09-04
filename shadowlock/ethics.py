"""AZ-OS ethics policy for ShadowLock observation.

Integrity precedes execution. Observation is read-only. Default deny.

Five gates (same shape as AZ-OS / DecisionGATE): definition, evidence,
impact, integrity, responsibility. Any FAIL → no attach, no observe.

This module does not issue ARC tokens and does not exec. It only labels
whether a proposed observation may proceed under ethics policy.
Author: Aziel Eliab.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

GATES = (
    "definition",
    "evidence",
    "impact",
    "integrity",
    "responsibility",
)

MOTTO = "Integrity precedes execution."
AUTHOR = "Aziel Eliab"
PRODUCT = "ShadowLock"

# Observation-only. Never halt, purge, dispatch, or control a process.
OBSERVE_ACTIONS = frozenset({"observe", "status", "list_modules"})

# AZ-OS maps ShadowLock observe → this safe builtin when requesting a token.
AZOS_SAFE_ATTACH_ACTION = "status"

_MIN = 8
_BANNED_IMPACT = (
    "wipe disk",
    "format drive",
    "mkfs",
    "self-replicate",
    "worm",
    "dispatch",
    "scheduler",
    "kill process",
    "remote takeover",
    "remote machine takeover",
)

DEFAULT_OBSERVE_PROPOSAL: dict[str, Any] = {
    "action": "observe",
    "definition": "Read-only ShadowLock observation of jobs or processes already surfaced by AZ-OS.",
    "evidence": "Operator requested an AZ-OS ethics-gated attach for a zero-retention outcome mirror.",
    "impact": "No host writes, no dispatch, no process control; anonymous aggregates only.",
    "actor": "operator",
    "extend_module": False,
    "comprehension": True,
    "intent": "Observe finished jobs through AZ-OS under Integrity precedes execution.",
}

PRINCIPLES = (
    "Integrity precedes execution.",
    "Time-bound actions are final.",
    "Understanding precedes modification.",
    "The system protects itself architecturally.",
    "Propagation is invitation, not infection.",
    "ShadowLock observes; it does not control.",
)


@dataclass
class EthicsProposal:
    """A proposed observation presented to the five gates."""

    action: str
    definition: str = ""
    evidence: str = ""
    impact: str = ""
    actor: str = ""
    extend_module: bool = False
    comprehension: bool = False
    intent: str = ""

    @classmethod
    def observe(cls, **overrides: Any) -> "EthicsProposal":
        data = dict(DEFAULT_OBSERVE_PROPOSAL)
        data.update(overrides)
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "EthicsProposal":
        src = dict(DEFAULT_OBSERVE_PROPOSAL if data is None else data)
        return cls(
            action=str(src.get("action") or ""),
            definition=str(src.get("definition") or ""),
            evidence=str(src.get("evidence") or ""),
            impact=str(src.get("impact") or ""),
            actor=str(src.get("actor") or ""),
            extend_module=bool(src.get("extend_module")),
            comprehension=bool(src.get("comprehension")),
            intent=str(src.get("intent") or ""),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "definition": self.definition,
            "evidence": self.evidence,
            "impact": self.impact,
            "actor": self.actor,
            "extend_module": self.extend_module,
            "comprehension": self.comprehension,
            "intent": self.intent,
        }

    def as_azos_request(self) -> dict[str, Any]:
        """Shape AZ-OS /api/request accepts. Observe maps to a safe builtin."""
        payload = self.as_dict()
        if payload["action"] == "observe":
            payload["action"] = AZOS_SAFE_ATTACH_ACTION
        return payload


@dataclass
class GateCheck:
    passed: bool
    reason: str


@dataclass
class EthicsResult:
    passed: bool
    gates: dict[str, GateCheck] = field(default_factory=dict)
    motto: str = MOTTO
    author: str = AUTHOR
    product: str = PRODUCT

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "motto": self.motto,
            "author": self.author,
            "product": self.product,
            "principles": list(PRINCIPLES),
            "gates": {
                name: {"pass": c.passed, "reason": c.reason}
                for name, c in self.gates.items()
            },
        }


def _filled(value: str, minimum: int = _MIN) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def authorize(proposal: EthicsProposal) -> EthicsResult:
    """Evaluate all five gates. Does not short-circuit."""
    action = (proposal.action or "").strip()
    checks: dict[str, GateCheck] = {}

    if not action:
        checks["definition"] = GateCheck(False, "action name is required")
    elif not _filled(proposal.definition):
        checks["definition"] = GateCheck(
            False, "definition must state what the action is (min 8 chars)"
        )
    else:
        checks["definition"] = GateCheck(True, "action is defined")

    if not _filled(proposal.evidence):
        checks["evidence"] = GateCheck(
            False, "evidence / justification is required (min 8 chars)"
        )
    else:
        checks["evidence"] = GateCheck(True, "evidence provided")

    impact = (proposal.impact or "").strip().lower()
    if not _filled(proposal.impact):
        checks["impact"] = GateCheck(
            False, "impact must state what will change (min 8 chars)"
        )
    elif any(b in impact for b in _BANNED_IMPACT):
        checks["impact"] = GateCheck(False, "impact violates overlay bounds")
    else:
        checks["impact"] = GateCheck(True, "impact stated")

    integrity_ok = True
    integrity_reason = "action is a registered observation"
    if action not in OBSERVE_ACTIONS:
        integrity_ok = False
        integrity_reason = "unsigned / unregistered action: default deny"
    if proposal.extend_module:
        if not proposal.comprehension:
            integrity_ok = False
            integrity_reason = "extending a module requires the comprehension checkbox"
        elif not _filled(proposal.intent, 12):
            integrity_ok = False
            integrity_reason = "extending a module requires a short restatement of intent"
        elif action not in OBSERVE_ACTIONS:
            integrity_ok = False
            integrity_reason = "understood, but unsigned modules cannot run (integrity)"
    checks["integrity"] = GateCheck(integrity_ok, integrity_reason)

    actor = (proposal.actor or "").strip()
    if not actor:
        checks["responsibility"] = GateCheck(False, "a named actor is required")
    else:
        checks["responsibility"] = GateCheck(
            True, f"actor {actor!r} is named (name is not a privilege)"
        )

    passed = all(c.passed for c in checks.values())
    return EthicsResult(passed=passed, gates=checks)


def evaluate_ethics(data: Mapping[str, Any] | None = None) -> EthicsResult:
    """Authorize an observation mapping. None → the default observe proposal."""
    return authorize(EthicsProposal.from_mapping(data))
