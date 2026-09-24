"""
OptimizationProfile Subsystem

Purpose:
    Defines the `OptimizationProfile` domain model representing optimization target profile parameters.

Role in Architecture:
    `OptimizationProfile` specifies primary objective ('MAXIMIZE_ENDURANCE', 'MAXIMIZE_RANGE', 'MAXIMIZE_PAYLOAD', 'MINIMIZE_MASS', 'BALANCED'),
    target improvement percentage, and maximum iteration count.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationProfile:
    """
    Multirotor optimization goal specification profile.

    Attributes:
        primary_objective (str): Target optimization objective string.
        target_improvement_percent (float): Target performance gain in % (e.g. 15.0%).
        max_iterations (int): Maximum optimization search iterations.
        metadata (dict[str, Any]): Additional profile metadata.
    """

    primary_objective: str = "MAXIMIZE_ENDURANCE"
    target_improvement_percent: float = 15.0
    max_iterations: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)
