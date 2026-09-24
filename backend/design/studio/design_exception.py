"""
DesignException Subsystem

Purpose:
    Defines exception classes for the Aircraft Design Studio framework.

Role in Architecture:
    `StudioDesignException` and its subclasses handle workflow execution failures, stage transition errors,
    and design session lookup errors across all design studios.
"""


class StudioDesignException(ValueError):
    """Base exception class for Design Studio errors."""
    pass


class WorkflowExecutionError(StudioDesignException):
    """Raised when a design workflow stage execution fails."""
    pass


class StageTransitionError(StudioDesignException):
    """Raised when an invalid or out-of-order stage transition is attempted."""
    pass


class SessionNotFoundError(StudioDesignException, KeyError):
    """Raised when looking up a session ID that is absent from active design sessions."""
    pass
