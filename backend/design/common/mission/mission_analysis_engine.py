"""
MissionAnalysisEngine Subsystem

Purpose:
    Defines the `MissionAnalysisEngine` class, which orchestrates mission analysis execution over a `DesignContext`.

Role in Architecture:
    `MissionAnalysisEngine` receives a `DesignContext`, verifies requirement validation state, delegates profile construction
    to `MissionAnalysisService`, updates `context.mission_profile`, advances the workflow stage to `DesignStage.MISSION_ANALYSIS`,
    creates a snapshot, and returns the updated `DesignContext`.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.common.mission.mission_analysis_service import MissionAnalysisService


class MissionAnalysisError(ValueError):
    """Base exception class for MissionAnalysisEngine errors."""
    pass


class InvalidRequirementError(MissionAnalysisError):
    """Raised when attempting to analyze a DesignContext with failed requirement validation."""
    pass


class MissionAnalysisEngine:
    """
    Engine orchestrating mission profile analysis for DesignContext instances.

    Design Principles:
        - Single Responsibility Principle: Mission analysis orchestration only.
        - Dependency Injection: Injects `MissionAnalysisService` collaborator.
        - Context Mutation: Stores `MissionProfile` and advances `DesignStage` on injected context.
    """

    def __init__(self, service: MissionAnalysisService | None = None) -> None:
        """
        Initializes the MissionAnalysisEngine.

        Args:
            service (MissionAnalysisService | None): Injected service instance. Defaults to creating new service if None.
        """
        self._service: MissionAnalysisService = service if service else MissionAnalysisService()

    def analyze(self, context: DesignContext) -> DesignContext:
        """
        Executes mission analysis on the provided DesignContext.

        Args:
            context (DesignContext): Target design context.

        Returns:
            DesignContext: Updated design context containing constructed MissionProfile.

        Raises:
            InvalidRequirementError: If context validation_result exists and is_valid is False.
        """
        if context.validation_result and not context.validation_result.is_valid:
            raise InvalidRequirementError(
                "Cannot perform mission analysis: Requirement validation failed with errors."
            )

        # Delegate analysis to MissionAnalysisService
        result = self._service.analyze_requirements(context.requirement_model)

        # Update DesignContext
        context.mission_profile = result.mission_profile
        context.update_stage(
            stage=DesignStage.MISSION_ANALYSIS,
            status=DesignStatus.IN_PROGRESS,
            snapshot_summary=f"Mission analysis complete. Complexity assessed as {result.mission_profile.mission_complexity.value}."
        )

        return context
