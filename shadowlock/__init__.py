"""ShadowLock: a read-only, zero-retention, software-agnostic outcome mirror.

July 2026 whitepaper implementation by Aziel Eliab.

Observes selectively. OS-hooks into AZ-OS for process/job observation
under ethics policy. Computes counterfactual expectations. Reports
financial variance. Forgets everything. Does not control, optimize,
replace, dispatch, schedule, or learn.

Change is optional. Truth is not.

Forks are welcome and always allowed.
"""

from __future__ import annotations

from shadowlock.adapters import CsvAdapter, JsonlAdapter, MemoryAdapter
from shadowlock.azos_hook import (
    PROTOCOL as AZOS_HOOK_PROTOCOL,
    AttachReceipt,
    AzosHookAdapter,
    LocalObserver,
    attach,
)
from shadowlock.counterfactual import Expectation
from shadowlock.envelope import JobEnvelope
from shadowlock.errors import (
    AirgapError,
    EthicsError,
    HookError,
    ReadOnlyError,
    SessionForgottenError,
)
from shadowlock.ethics import EthicsProposal, EthicsResult, evaluate_ethics
from shadowlock.ledger import FinancialLedger
from shadowlock.report import Report
from shadowlock.sample import Sampler
from shadowlock.session import ShadowLockSession

__version__ = "0.2.0"
__author__ = "Aziel Eliab"
__all__ = [
    "AZOS_HOOK_PROTOCOL",
    "AirgapError",
    "AttachReceipt",
    "AzosHookAdapter",
    "CsvAdapter",
    "EthicsError",
    "EthicsProposal",
    "EthicsResult",
    "Expectation",
    "FinancialLedger",
    "HookError",
    "JobEnvelope",
    "JsonlAdapter",
    "LocalObserver",
    "MemoryAdapter",
    "ReadOnlyError",
    "Report",
    "Sampler",
    "SessionForgottenError",
    "ShadowLockSession",
    "attach",
    "evaluate_ethics",
    "__version__",
]
