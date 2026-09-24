"""
Fixed-Wing Manufacturing Sizing Strategy Subsystem

Purpose:
    Defines the `ManufacturingStrategy` base class and concrete selection strategies.

Role in Architecture:
    The strategy pattern isolates target fabrication styles, cost factors, and warnings.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class ManufacturingStrategy(ABC):
    """
    Abstract base class for all fixed-wing manufacturing strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_overhead_factors(self) -> Tuple[float, float]:
        """
        Returns strategy settings: (labor_rate_multiplier, tooling_overhead_usd).
        """
        pass

    @abstractmethod
    def get_target_methods(self) -> List[str]:
        """Allowed manufacturing methods list."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates process planning advice."""
        pass


class BaseManufacturingStrategy(ManufacturingStrategy):
    """
    Common base implementation of ManufacturingStrategy.
    """

    def get_overhead_factors(self) -> Tuple[float, float]:
        return 1.0, 150.0

    def get_target_methods(self) -> List[str]:
        return ["3D Printing", "CNC Machining", "Laser Cutting", "Manual Fabrication"]

    def get_recommendations(self) -> List[str]:
        return [
            "Use carbon fiber booms for structural spar stiffness.",
            "Verify fastener sizes against the BOM schedules before procurement.",
        ]


class PrototypeManufacturingStrategy(BaseManufacturingStrategy):
    """Strategy optimized for fast mockups using foam boards and 3D printing."""

    @property
    def name(self) -> str:
        return "Prototype"

    def get_overhead_factors(self) -> Tuple[float, float]:
        return 0.8, 50.0  # lower tooling costs, quick manual labor

    def get_target_methods(self) -> List[str]:
        return ["3D Printing", "Foam Cutting", "Manual Fabrication"]

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use PLA or PETG for 3D printed motor mounts. ABS is recommended for heat resistance.",
        ])
        return recs


class ResearchManufacturingStrategy(BaseManufacturingStrategy):
    """Strategy optimized for research prototyping."""

    @property
    def name(self) -> str:
        return "Research"


class EducationalManufacturingStrategy(BaseManufacturingStrategy):
    """Strategy optimized for low complexity student builds."""

    @property
    def name(self) -> str:
        return "Educational"

    def get_overhead_factors(self) -> Tuple[float, float]:
        return 0.5, 20.0

    def get_target_methods(self) -> List[str]:
        return ["Foam Cutting", "Manual Fabrication"]


class LowVolumeProductionStrategy(BaseManufacturingStrategy):
    """Strategy optimized for composite layup and batch CNC runs."""

    @property
    def name(self) -> str:
        return "Low Volume Production"

    def get_overhead_factors(self) -> Tuple[float, float]:
        return 1.2, 500.0  # higher tooling overhead for composite molds

    def get_target_methods(self) -> List[str]:
        return ["CNC Machining", "Composite Layup", "Waterjet Cutting"]

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Post-cure composite wing skins at 60 degrees C to achieve maximum stiffness.",
        ])
        return recs


class CompositeAircraftStrategy(LowVolumeProductionStrategy):
    """Strategy optimized for full composite wing/fuselage designs."""

    @property
    def name(self) -> str:
        return "Composite Aircraft"


class HighPrecisionManufacturingStrategy(BaseManufacturingStrategy):
    """Strategy optimized for tight tolerance aerospace checks."""

    @property
    def name(self) -> str:
        return "High Precision"

    def get_overhead_factors(self) -> Tuple[float, float]:
        return 1.8, 1200.0


class BalancedManufacturingStrategy(BaseManufacturingStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
"""
Fixed-Wing Manufacturing Strategy models.
"""
