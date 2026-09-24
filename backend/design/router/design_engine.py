"""
DesignEngine Interface Subsystem

Purpose:
    Defines the abstract `DesignEngine` interface that every category-specific Design Studio must implement.

Role in Architecture:
    `DesignEngine` provides the contract for studio workflow execution.
    It receives a `DesignContext`, executes category-specific sizing and component selection, and returns an updated `DesignContext`.
"""

from abc import ABC, abstractmethod
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.context.design_context import DesignContext


class DesignEngine(ABC):
    """
    Abstract interface for category-specific design studio engines.
    """

    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier string of the design engine implementation."""
        pass

    @property
    @abstractmethod
    def supported_aircraft_types(self) -> list[AircraftType]:
        """List of aircraft categories supported by this design engine."""
        pass

    @abstractmethod
    def execute_design(self, context: DesignContext) -> DesignContext:
        """
        Executes the category-specific aircraft design workflow.

        Args:
            context (DesignContext): Input design context.

        Returns:
            DesignContext: Updated design context containing sized aircraft design.
        """
        pass
