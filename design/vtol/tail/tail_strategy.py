"""
VTOL Tail Sizing Strategy Subsystem

Purpose:
    Defines the `TailStrategy` abstract base and concrete implementations
    specifying target volume coefficients and control mixers.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class TailStrategy(ABC):
    """
    Interface for VTOL tail configuration strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def default_tail_configuration(self) -> str:
        """Sized layout format."""
        pass

    @property
    @abstractmethod
    def default_vh(self) -> float:
        """Target horizontal tail volume coefficient."""
        pass

    @property
    @abstractmethod
    def default_vv(self) -> float:
        """Target vertical tail volume coefficient."""
        pass

    @property
    @abstractmethod
    def control_mixing_type(self) -> str:
        """Standard flap mixing output configuration."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Empennage design best practices."""
        pass


class BaseTailStrategy(TailStrategy):
    """
    Generic tail strategy defaults.
    """

    @property
    def default_tail_configuration(self) -> str:
        return "Conventional Tail"

    @property
    def default_vh(self) -> float:
        return 0.50

    @property
    def default_vv(self) -> float:
        return 0.04

    @property
    def control_mixing_type(self) -> str:
        return "Conventional Elevator/Rudder"

    def get_recommendations(self) -> List[str]:
        return [
            "Incorporate aerodynamic balanced tabs on elevators to reduce servo load.",
            "Route rudder control horn horns internally to prevent snagging during field handling.",
        ]


class SurveyTailStrategy(BaseTailStrategy):
    """Optimized for steady photo paths and low wake vibrations."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def default_tail_configuration(self) -> str:
        return "T-Tail"  # T-tails place stabilizers above wing downwash/prop wake

    @property
    def default_vh(self) -> float:
        return 0.60

    @property
    def default_vv(self) -> float:
        return 0.045

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Design T-tail root structure with a carbon sleeve to handle extra vertical fin torsion loads.",
            "Verify clear elevator linkages routing up inside the vertical fin skin.",
        ])
        return recs


class CargoTailStrategy(BaseTailStrategy):
    """Optimized for high weight loading and pitch trim authorities."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def default_tail_configuration(self) -> str:
        return "Twin Boom Tail"  # Twin boom tail allows cargo door access behind fuselage

    @property
    def default_vh(self) -> float:
        return 0.55

    @property
    def default_vv(self) -> float:
        return 0.05

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use twin carbon tail booms extending from the wing spar for loading hatch path clearance.",
            "Specify dual elevator servos (left/right) for structural control redundancy.",
        ])
        return recs


class MappingTailStrategy(BaseTailStrategy):
    """Optimized for camera pitch damping."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def default_tail_configuration(self) -> str:
        return "Conventional Tail"

    @property
    def default_vh(self) -> float:
        return 0.50

    @property
    def default_vv(self) -> float:
        return 0.04

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class LongEnduranceTailStrategy(BaseTailStrategy):
    """Optimized for lightweight and low drag (e.g. V-tail)."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_tail_configuration(self) -> str:
        return "V-Tail"  # V-tail reduces junction drag and structural weight

    @property
    def default_vh(self) -> float:
        return 0.48

    @property
    def default_vv(self) -> float:
        return 0.038

    @property
    def control_mixing_type(self) -> str:
        return "V-Tail Mixer (Ruddervons)"

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use V-tail configurations to eliminate vertical fin drag intersections.",
            "Verify autopilot supports ruddervon mixing offsets under high wind hover transitions.",
        ])
        return recs


class MilitaryTailStrategy(BaseTailStrategy):
    """Optimized for speed and compact packaging."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def default_tail_configuration(self) -> str:
        return "Inverted V-Tail"  # Sized low profile and high dynamic pressure slipstream path

    @property
    def default_vh(self) -> float:
        return 0.45

    @property
    def default_vv(self) -> float:
        return 0.04

    @property
    def control_mixing_type(self) -> str:
        return "Inverted V-Tail Mixer"

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Select inverted V-tail stabilizer to avoid direct prop slipstream swirl.",
        ])
        return recs


class ResearchTailStrategy(BaseTailStrategy):
    """Modular setups."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def default_tail_configuration(self) -> str:
        return "Conventional Tail"

    @property
    def default_vh(self) -> float:
        return 0.50

    @property
    def default_vv(self) -> float:
        return 0.04

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class BalancedTailStrategy(BaseTailStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()
