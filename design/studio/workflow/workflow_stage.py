"""
WorkflowStage Subsystem

Purpose:
    Defines the abstract `WorkflowStage` interface that every design workflow stage step must implement.

Role in Architecture:
    `WorkflowStage` represents a discrete step in an aircraft design workflow (e.g. Propulsion Sizing, Airframe Sizing, Battery Sizing).
    It receives a `DesignContext`, performs its step, and returns the updated `DesignContext` alongside a `WorkflowStageResult`.
"""

from abc import ABC, abstractmethod
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.workflow.workflow_stage_result import WorkflowStageResult


class WorkflowStage(ABC):
    """
    Abstract interface for aircraft design workflow stages.
    """

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Unique identifier name of the workflow stage."""
        pass

    @abstractmethod
    def execute(self, context: DesignContext) -> tuple[DesignContext, WorkflowStageResult]:
        """
        Executes the workflow stage against the provided DesignContext.

        Args:
            context (DesignContext): Input design context.

        Returns:
            tuple[DesignContext, WorkflowStageResult]: Tuple of (updated DesignContext, stage result summary).
        """
        pass
