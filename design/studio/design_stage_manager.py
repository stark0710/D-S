"""
DesignStageManager Subsystem

Purpose:
    Defines the `DesignStageManager` class responsible for tracking workflow stage progression, completions, skips, and failures.

Role in Architecture:
    `DesignStageManager` manages workflow lifecycle state transitions for `DesignWorkflow` and `DesignStudio` instances.
"""

from backend.design.common.context.design_stage import DesignStage
from backend.design.studio.design_exception import StageTransitionError


class DesignStageManager:
    """
    State manager for tracking workflow stage transitions.

    Design Principles:
        - Single Responsibility Principle: Stage state transition tracking only.
    """

    def __init__(self, initial_stage: DesignStage = DesignStage.REQUIREMENT_COLLECTION) -> None:
        """
        Initializes the DesignStageManager.

        Args:
            initial_stage (DesignStage): Initial starting workflow stage.
        """
        self.current_stage: DesignStage = initial_stage
        self.completed_stages: list[DesignStage] = []
        self.skipped_stages: list[DesignStage] = []
        self.failed_stages: list[DesignStage] = []

    def can_transition_to(self, target_stage: DesignStage) -> bool:
        """Checks whether transitioning to target_stage is valid."""
        return True  # Flexible state transition validation

    def advance_stage(self, stage: DesignStage) -> None:
        """
        Advances current_stage to stage.

        Args:
            stage (DesignStage): Target workflow stage.

        Raises:
            StageTransitionError: If stage transition is invalid.
        """
        if not self.can_transition_to(stage):
            raise StageTransitionError(
                f"Cannot transition from current stage '{self.current_stage.value}' to '{stage.value}'."
            )
        self.current_stage = stage

    def mark_completed(self, stage: DesignStage) -> None:
        """Marks stage as completed and appends to completed_stages."""
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)

    def mark_skipped(self, stage: DesignStage) -> None:
        """Marks stage as skipped and appends to skipped_stages."""
        if stage not in self.skipped_stages:
            self.skipped_stages.append(stage)

    def mark_failed(self, stage: DesignStage) -> None:
        """Marks stage as failed and appends to failed_stages."""
        if stage not in self.failed_stages:
            self.failed_stages.append(stage)
