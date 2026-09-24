"""
VTOL Forward Propulsion Strategy Subsystem

Purpose:
    Defines the `ForwardPropulsionStrategy` abstract base and concrete implementations
    specifying target flight layouts and climb safety factors.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class ForwardPropulsionStrategy(ABC):
    """
    Interface for VTOL forward propulsion sizing strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def default_propulsion_architecture(self) -> str:
        """Sized layout format."""
        pass

    @property
    @abstractmethod
    def default_climb_power_factor(self) -> float:
        """Reserve sizing multiplier for climbs."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Sizing recommendations."""
        pass


class BaseCruiseStrategy(ForwardPropulsionStrategy):
    """
    Generic cruise strategies.
    """

    @property
    def default_propulsion_architecture(self) -> str:
        return "Single Pusher"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.30

    def get_recommendations(self) -> List[str]:
        return [
            "Use folder folding props on the forward motor to reduce drag when vertical rotors take over.",
            "Verify ESC is mounted directly in the NACA cooling duct flow to prevent thermal throttle.",
        ]


class SurveyCruiseStrategy(BaseCruiseStrategy):
    """Camera scans require stable pusher paths to avoid prop interference."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def default_propulsion_architecture(self) -> str:
        return "Single Pusher"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.25

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Verify rear pusher hub clearance prevents tailboom elastic vibration strike.",
        ])
        return recs


class CargoCruiseStrategy(BaseCruiseStrategy):
    """Heavy cargo requires twin tractor pullers."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def default_propulsion_architecture(self) -> str:
        return "Twin Tractor"

    @property
    def default_climb_power_factor(self) -> float:
        # Cargo requires higher climb reserves
        return 1.45

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use twin tractor layouts to blow clean air over wing sections, reducing stall speeds.",
            "Implement differential cruise throttle controls to provide secondary yaw trim checks.",
        ])
        return recs


class MappingCruiseStrategy(BaseCruiseStrategy):
    """Steady scan tracking."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def default_propulsion_architecture(self) -> str:
        return "Single Pusher"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.30

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class LongEnduranceCruiseStrategy(BaseCruiseStrategy):
    """Endurance optimized with high efficiency props."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_propulsion_architecture(self) -> str:
        return "Single Tractor"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.20

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Select high pitch-to-diameter propellers to maximize propulsive efficiency at target cruise speed.",
        ])
        return recs


class MilitaryCruiseStrategy(BaseCruiseStrategy):
    """High speeds focus."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def default_propulsion_architecture(self) -> str:
        return "Twin Tractor"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.50

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class ResearchCruiseStrategy(BaseCruiseStrategy):
    """Highly customizable layouts."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def default_propulsion_architecture(self) -> str:
        return "Single Pusher"

    @property
    def default_climb_power_factor(self) -> float:
        return 1.30

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class BalancedCruiseStrategy(BaseCruiseStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()
