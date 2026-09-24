"""
MissionFeasibility Domain Model Subsystem

Purpose:
    Defines the `MissionFeasibilityResult` model representing the physical feasibility assessment of a mission profile.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class MissionFeasibilityResult:
    """
    Structured outcome of the Mission Feasibility Assessment layer.

    Attributes:
        is_feasible (bool): True if mission profile is physically achievable within studio design envelopes.
        confidence (float): Assessment confidence score (0.0 to 1.0).
        limiting_factors (List[str]): Primary physical parameters violating design limits.
        reasons (List[str]): Engineering rationale explaining feasibility status.
        warnings (List[str]): Operational advisory warnings for near-limit boundaries.
    """
    is_feasible: bool
    confidence: float = 1.0
    limiting_factors: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
