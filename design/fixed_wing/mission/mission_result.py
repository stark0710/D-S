"""
Fixed-Wing Mission Result Subsystem

Purpose:
    Defines the `MissionResult` domain model, which encapsulates the output of the mission engineering analysis.

Role in Architecture:
    `MissionResult` is the data structure returned by the `MissionEngine`. It contains the completed mission profile,
    constraints, scoring, recommendations, and warnings for consumption by the next design stage.
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict
from backend.design.fixed_wing.mission.mission_requirements import MissionCategory
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_constraints import MissionConstraints


@dataclass(slots=True)
class MissionResult:
    """
    Canonical output result of the fixed-wing mission engineering workflow.

    Attributes:
        mission_profile (MissionProfile): The processed engineering mission profile.
        mission_category (MissionCategory): Determined class of the mission.
        mission_score (float): Score evaluated by the scoring engine (0.0 to 100.0).
        complexity (str): Assessed mission complexity class (e.g. "Low", "Medium", "High").
        engineering_requirements (Dict[str, Any]): Normalized target requirements mapped for the design studio.
        constraints (MissionConstraints): Consolidated constraints mapping target design spaces.
        recommendations (List[str]): Actionable engineering recommendations generated during analysis.
        warnings (List[str]): Validation warnings or operational risk notifications.
        metadata (Dict[str, Any]): Performance metadata, software version info, timestamps, etc.
    """

    mission_profile: MissionProfile
    mission_category: MissionCategory
    mission_score: float
    complexity: str
    engineering_requirements: Dict[str, Any]
    constraints: MissionConstraints
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def mission_summary(self) -> Dict[str, Any]:
        """Provides a standardized summary dictionary of the mission profile."""
        cat = self.mission_category.value if hasattr(self.mission_category, "value") else str(self.mission_category)
        mp = self.mission_profile
        return {
            "category": cat,
            "payload_kg": getattr(mp, "payload_kg", 0.0),
            "flight_time_min": getattr(mp, "flight_time_min", 0.0),
            "cruise_speed_kmh": getattr(mp, "cruise_speed_kmh", 0.0),
            "mission_range_km": getattr(mp, "mission_range_km", 0.0),
        }
