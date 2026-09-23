"""
CompatibilitySeverity Enumeration Subsystem

Purpose:
    Defines the `CompatibilitySeverity` enumeration representing severity levels of compatibility findings.

Role in Architecture:
    `CompatibilitySeverity` categorizes issues identified during compatibility checks (INFO, WARNING, CRITICAL).
"""

from enum import Enum


class CompatibilitySeverity(str, Enum):
    """
    Compatibility issue severity classification.

    Members:
        INFO: Informational observation or efficiency note.
        WARNING: Non-critical incompatibility or minor performance penalty.
        CRITICAL: Catastrophic incompatibility leading to hardware failure or fire hazard.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
