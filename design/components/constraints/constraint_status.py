"""
ConstraintStatus Enumeration Subsystem

Purpose:
    Defines the `ConstraintStatus` enumeration representing overall engineering constraint satisfaction.

Role in Architecture:
    `ConstraintStatus` summarizes whether an aircraft design satisfies all mission constraints, satisfies with warnings, or violates constraints.
"""

from enum import Enum


class ConstraintStatus(str, Enum):
    """
    Engineering constraint satisfaction status classification.

    Members:
        SATISFIED: All mission constraints and physical limits are fully satisfied.
        SATISFIED_WITH_WARNINGS: Constraints satisfied but operating close to structural/thermal limits.
        VIOLATED: One or more critical mission constraints or physical limits are violated.
        UNKNOWN: Insufficient design parameters available to evaluate constraints.
    """
    SATISFIED = "SATISFIED"
    SATISFIED_WITH_WARNINGS = "SATISFIED_WITH_WARNINGS"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"
