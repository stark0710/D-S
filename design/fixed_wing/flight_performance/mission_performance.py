"""
Fixed-Wing Mission Performance Evaluation Subsystem

Purpose:
    Defines the `MissionPerformance` class.

Role in Architecture:
    `MissionPerformance` holds mission completion probability and energy margins.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class MissionPerformance:
    """
    Flight mission capability metrics.

    Attributes:
        mission_completion_probability (float): Sized percentage rating for completing strategy (0.0 to 100.0).
        critical_phase_suitability (str): Qualitative checklist check.
        energy_margin_pct (float): Battery energy reserve percentage.
        metadata (Dict[str, Any]): Range and climb margins.
    """

    mission_completion_probability: float
    critical_phase_suitability: str
    energy_margin_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
