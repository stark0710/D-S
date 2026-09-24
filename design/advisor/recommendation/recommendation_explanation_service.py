"""
RecommendationExplanationService Subsystem

Purpose:
    Defines the `RecommendationExplanationService` class responsible for generating transparent, human-readable explanations.

Role in Architecture:
    `RecommendationExplanationService` generates physics-based engineering rationale, trade-off notes, and summary text
    explaining why specific aircraft categories received their respective suitability scores.
"""

from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation
from backend.design.advisor.recommendation.recommendation_report import RecommendationReport


class RecommendationExplanationService:
    """
    Explanation generator for vehicle category recommendations.

    Design Principles:
        - Single Responsibility Principle: Physics-based explanation generation only.
        - Explainable AI: Produces human-interpretable rationale for every recommendation score.
    """

    def generate_report(
        self,
        ranked_recommendations: list[VehicleRecommendation],
        mission_profile: MissionProfile
    ) -> RecommendationReport:
        """
        Constructs a RecommendationReport containing transparent engineering explanations.

        Args:
            ranked_recommendations (list[VehicleRecommendation]): Ranked candidate evaluations.
            mission_profile (MissionProfile): Engineering mission profile.

        Returns:
            RecommendationReport: Final recommendation report carrying structured explanations.
        """
        top_rec = ranked_recommendations[0]
        recommended_type = top_rec.vehicle_type

        summary = (
            f"Recommended Aircraft Category: {recommended_type.value} (Score: {top_rec.overall_score}, Rating: {top_rec.engineering_score.value}). "
            f"This category is recommended for the {mission_profile.mission_type.value} mission because it optimally satisfies "
            f"the {mission_profile.payload_requirement} kg payload, {mission_profile.range_requirement} km range, and "
            f"{mission_profile.takeoff_requirement.value} takeoff requirements with minimal complexity trade-offs."
        )

        notes: list[str] = [
            f"Top Recommendation ({recommended_type.value}): Score {top_rec.overall_score}. Key Pros: {', '.join(top_rec.pros)}.",
        ]

        if len(ranked_recommendations) > 1:
            runner_up = ranked_recommendations[1]
            notes.append(
                f"Alternative Category ({runner_up.vehicle_type.value}): Score {runner_up.overall_score}. Trade-offs: {', '.join(runner_up.cons)}."
            )

        return RecommendationReport(
            recommendations=ranked_recommendations,
            recommended_vehicle=recommended_type,
            summary=summary,
            engineering_notes=notes,
            metadata={"candidate_count": len(ranked_recommendations)}
        )
