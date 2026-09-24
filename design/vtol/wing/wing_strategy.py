"""
VTOL Wing Sizing Strategy Subsystem

Purpose:
    Defines the `WingStrategy` abstract base and concrete implementations
    specifying target aspect ratios, wing loadings, and structural concepts.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from backend.design.vtol.wing.wing_geometry import WingGeometry


class WingStrategy(ABC):
    """
    Interface for VTOL wing layout strategies.
    """

    @property
    @abstractmethod
    def category(self) -> VTOLMissionCategory:
        """The mission category this strategy maps to."""
        pass

    @property
    @abstractmethod
    def default_aspect_ratio(self) -> float:
        """Target wing aspect ratio."""
        pass

    @property
    @abstractmethod
    def default_wing_loading_kg_m2(self) -> float:
        """Target wing loading in kg/m²."""
        pass

    @property
    @abstractmethod
    def default_sweep_deg(self) -> float:
        """Target wing sweep angle in degrees."""
        pass

    @property
    @abstractmethod
    def default_dihedral_deg(self) -> float:
        """Target dihedral angle in degrees."""
        pass

    @property
    @abstractmethod
    def structural_concept(self) -> str:
        """Material construction layout description."""
        pass

    @property
    @abstractmethod
    def default_wing_position(self) -> str:
        """Height of wing on fuselage (e.g. High Wing, Low Wing)."""
        pass

    @abstractmethod
    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        """Strategic wing design guidelines."""
        pass


class BaseWingStrategy(WingStrategy):
    """
    Generic wing sizing guidelines.
    """

    @property
    def default_aspect_ratio(self) -> float:
        return 10.0

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 35.0

    @property
    def default_sweep_deg(self) -> float:
        return 0.0

    @property
    def default_dihedral_deg(self) -> float:
        return 1.5

    @property
    def structural_concept(self) -> str:
        return "Composite spar with ribbed skin"

    @property
    def default_wing_position(self) -> str:
        return "High Wing"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            f"Specify a {self.structural_concept} concept to absorb vertical boom twist loads during transition.",
            "Verify aileron surfaces extend at least 25% of the semi-span for roll authority in hover transition.",
        ]


class SurveyWingStrategy(BaseWingStrategy):
    """Optimized for steady flight and stable camera paths."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.SURVEY

    @property
    def default_aspect_ratio(self) -> float:
        return 13.0

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 30.0

    @property
    def structural_concept(self) -> str:
        return "Carbon sandwich skin with hollow spar cavities"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Use high aspect ratio panels to reduce induced drag in cruise grids.",
            "Incorporate small winglet tips to minimize vortex shedding and roll disturbances.",
        ])
        return recs


class CargoWingStrategy(BaseWingStrategy):
    """Optimized for heavy lift loads and thick structural root joints."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CARGO

    @property
    def default_aspect_ratio(self) -> float:
        return 8.5  # Stiffer, thicker chord wings to support load

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 48.0  # High wing loading for structural compactness

    @property
    def structural_concept(self) -> str:
        return "Reinforced double carbon spar with shear webs"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Design thick airfoil roots (e.g. Selig S1223) to maximize internal spar depth.",
            "Utilize high wing mounts to elevate motors far above landing gear clearance arcs.",
        ])
        return recs


class MappingWingStrategy(BaseWingStrategy):
    """Optimized for stable roll response and nadir photo grids."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MAPPING

    @property
    def default_aspect_ratio(self) -> float:
        return 12.5

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 32.0

    @property
    def structural_concept(self) -> str:
        return "Composite skin with internal CNC cut balsa ribs"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Provide internal spar routing tubes for ESC signal wiring shielding.",
            "Implement negative twist (washout) at tips to stabilize roll holding.",
        ])
        return recs


class LongEnduranceWingStrategy(BaseWingStrategy):
    """Glider-like high efficiency wings."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_aspect_ratio(self) -> float:
        return 16.5  # High aerodynamic glide efficiency

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 22.0  # Low loading for slower, efficient speeds

    @property
    def structural_concept(self) -> str:
        return "Carbon-fiber prepreg monocoque shell"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Specify high-aspect-ratio panels to minimize induced cruise power.",
            "Verify aileron hinge lines are sealed to avoid low Reynolds boundary layer drag.",
        ])
        return recs


class MilitaryWingStrategy(BaseWingStrategy):
    """Optimized for high speeds and structural G load reserves."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MILITARY

    @property
    def default_aspect_ratio(self) -> float:
        return 9.0

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 42.0

    @property
    def default_sweep_deg(self) -> float:
        return 8.0  # swept wing for higher speed transition stability

    @property
    def structural_concept(self) -> str:
        return "Solid machined core with composite skin overlay"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Design sweep lines to shift aerodynamic center aft, improving high-speed transition damping.",
            "Structure panels with mechanical quick-release hinge pins for rapid field breakdown.",
        ])
        return recs


class ResearchWingStrategy(BaseWingStrategy):
    """Modular wing profiles for varying atmospheric loads."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.RESEARCH

    @property
    def default_aspect_ratio(self) -> float:
        return 11.5

    @property
    def default_wing_loading_kg_m2(self) -> float:
        return 34.0

    @property
    def structural_concept(self) -> str:
        return "Removable wing segments with carbon joiner tubes"

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        recs = super().get_recommendations(geometry)
        recs.extend([
            "Implement standardized carbon fiber spar joiner sleeves for simple panel replacements.",
            "Provide modular external pylons for scientific sensor pod attachments.",
        ])
        return recs


class BalancedWingStrategy(BaseWingStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return super().get_recommendations(geometry)
