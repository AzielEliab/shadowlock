"""ShadowLock errors."""

from __future__ import annotations


class ShadowLockError(Exception):
    """Base error."""


class ReadOnlyError(ShadowLockError):
    """Raised when a write/control method is requested on an adapter."""


class SessionForgottenError(ShadowLockError):
    """Raised when observe/report is requested after forget()."""


class AirgapError(ShadowLockError):
    """Raised when --airgap is set but proxy environment variables are present."""


class EthicsError(ShadowLockError):
    """Raised when the AZ-OS ethics policy refuses an observation."""


class HookError(ShadowLockError):
    """Raised when the AZ-OS hook cannot attach or exchange a frame."""
