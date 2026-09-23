"""
VTOL Airfoil Sizing Strategy Subsystem

Purpose:
    Defines the `AirfoilStrategy` abstract base and concrete implementations
    directing database candidate matching.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AirfoilStrategy(ABC):
    """
    Interface for VTOL airfoil selection strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def preferred_candidates(self) -> List[str]:
        """Ranked list of preferred airfoil names in database."""
        pass

    @property
    @abstractmethod
    def target_cl(self) -> float:
        """Target sectional lift coefficient during cruise."""
        pass

    @abstractmethod
    def get_recommendations(self, airfoil_name: str) -> List[str]:
        """Engineering tips for motor mounts and flow interactions."""
        pass


class BaseAirfoilStrategy(AirfoilStrategy):
    """
    Generic airfoil parameters.
    """

    @property
    def preferred_candidates(self) -> List[str]:
        return ["NACA 4412", "Clark Y"]

    @property
    def target_cl(self) -> float:
        return 0.50

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        return [
            f"Utilize boundary layer fences on wing sections directly behind hover rotor downwash lines.",
            f"Verify trailing edge reinforcement on '{airfoil_name}' to support control surface hinges.",
        ]


class SurveyAirfoilStrategy(BaseAirfoilStrategy):
    """Optimized for steady flight and stable pitching moments."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def preferred_candidates(self) -> List[str]:
        return ["Clark Y", "NACA 4412"]

    @property
    def target_cl(self) -> float:
        return 0.45

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        recs = super().get_recommendations(airfoil_name)
        recs.extend([
            "Select Clark Y for flat-bottomed ease of camera payload hatch cutout alignment.",
            "Verify low pitching moments under cruise gust speeds.",
        ])
        return recs


class CargoAirfoilStrategy(BaseAirfoilStrategy):
    """Optimized for high Cl_max at low speeds."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def preferred_candidates(self) -> List[str]:
        return ["Selig S1223", "NACA 4412"]

    @property
    def target_cl(self) -> float:
        return 0.85

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        recs = super().get_recommendations(airfoil_name)
        recs.extend([
            "Ensure the carbon tube spar is positioned exactly at maximum thickness point (20% chord for Selig).",
            "Prepare for strong pitching moment correction forces via horizontal stabilizers.",
        ])
        return recs


class MappingAirfoilStrategy(BaseAirfoilStrategy):
    """Optimized for steady state nadir scans."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def preferred_candidates(self) -> List[str]:
        return ["NACA 4412", "Clark Y"]

    @property
    def target_cl(self) -> float:
        return 0.50

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        recs = super().get_recommendations(airfoil_name)
        recs.extend([
            "Utilize standard NACA 4-digit profiles to assure predictable stall characteristics in transition.",
        ])
        return recs


class LongEnduranceAirfoilStrategy(BaseAirfoilStrategy):
    """Optimized for maximum L/D glider efficiency."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def preferred_candidates(self) -> List[str]:
        return ["MH 32", "RG 15", "Eppler 387"]

    @property
    def target_cl(self) -> float:
        return 0.55

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        recs = super().get_recommendations(airfoil_name)
        recs.extend([
            "Select thin airfoil profiles (MH 32) to minimize parasitic profile drag in cruise.",
            "Verify low Reynolds laminar flow separation bubbles at cruise speeds.",
        ])
        return recs


class MilitaryAirfoilStrategy(BaseAirfoilStrategy):
    """Optimized for speed and stealthy low drag profile."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def preferred_candidates(self) -> List[str]:
        return ["NACA 0012", "RG 15"]

    @property
    def target_cl(self) -> float:
        return 0.35

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        recs = super().get_recommendations(airfoil_name)
        recs.extend([
            "Utilize symmetrical NACA 0012 or reflexed profiles for tailless configurations.",
        ])
        return recs


class ResearchAirfoilStrategy(BaseAirfoilStrategy):
    """Modular wing templates with good structural clearance."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def preferred_candidates(self) -> List[str]:
        return ["NACA 4412", "Clark Y"]

    @property
    def target_cl(self) -> float:
        return 0.50

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        return super().get_recommendations(airfoil_name)


class BalancedAirfoilStrategy(BaseAirfoilStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self, airfoil_name: str) -> List[str]:
        return super().get_recommendations(airfoil_name)
