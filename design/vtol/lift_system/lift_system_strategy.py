"""
VTOL Lift System Strategy Subsystem

Purpose:
    Defines the `LiftSystemStrategy` abstract base and concrete implementations
    specifying thrust safety factors and loading parameters.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class LiftSystemStrategy(ABC):
    """
    Interface for VTOL vertical lift sizing strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def default_safety_factor(self) -> float:
        """Target thrust safety factor multiplier."""
        pass

    @property
    @abstractmethod
    def target_disk_loading_n_m2(self) -> float:
        """Target disk loading index."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Sizing recommendations."""
        pass


class BaseLiftStrategy(LiftSystemStrategy):
    """
    Generic lift strategies.
    """

    @property
    def default_safety_factor(self) -> float:
        return 1.45

    @property
    def target_disk_loading_n_m2(self) -> float:
        return 65.0

    def get_recommendations(self) -> List[str]:
        return [
            "Use dynamic RPM matching on opposing vertical rotors to minimize gyroscopic moments.",
            "Isolate the autopilot GPS compass from ESC electromagnetic lines to avoid EMI compass heading errors.",
        ]


class SurveyLiftStrategy(BaseLiftStrategy):
    """Optimized for low-vibration and quiet hover."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def default_safety_factor(self) -> float:
        # Low vibration requires larger rotors with lower RPM
        return 1.50

    @property
    def target_disk_loading_n_m2(self) -> float:
        # Lower disk loading for quiet hover efficiency
        return 45.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Specify foam-filled carbon propellers to reduce structural acoustic resonances.",
            "Enable field-oriented control (FOC) on the ESC firmware to reduce audible motor noise.",
        ])
        return recs


class CargoLiftStrategy(BaseLiftStrategy):
    """Heavy lift focus with high thrust reserve margins."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def default_safety_factor(self) -> float:
        # Heavy transport requires higher safety factor
        return 1.65

    @property
    def target_disk_loading_n_m2(self) -> float:
        # High disk loading with high-current motors
        return 110.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Employ active cooling fans on the ESC heat sinks to prevent thermal throttle.",
            "Verify boom wall thickness can handle the torsional torque from rapid throttle changes.",
        ])
        return recs


class MappingLiftStrategy(BaseLiftStrategy):
    """Stable nadir survey tracking."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def default_safety_factor(self) -> float:
        return 1.45

    @property
    def target_disk_loading_n_m2(self) -> float:
        return 50.0

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class LongEnduranceLiftStrategy(BaseLiftStrategy):
    """Endurance optimized with lightweight rotors and lower safety factors."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_safety_factor(self) -> float:
        # Minimize motor empty weight by running lower safety margins
        return 1.35

    @property
    def target_disk_loading_n_m2(self) -> float:
        # Large, thin, highly efficient propellers
        return 35.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Select high-modulus carbon fiber props to maximize lift-to-power efficiency.",
            "Reduce total climb rates during transition to save energy.",
        ])
        return recs


class MilitaryLiftStrategy(BaseLiftStrategy):
    """High agility and speed focus."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def default_safety_factor(self) -> float:
        return 1.60

    @property
    def target_disk_loading_n_m2(self) -> float:
        return 90.0

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class ResearchLiftStrategy(BaseLiftStrategy):
    """Highly flexible setups."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def default_safety_factor(self) -> float:
        return 1.50

    @property
    def target_disk_loading_n_m2(self) -> float:
        return 60.0

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class BalancedLiftStrategy(BaseLiftStrategy):
    """Generic custom strategy."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()
