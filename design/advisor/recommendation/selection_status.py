"""
SelectionStatus Enumeration Subsystem

Purpose:
    Defines the `SelectionStatus` enumeration representing outcome status of vehicle family selection.

Role in Architecture:
    `SelectionStatus` explicitly separates valid family selection from invalid input or infeasible mission states.
"""

from enum import Enum


class SelectionStatus(str, Enum):
    """
    Vehicle selection process status outcome.

    Members:
        SELECTED: One aircraft family was successfully selected.
        INVALID_REQUIREMENTS: User input failed requirement validation rules.
        NO_FEASIBLE_SOLUTION: Mission requirements exceed engineering design limits.
        INSUFFICIENT_INFORMATION: Requirements lack necessary data to decide suitability.
    """
    SELECTED = "SELECTED"
    INVALID_REQUIREMENTS = "INVALID_REQUIREMENTS"
    NO_FEASIBLE_SOLUTION = "NO_FEASIBLE_SOLUTION"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
