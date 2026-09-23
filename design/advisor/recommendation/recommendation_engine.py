"""
RecommendationEngine Subsystem

Purpose:
    Defines the `RecommendationEngine` class orchestrating vehicle category selection over a `DesignContext`.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.advisor.recommendation.selection_status import SelectionStatus
from backend.design.advisor.recommendation.recommendation_pipeline import RecommendationPipeline


class RecommendationEngineError(ValueError):
    """Base exception class for RecommendationEngine errors."""
    pass


class MissingMissionProfileError(RecommendationEngineError):
    """Raised when attempting vehicle recommendation on a DesignContext lacking a MissionProfile."""
    pass


class RecommendationEngine:
    """
    Engine orchestrating 3-family vehicle selection for DesignContext instances.
    """

    def __init__(self, pipeline: RecommendationPipeline | None = None) -> None:
        self._pipeline: RecommendationPipeline = pipeline if pipeline else RecommendationPipeline()

    def recommend(self, context: DesignContext) -> DesignContext:
        """
        Executes 3-family vehicle selection on the provided DesignContext.

        Args:
            context (DesignContext): Target design context.

        Returns:
            DesignContext: Updated design context containing generated RecommendationReport.
        """
        if context.mission_profile is None:
            raise MissingMissionProfileError(
                "Cannot perform vehicle recommendation: DesignContext is missing a MissionProfile."
            )

        report = self._pipeline.execute(context.mission_profile)
        context.vehicle_recommendations = report

        if report.status == SelectionStatus.SELECTED and report.selected_family:
            top_rec = report.recommendations[0]
            context.update_stage(
                stage=DesignStage.VEHICLE_RECOMMENDATION,
                status=DesignStatus.WAITING_FOR_USER,
                snapshot_summary=(
                    f"Vehicle family selected. Top recommended family: {report.selected_family.value} "
                    f"(Score: {top_rec.overall_score}, Confidence: {top_rec.confidence})."
                )
            )
        else:
            context.update_stage(
                stage=DesignStage.VEHICLE_RECOMMENDATION,
                status=DesignStatus.FAILED,
                snapshot_summary=f"Vehicle family selection failed: {report.summary}"
            )

        return context
