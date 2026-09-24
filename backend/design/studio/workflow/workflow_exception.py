"""
WorkflowException Subsystem

Purpose:
    Defines exception classes for the Universal Aircraft Design Workflow Engine.

Role in Architecture:
    `WorkflowEngineException` and its subclasses handle recoverable, retryable, and fatal workflow execution errors.
"""


class WorkflowEngineException(ValueError):
    """Base exception class for Workflow Engine errors."""
    pass


class StageExecutionError(WorkflowEngineException):
    """Raised when a workflow stage fails during execution."""
    pass


class StageNotFoundError(WorkflowEngineException, KeyError):
    """Raised when looking up a stage name that is absent from the registry."""
    pass


class FatalWorkflowError(WorkflowEngineException):
    """Raised when an unrecoverable fatal failure occurs terminating the workflow."""
    pass


class RecoverableWorkflowError(WorkflowEngineException):
    """Raised when a non-fatal recoverable failure occurs."""
    pass


class RetryableWorkflowError(WorkflowEngineException):
    """Raised when a transient failure occurs that can be safely retried."""
    pass
