"""
WorkflowRegistry Subsystem

Purpose:
    Defines the `WorkflowRegistry` class responsible for registering and managing workflow stage steps.

Role in Architecture:
    `WorkflowRegistry` provides the plugin registry for design workflow stage steps.
    It enables dynamic registration and lookup of custom aircraft design stage implementations.
"""

from backend.design.studio.workflow.workflow_stage import WorkflowStage
from backend.design.studio.workflow.workflow_exception import StageNotFoundError


class WorkflowRegistry:
    """
    Registry for managing workflow stage steps.

    Design Principles:
        - Registry Pattern: Centralized stage registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom workflow stages.
    """

    def __init__(self) -> None:
        """Initializes the WorkflowRegistry."""
        self._stages: dict[str, WorkflowStage] = {}

    def register_stage(self, stage: WorkflowStage) -> None:
        """
        Registers a new workflow stage step.

        Args:
            stage (WorkflowStage): WorkflowStage instance to register.
        """
        self._stages[stage.stage_name] = stage

    def get_stage(self, stage_name: str) -> WorkflowStage:
        """
        Retrieves a registered stage by name.

        Args:
            stage_name (str): Stage identifier name.

        Returns:
            WorkflowStage: Registered stage instance.

        Raises:
            StageNotFoundError: If stage_name is not registered.
        """
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Workflow stage '{stage_name}' not found in registry.")
        return self._stages[stage_name]

    def registered_stages(self) -> list[WorkflowStage]:
        """Returns a list of all registered WorkflowStage instances."""
        return list(self._stages.values())
