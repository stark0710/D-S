"""
RecommendationStrategy Subsystem

Purpose:
    Defines the `RecommendationStrategy` base class and concrete family evaluation strategies
    for MULTIROTOR, FIXED_WING, and VTOL aircraft families.
"""

from abc import ABC, abstractmethod
from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.advisor.recommendation.vehicle_type import VehicleType
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily
from backend.design.advisor.recommendation.recommendation_score import RecommendationScore
from backend.design.advisor.recommendation.recommendation_reason import RecommendationReason
from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation


def _to_engineering_score(score: float) -> RecommendationScore:
    """Helper mapping numeric score (0.0 to 1.0) into qualitative RecommendationScore."""
    if score >= 0.85:
        return RecommendationScore.EXCELLENT
    elif score >= 0.70:
        return RecommendationScore.GOOD
    elif score >= 0.50:
        return RecommendationScore.ACCEPTABLE
    elif score >= 0.30:
        return RecommendationScore.POOR
    else:
        return RecommendationScore.UNSUITABLE


class RecommendationStrategy(ABC):
    """
    Abstract strategy for evaluating a single candidate vehicle family.
    """

    @abstractmethod
    def evaluate(self, mission_profile: MissionProfile) -> VehicleRecommendation:
        """
        Evaluates family suitability for the given MissionProfile.

        Args:
            mission_profile (MissionProfile): Engineering mission profile input.

        Returns:
            VehicleRecommendation: Evaluation recommendation for this family.
        """
        pass


class MultirotorFamilyStrategy(RecommendationStrategy):
    """Evaluation strategy for MULTIROTOR family."""

    def evaluate(self, mission_profile: MissionProfile) -> VehicleRecommendation:
        score = 0.80
        pros: list[str] = [
            "Vertical takeoff and precision hover capability",
            "High station-keeping flight control precision",
            "No runway required",
        ]
        cons: list[str] = []
        reasons: list[RecommendationReason] = [
            RecommendationReason.HOVER_CAPABILITY,
            RecommendationReason.VERTICAL_TAKEOFF,
        ]

        # Range penalties
        if mission_profile.range_requirement > 30.0:
            score -= 0.40
            cons.append("High aerodynamic drag limits long-range performance (> 30 km).")
            reasons.append(RecommendationReason.RANGE)
        elif mission_profile.range_requirement > 15.0:
            score -= 0.20
            cons.append("Moderate energy consumption for mid-range flights.")
            reasons.append(RecommendationReason.RANGE)

        # Endurance penalties
        if mission_profile.flight_time_requirement > 45.0:
            score -= 0.30
            cons.append("LiPo battery energy density limits hover endurance beyond 45 minutes.")
            reasons.append(RecommendationReason.FLIGHT_TIME)

        # Payload penalties
        if mission_profile.payload_requirement > 10.0:
            if mission_profile.range_requirement < 15.0:
                score -= 0.10
                cons.append("Heavy payload mass requires high multi-rotor motor power draw.")
            else:
                score -= 0.25
                cons.append("Heavy payload mass requires high multi-rotor power draw (> 10 kg).")
            reasons.append(RecommendationReason.PAYLOAD_CAPABILITY)

        score = max(0.0, min(1.0, score))
        eng_score = _to_engineering_score(score)

        return VehicleRecommendation(
            vehicle_family=VehicleFamily.MULTIROTOR,
            overall_score=round(score, 2),
            confidence=0.90,
            engineering_score=eng_score,
            estimated_cost=2500.0,
            estimated_complexity="Low-Medium",
            pros=pros,
            cons=cons,
            reasons=reasons,
            vehicle_type=VehicleType.QUADCOPTER,
        )


class FixedWingFamilyStrategy(RecommendationStrategy):
    """Evaluation strategy for FIXED_WING family."""

    def evaluate(self, mission_profile: MissionProfile) -> VehicleRecommendation:
        score = 0.70
        pros: list[str] = [
            "High aerodynamic lift-to-drag efficiency",
            "Exceptional range capability",
            "High cruise endurance",
        ]
        cons: list[str] = []
        reasons: list[RecommendationReason] = [
            RecommendationReason.RANGE,
            RecommendationReason.CRUISE_EFFICIENCY,
            RecommendationReason.FLIGHT_TIME,
        ]

        if mission_profile.takeoff_requirement in (TakeoffType.RUNWAY, TakeoffType.CATAPULT, TakeoffType.HAND_LAUNCH):
            score += 0.15
            pros.append("Wing-borne aerodynamic flight highly efficient for non-vertical launch.")

        if mission_profile.range_requirement >= 30.0:
            score += 0.20
            pros.append("Ideal candidate for long-range mapping and survey (> 30 km).")

        if mission_profile.flight_time_requirement >= 60.0:
            score += 0.15
            pros.append("Excellent wing-borne flight endurance.")

        if mission_profile.takeoff_requirement == TakeoffType.VERTICAL:
            score -= 0.75
            cons.append("Fixed-wing cannot perform vertical takeoff without specialized VTOL hardware.")
            reasons.append(RecommendationReason.VERTICAL_TAKEOFF)

        score = max(0.0, min(1.0, score))
        eng_score = _to_engineering_score(score)

        return VehicleRecommendation(
            vehicle_family=VehicleFamily.FIXED_WING,
            overall_score=round(score, 2),
            confidence=0.92,
            engineering_score=eng_score,
            estimated_cost=4500.0,
            estimated_complexity="Medium",
            pros=pros,
            cons=cons,
            reasons=reasons,
            vehicle_type=VehicleType.FIXED_WING,
        )


class VTOLFamilyStrategy(RecommendationStrategy):
    """Evaluation strategy for VTOL family."""

    def evaluate(self, mission_profile: MissionProfile) -> VehicleRecommendation:
        score = 0.80
        pros: list[str] = [
            "Combines vertical takeoff with long-range fixed-wing cruise",
            "No runway required",
            "High range and endurance",
        ]
        cons: list[str] = []
        reasons: list[RecommendationReason] = [
            RecommendationReason.VERTICAL_TAKEOFF,
            RecommendationReason.RANGE,
            RecommendationReason.FLIGHT_TIME,
        ]

        if mission_profile.takeoff_requirement == TakeoffType.VERTICAL and mission_profile.range_requirement >= 30.0:
            score += 0.15
            pros.append("Optimal choice for vertical takeoff combined with long range (> 30 km).")

        if mission_profile.range_requirement < 15.0:
            score -= 0.30
            cons.append("Unnecessary structural weight and tilt-rotor complexity for short-range missions (< 15 km).")
        elif mission_profile.range_requirement < 25.0:
            score -= 0.10

        score = max(0.0, min(1.0, score))
        eng_score = _to_engineering_score(score)

        return VehicleRecommendation(
            vehicle_family=VehicleFamily.VTOL,
            overall_score=round(score, 2),
            confidence=0.90,
            engineering_score=eng_score,
            estimated_cost=8500.0,
            estimated_complexity="High",
            pros=pros,
            cons=cons,
            reasons=reasons,
            vehicle_type=VehicleType.VTOL,
        )


# Backward compatibility aliases
class QuadcopterRecommendationStrategy(MultirotorFamilyStrategy):
    """Legacy alias for MultirotorFamilyStrategy."""
    pass


class HexacopterRecommendationStrategy(MultirotorFamilyStrategy):
    """Legacy alias for MultirotorFamilyStrategy."""
    pass


class OctocopterRecommendationStrategy(MultirotorFamilyStrategy):
    """Legacy alias for MultirotorFamilyStrategy."""
    pass


class FixedWingRecommendationStrategy(FixedWingFamilyStrategy):
    """Legacy alias for FixedWingFamilyStrategy."""
    pass


class VTOLRecommendationStrategy(VTOLFamilyStrategy):
    """Legacy alias for VTOLFamilyStrategy."""
    pass
