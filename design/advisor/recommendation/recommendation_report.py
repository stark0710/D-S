"""
RecommendationReport Subsystem

Purpose:
    Defines the `RecommendationReport` domain model representing the aggregated vehicle family recommendation output.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from backend.design.advisor.recommendation.vehicle_type import VehicleType
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily
from backend.design.advisor.recommendation.selection_status import SelectionStatus
from backend.design.advisor.recommendation.mission_feasibility import MissionFeasibilityResult
from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation


@dataclass(slots=True)
class RecommendationReport:
    """
    Aggregated vehicle family recommendation report.

    Attributes:
        recommendations (list[VehicleRecommendation]): Ranked list of candidate vehicle evaluations.
        recommended_vehicle (VehicleType | VehicleFamily): Top-ranked recommended aircraft category/family.
        summary (str): Transparent, human-readable summary explaining recommendation status and rationale.
        status (SelectionStatus): Outcome selection status (SELECTED, INVALID_REQUIREMENTS, NO_FEASIBLE_SOLUTION).
        selected_family (VehicleFamily | None): Top selected aircraft family if status == SELECTED.
        family_scores (Dict[VehicleFamily, float]): Scores for evaluated eligible families.
        eligible_families (List[VehicleFamily]): List of families meeting hard eligibility constraints.
        eliminated_families (Dict[VehicleFamily, str]): Map of eliminated families to elimination reasons.
        feasibility (MissionFeasibilityResult | None): Feasibility analysis outcome.
        engineering_notes (list[str]): Detailed technical notes on trade-offs and physics considerations.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    recommendations: list[VehicleRecommendation]
    recommended_vehicle: VehicleType | VehicleFamily | Any
    summary: str
    status: SelectionStatus = SelectionStatus.SELECTED
    selected_family: VehicleFamily | None = None
    family_scores: Dict[VehicleFamily, float] = field(default_factory=dict)
    eligible_families: List[VehicleFamily] = field(default_factory=list)
    eliminated_families: Dict[VehicleFamily, str] = field(default_factory=dict)
    feasibility: MissionFeasibilityResult | None = None
    engineering_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.selected_family is None and self.recommendations:
            object.__setattr__(self, "selected_family", self.recommendations[0].vehicle_family)
