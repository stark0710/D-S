"""
DesignStudio Subsystem

Purpose:
    Defines the abstract `DesignStudio` interface that all category-specific Design Studios inherit from.

Role in Architecture:
    `DesignStudio` provides the common base class contract for DroneDesignStudio, FixedWingDesignStudio,
    and VTOLDesignStudio. It defines the entry-point method signature `execute_design(context)` returning a `DesignResult`.
"""

from abc import ABC, abstractmethod
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.design_result import DesignResult


class DesignStudio(ABC):
    """
    Abstract base class for all Torq Wings Aircraft Design Studios.
    """

    @property
    @abstractmethod
    def studio_name(self) -> str:
        """Unique identifier name of the Design Studio implementation."""
        pass

    @abstractmethod
    def execute_design(self, context: DesignContext) -> DesignResult:
        """
        Executes the category-specific engineering design workflow.

        Args:
            context (DesignContext): Input design context.

        Returns:
            DesignResult: Final design execution result containing updated context and generated artifacts.
        """
        pass
