"""
RecommendationRanker Subsystem

Purpose:
    Defines the `RecommendationRanker` class responsible for sorting and ranking candidate vehicle recommendations.

Role in Architecture:
    `RecommendationRanker` orders `VehicleRecommendation` objects by overall suitability score and confidence,
    producing a deterministic recommendation order.
"""

from backend.design.advisor.recommendation.vehicle_recommendation import VehicleRecommendation


class RecommendationRanker:
    """
    Ranker for sorting candidate vehicle recommendations.

    Design Principles:
        - Single Responsibility Principle: Ranking and tie-breaking only.
        - Deterministic Order: Sorts primarily by overall_score descending, secondarily by confidence.
    """

    def rank(self, recommendations: list[VehicleRecommendation]) -> list[VehicleRecommendation]:
        """
        Sorts candidate vehicle recommendations in descending suitability order.

        Args:
            recommendations (list[VehicleRecommendation]): Unsorted list of vehicle recommendations.

        Returns:
            list[VehicleRecommendation]: Ranked list of vehicle recommendations (highest score first).
        """
        return sorted(
            recommendations,
            key=lambda rec: (rec.overall_score, rec.confidence),
            reverse=True
        )
