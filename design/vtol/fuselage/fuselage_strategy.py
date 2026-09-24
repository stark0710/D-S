"""
VTOL Fuselage Sizing Strategy Subsystem

Purpose:
    Defines the `FuselageStrategy` abstract base and concrete implementations
    specifying target compartments and structural types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class FuselageStrategy(ABC):
    """
    Interface for VTOL fuselage layout strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def default_fuselage_type(self) -> str:
        """Sized layout format."""
        pass

    @property
    @abstractmethod
    def default_shape(self) -> str:
        """Cross-section profile shape."""
        pass

    @abstractmethod
    def get_compartment_shares(self) -> Dict[str, float]:
        """Volume allocation shares (must sum to <= 1.0)."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Sizing recommendations."""
        pass


class BaseFuselageStrategy(FuselageStrategy):
    """
    Generic fuselage strategies.
    """

    @property
    def default_fuselage_type(self) -> str:
        return "Monocoque"

    @property
    def default_shape(self) -> str:
        return "Oval"

    def get_compartment_shares(self) -> Dict[str, float]:
        return {"battery": 0.40, "payload": 0.30, "avionics": 0.20}

    def get_recommendations(self) -> List[str]:
        return [
            "Use carbon fiber plies at bulkhead joints to secure structural rigidity.",
            "Separate avionics routing wires from high-current ESC wires to mitigate EMF noise.",
        ]


class SurveyFuselageStrategy(BaseFuselageStrategy):
    """Optimized for camera sensor pods."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def default_fuselage_type(self) -> str:
        return "Pod-and-Boom"

    @property
    def default_shape(self) -> str:
        return "Oval"

    def get_compartment_shares(self) -> Dict[str, float]:
        # Survey allocates more volume for payloads (gimbals, cameras)
        return {"battery": 0.35, "payload": 0.45, "avionics": 0.15}

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Specify quick-release latches on the payload compartment hatch.",
            "Install vibration damping gel mounts beneath the IMU/autopilot tray.",
        ])
        return recs


class CargoFuselageStrategy(BaseFuselageStrategy):
    """Optimized for boxy shapes and high payload volume."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def default_fuselage_type(self) -> str:
        return "Box Fuselage"

    @property
    def default_shape(self) -> str:
        return "Rectangular"

    def get_compartment_shares(self) -> Dict[str, float]:
        # Massive payload bay share
        return {"battery": 0.30, "payload": 0.55, "avionics": 0.10}

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use rectangular cross sections to maximize payload box packaging volume utility.",
            "Reinforce the cargo floor with longitudinal carbon composite ribs to support cargo weight loads.",
        ])
        return recs


class MappingFuselageStrategy(BaseFuselageStrategy):
    """Optimized for vertical nadir sensor placement."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def default_fuselage_type(self) -> str:
        return "Pod-and-Boom"

    @property
    def default_shape(self) -> str:
        return "Oval"

    def get_compartment_shares(self) -> Dict[str, float]:
        return {"battery": 0.40, "payload": 0.40, "avionics": 0.15}

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Specify vertical downward camera port opening in the center payload compartment.",
        ])
        return recs


class LongEnduranceFuselageStrategy(BaseFuselageStrategy):
    """Optimized for minimum aerodynamic drag."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_fuselage_type(self) -> str:
        return "Composite Shell"

    @property
    def default_shape(self) -> str:
        return "Circular"

    def get_compartment_shares(self) -> Dict[str, float]:
        # Battery dominates endurance designs
        return {"battery": 0.60, "payload": 0.20, "avionics": 0.15}

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Design highly streamlined circular profiles to minimize bare fuselage wetted drag.",
            "Verify ventilation tunnels feed cooling airflow over battery panels during long cruise flights.",
        ])
        return recs


class MilitaryFuselageStrategy(BaseFuselageStrategy):
    """Streamlined composite shells with low signatures."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def default_fuselage_type(self) -> str:
        return "Composite Shell"

    @property
    def default_shape(self) -> str:
        return "Circular"

    def get_compartment_shares(self) -> Dict[str, float]:
        return {"battery": 0.40, "payload": 0.40, "avionics": 0.15}

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class ResearchFuselageStrategy(BaseFuselageStrategy):
    """Modular bays."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def default_fuselage_type(self) -> str:
        return "Modular"

    @property
    def default_shape(self) -> str:
        return "Rectangular"

    def get_compartment_shares(self) -> Dict[str, float]:
        return {"battery": 0.40, "payload": 0.40, "avionics": 0.15}

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class BalancedFuselageStrategy(BaseFuselageStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()
