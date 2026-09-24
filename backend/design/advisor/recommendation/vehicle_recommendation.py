"""
VehicleRecommendation Subsystem

Purpose:
    Defines the `VehicleRecommendation` domain model representing an evaluation finding for a candidate vehicle family.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.advisor.recommendation.vehicle_type import VehicleType
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily
from backend.design.advisor.recommendation.recommendation_score import RecommendationScore
from backend.design.advisor.recommendation.recommendation_reason import RecommendationReason


@dataclass(slots=True)
class VehicleRecommendation:
    """
    Evaluation recommendation for a candidate vehicle family.

    Attributes:
        vehicle_family (VehicleFamily): Target aircraft family (FIXED_WING, MULTIROTOR, VTOL).
        overall_score (float): Normalized suitability score from 0.0 to 1.0.
        confidence (float): Metric confidence rating from 0.0 to 1.0.
        engineering_score (RecommendationScore): Qualitative rating.
        estimated_cost (float): Estimated baseline airframe/propulsion cost in USD.
        estimated_complexity (str): Qualitative complexity rating description.
        pros (list[str]): Key physics-based advantages.
        cons (list[str]): Key engineering drawbacks or limitations.
        reasons (list[RecommendationReason]): Standardized criteria tags.
        metadata (dict[str, Any]): Additional internal scoring calculations.
        vehicle_type (VehicleType | str | None): Legacy vehicle type compatibility attribute.
    """

    vehicle_family: VehicleFamily = VehicleFamily.MULTIROTOR
    overall_score: float = 0.0
    confidence: float = 0.0
    engineering_score: RecommendationScore = RecommendationScore.ACCEPTABLE
    estimated_cost: float = 0.0
    estimated_complexity: str = "Low"
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    reasons: list[RecommendationReason] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    vehicle_type: VehicleType | str | None = None

    def __post_init__(self) -> None:
        if self.vehicle_type is not None:
            v_type_val = self.vehicle_type.value if hasattr(self.vehicle_type, 'value') else str(self.vehicle_type)
            if v_type_val in ("QUADCOPTER", "HEXACOPTER", "OCTOCOPTER", "MULTIROTOR"):
                object.__setattr__(self, "vehicle_family", VehicleFamily.MULTIROTOR)
            elif v_type_val == "FIXED_WING":
                object.__setattr__(self, "vehicle_family", VehicleFamily.FIXED_WING)
            elif v_type_val == "VTOL":
                object.__setattr__(self, "vehicle_family", VehicleFamily.VTOL)

        if self.vehicle_type is None:
            if self.vehicle_family == VehicleFamily.MULTIROTOR:
                object.__setattr__(self, "vehicle_type", VehicleType.QUADCOPTER)
            elif self.vehicle_family == VehicleFamily.FIXED_WING:
                object.__setattr__(self, "vehicle_type", VehicleType.FIXED_WING)
            elif self.vehicle_family == VehicleFamily.VTOL:
                object.__setattr__(self, "vehicle_type", VehicleType.VTOL)
