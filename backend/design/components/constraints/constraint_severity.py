"""
ConstraintSeverity Enumeration Subsystem

Purpose:
    Defines the `ConstraintSeverity` enumeration representing severity levels of constraint findings.

Role in Architecture:
    `ConstraintSeverity` categorizes constraint findings into INFO, WARNING, or CRITICAL violations.
"""

from enum import Enum


class ConstraintSeverity(str, Enum):
    """
    Constraint finding severity level classification.

    Members:
        INFO: Informational observation or margin note.
        WARNING: Non-critical performance shortfall or operating limit advisory.
        CRITICAL: Unacceptable requirement violation or physical safety limit breach.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
