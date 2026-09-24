"""
OptimizationRequirements Subsystem

Purpose:
    Defines the `OptimizationRequirements` domain model representing input requirements for design optimization.

Role in Architecture:
    `OptimizationRequirements` specifies optimization objectives list, target endurance gain min, and cost limit constraint.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationRequirements:
    """
    Multirotor design optimization requirements model.

    Attributes:
        objectives (list[str]): List of optimization objective names.
        target_endurance_gain_min (float): Target endurance gain in minutes (default 5.0).
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    objectives: list[str] = field(default_factory=lambda: ["MAXIMIZE_ENDURANCE", "MINIMIZE_MASS"])
    target_endurance_gain_min: float = 5.0
    metadata: dict[str, Any] = field(default_factory=dict)
