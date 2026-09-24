"""
CompatibilityStatus Enumeration Subsystem

Purpose:
    Defines the `CompatibilityStatus` enumeration representing component set compatibility statuses.

Role in Architecture:
    `CompatibilityStatus` summarizes whether a set of hardware components is compatible, compatible with warnings, incompatible, or unknown.
"""

from enum import Enum


class CompatibilityStatus(str, Enum):
    """
    Component compatibility status classification.

    Members:
        COMPATIBLE: Components are fully compatible with zero engineering issues.
        COMPATIBLE_WITH_WARNINGS: Components can operate together but exhibit minor sub-optimal trade-offs or warnings.
        INCOMPATIBLE: Components exhibit severe electrical, physical, or thermal incompatibility (unsafe).
        UNKNOWN: Insufficient parameters available to evaluate compatibility.
    """
    COMPATIBLE = "COMPATIBLE"
    COMPATIBLE_WITH_WARNINGS = "COMPATIBLE_WITH_WARNINGS"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"
