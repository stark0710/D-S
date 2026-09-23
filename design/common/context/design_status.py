"""
DesignStatus Enumeration Subsystem

Purpose:
    Defines the `DesignStatus` enumeration representing execution status of a design context.

Role in Architecture:
    `DesignStatus` tracks whether a `DesignContext` is active, waiting for user approval, completed, or failed.
"""

from enum import Enum


class DesignStatus(str, Enum):
    """
    Design stage execution status.

    Members:
        CREATED: Context newly initialized; processing not started.
        IN_PROGRESS: Stage processing actively executing.
        WAITING_FOR_USER: Execution paused waiting for user input/approval (e.g. category selection).
        COMPLETED: Current stage or entire design process completed successfully.
        FAILED: Execution aborted due to validation or sizing error.
        CANCELLED: Process terminated by user intervention.
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
