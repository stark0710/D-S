"""
DesignStage Interface Subsystem

Purpose:
    Defines the abstract `DesignStage` interface that every reusable workflow stage step must implement.

Role in Architecture:
    `DesignStage` defines the contract for reusable workflow stage steps.
    It declares required inputs, required dependencies, category classification, and execution handler `execute(stage_context)`.
"""

from abc import ABC, abstractmethod
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.stages.stage_category import StageCategory
from backend.design.studio.stages.stage_context import StageContext
from backend.design.studio.stages.stage_result import StageResult


class DesignStage(ABC):
    """
    Abstract interface for reusable aircraft design workflow stages.
    """

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Unique identifier name of the stage step."""
        pass

    @property
    @abstractmethod
    def category(self) -> StageCategory:
        """StageCategory classification."""
        pass

    @property
    @abstractmethod
    def required_inputs(self) -> list[str]:
        """List of required data keys expected in design_data or context."""
        pass

    @property
    @abstractmethod
    def required_dependencies(self) -> list[str]:
        """List of stage names that MUST be executed prior to this stage."""
        pass

    @abstractmethod
    def execute(self, stage_context: StageContext) -> tuple[DesignContext, StageResult]:
        """
        Executes the design stage step.

        Args:
            stage_context (StageContext): Input stage context.

        Returns:
            tuple[DesignContext, StageResult]: Tuple of (updated DesignContext, StageResult summary).
        """
        pass
