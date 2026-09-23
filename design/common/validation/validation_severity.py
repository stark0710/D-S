"""
ValidationSeverity Enumeration Subsystem

Purpose:
    Defines the `ValidationSeverity` enumeration representing validation issue severity levels.

Role in Architecture:
    `ValidationSeverity` categorizes issues identified during requirement validation.
    `ERROR` blocks progression to Mission Analysis, while `WARNING` and `INFO` provide advisory notes.
"""

from enum import Enum


class ValidationSeverity(str, Enum):
    """
    Validation issue severity classification.

    Members:
        INFO: Informational observation or advisory suggestion.
        WARNING: Sub-optimal requirement choice or boundary note (non-blocking).
        ERROR: Severe requirement error or violation (blocks mission analysis).
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
