"""
Recommendation package for Torq Wings Design Studio Phase 5.1 Common Design Platform.
"""

from backend.design.advisor.recommendation.vehicle_type import VehicleType
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily
from backend.design.advisor.recommendation.selection_status import SelectionStatus
from backend.design.advisor.recommendation.mission_feasibility import MissionFeasibilityResult
from backend.design.advisor.recommendation.mission_feasibility_assessor import MissionFeasibilityAssessor
from backend.design.advisor.recommendation.family_eligibility_analyzer import FamilyEligibilityAnalyzer
from backend.design.advisor.recommendation.recommendation_score import RecommendationScore
from backend.design.advisor.recommendation.recommendation_reason import RecommendationReason
from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation
from backend.design.advisor.recommendation.recommendation_report import RecommendationReport
from backend.design.advisor.recommendation.recommendation_strategy import (
    RecommendationStrategy,
    MultirotorFamilyStrategy,
    FixedWingFamilyStrategy,
    VTOLFamilyStrategy,
    QuadcopterRecommendationStrategy,
    HexacopterRecommendationStrategy,
    OctocopterRecommendationStrategy,
    FixedWingRecommendationStrategy,
    VTOLRecommendationStrategy,
)
from backend.design.advisor.recommendation.recommendation_ranker import RecommendationRanker
from backend.design.advisor.recommendation.recommendation_explanation_service import RecommendationExplanationService
from backend.design.advisor.recommendation.recommendation_pipeline import RecommendationPipeline
from backend.design.advisor.recommendation.recommendation_engine import (
    RecommendationEngine,
    RecommendationEngineError,
    MissingMissionProfileError,
)

__all__ = [
    "VehicleType",
    "VehicleFamily",
    "SelectionStatus",
    "MissionFeasibilityResult",
    "MissionFeasibilityAssessor",
    "FamilyEligibilityAnalyzer",
    "RecommendationScore",
    "RecommendationReason",
    "VehicleRecommendation",
    "RecommendationReport",
    "RecommendationStrategy",
    "MultirotorFamilyStrategy",
    "FixedWingFamilyStrategy",
    "VTOLFamilyStrategy",
    "QuadcopterRecommendationStrategy",
    "HexacopterRecommendationStrategy",
    "OctocopterRecommendationStrategy",
    "FixedWingRecommendationStrategy",
    "VTOLRecommendationStrategy",
    "RecommendationRanker",
    "RecommendationExplanationService",
    "RecommendationPipeline",
    "RecommendationEngine",
    "RecommendationEngineError",
    "MissingMissionProfileError",
]
