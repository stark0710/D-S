"""
RecommendationPipeline Subsystem

Purpose:
    Defines the `RecommendationPipeline` class responsible for orchestrating the 4-stage vehicle family selection workflow:
    1. Input Validation
    2. Mission Feasibility Assessment
    3. Family Eligibility Analysis
    4. Family Scoring & Dynamic Confidence Calculation
"""

from typing import Dict, List
from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily
from backend.design.advisor.recommendation.selection_status import SelectionStatus
from backend.design.advisor.recommendation.mission_feasibility import MissionFeasibilityResult
from backend.design.advisor.recommendation.mission_feasibility_assessor import MissionFeasibilityAssessor
from backend.design.advisor.recommendation.family_eligibility_analyzer import FamilyEligibilityAnalyzer
from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation
from backend.design.advisor.recommendation.recommendation_report import RecommendationReport
from backend.design.advisor.recommendation.recommendation_strategy import (
    RecommendationStrategy,
    MultirotorFamilyStrategy,
    FixedWingFamilyStrategy,
    VTOLFamilyStrategy,
)
from backend.design.advisor.recommendation.recommendation_ranker import RecommendationRanker
from backend.design.advisor.recommendation.recommendation_explanation_service import RecommendationExplanationService


class RecommendationPipeline:
    """
    4-Stage Vehicle Family Selection Pipeline.
    """

    def __init__(
        self,
        strategies: list[RecommendationStrategy] | None = None,
        ranker: RecommendationRanker | None = None,
        explanation_service: RecommendationExplanationService | None = None,
        feasibility_assessor: MissionFeasibilityAssessor | None = None,
        eligibility_analyzer: FamilyEligibilityAnalyzer | None = None,
    ) -> None:
        if strategies is None:
            strategies = [
                MultirotorFamilyStrategy(),
                FixedWingFamilyStrategy(),
                VTOLFamilyStrategy(),
            ]
        self._strategies: list[RecommendationStrategy] = list(strategies)
        self._ranker: RecommendationRanker = ranker if ranker else RecommendationRanker()
        self._explanation_service: RecommendationExplanationService = (
            explanation_service if explanation_service else RecommendationExplanationService()
        )
        self._feasibility_assessor: MissionFeasibilityAssessor = (
            feasibility_assessor if feasibility_assessor else MissionFeasibilityAssessor()
        )
        self._eligibility_analyzer: FamilyEligibilityAnalyzer = (
            eligibility_analyzer if eligibility_analyzer else FamilyEligibilityAnalyzer()
        )

    def execute(self, mission_profile: MissionProfile) -> RecommendationReport:
        """
        Executes the 4-stage vehicle selection workflow.

        Args:
            mission_profile (MissionProfile): Target engineering mission profile.

        Returns:
            RecommendationReport: Structured 3-family recommendation report.
        """
        # Stage 1: Mission Feasibility Assessment
        feasibility = self._feasibility_assessor.assess(mission_profile)
        if not feasibility.is_feasible:
            return RecommendationReport(
                recommendations=[],
                recommended_vehicle="NONE",
                summary=f"No feasible aircraft design solution: {'; '.join(feasibility.reasons)}",
                status=SelectionStatus.NO_FEASIBLE_SOLUTION,
                selected_family=None,
                family_scores={},
                eligible_families=[],
                eliminated_families={
                    VehicleFamily.MULTIROTOR: "Exceeds physical energy limits",
                    VehicleFamily.FIXED_WING: "Exceeds physical energy limits",
                    VehicleFamily.VTOL: "Exceeds physical energy limits",
                },
                feasibility=feasibility,
                engineering_notes=feasibility.reasons,
                metadata={"feasibility_passed": False},
            )

        # Stage 2: Family Eligibility Analysis
        hover_req = ("hover" in mission_profile.mission_summary.lower() or "inspection" in mission_profile.mission_summary.lower())
        eligible_families, eliminated_families = self._eligibility_analyzer.analyze_eligibility(
            mission_profile, hover_required=hover_req
        )

        if not eligible_families:
            return RecommendationReport(
                recommendations=[],
                recommended_vehicle="NONE",
                summary="No candidate aircraft family satisfied mandatory operational constraints.",
                status=SelectionStatus.NO_FEASIBLE_SOLUTION,
                selected_family=None,
                family_scores={},
                eligible_families=[],
                eliminated_families=eliminated_families,
                feasibility=feasibility,
                metadata={"eligibility_passed": False},
            )

        # Stage 3: Score Eligible Families
        unranked: list[VehicleRecommendation] = []
        family_scores: Dict[VehicleFamily, float] = {}

        for strategy in self._strategies:
            rec = strategy.evaluate(mission_profile)
            if rec.vehicle_family in eligible_families:
                unranked.append(rec)
                family_scores[rec.vehicle_family] = rec.overall_score

        # Sort eligible candidates
        ranked = self._ranker.rank(unranked)
        if not ranked:
            return RecommendationReport(
                recommendations=[],
                recommended_vehicle="NONE",
                summary="No eligible aircraft family achieved positive suitability score.",
                status=SelectionStatus.NO_FEASIBLE_SOLUTION,
                selected_family=None,
                family_scores=family_scores,
                eligible_families=eligible_families,
                eliminated_families=eliminated_families,
                feasibility=feasibility,
            )

        # Stage 4: Calculate Dynamic Confidence
        top_rec = ranked[0]
        if len(ranked) == 1:
            dynamic_conf = top_rec.overall_score
        else:
            runner_up_score = ranked[1].overall_score
            delta = top_rec.overall_score - runner_up_score
            if delta >= 0.20:
                dynamic_conf = min(0.95, round(top_rec.overall_score, 2))
            elif delta >= 0.10:
                dynamic_conf = round(0.70 + delta, 2)
            else:
                dynamic_conf = round(0.50 + delta, 2)

        # Assign calculated dynamic confidence to top recommendation
        top_rec.confidence = dynamic_conf

        report = self._explanation_service.generate_report(ranked, mission_profile)
        report.status = SelectionStatus.SELECTED
        report.selected_family = top_rec.vehicle_family
        report.family_scores = family_scores
        report.eligible_families = eligible_families
        report.eliminated_families = eliminated_families
        report.feasibility = feasibility
        report.recommended_vehicle = top_rec.vehicle_family

        return report
