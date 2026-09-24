"""
Fixed-Wing Wing Strategy Subsystem

Purpose:
    Defines the `WingStrategy` base class and concrete sizing strategies for different wing types.

Role in Architecture:
    Enforces strategy pattern to isolate typical wing load limits, target aspect ratios, sweep/dihedral values,
    and planform preferences for Survey, Endurance, Cargo, Agriculture, and Training configurations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry


class WingStrategy(ABC):
    """
    Abstract base class for fixed-wing wing design strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_target_aspect_ratio(self) -> float:
        """Typical Aspect Ratio for this wing class."""
        pass

    @abstractmethod
    def get_typical_wing_loading_kg_m2(self) -> float:
        """Typical wing loading limit in kg/m2."""
        pass

    @abstractmethod
    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        """Determines planform shape."""
        pass

    @abstractmethod
    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        """
        Determines sweep, dihedral, and incidence angles.
        
        Returns:
            Tuple[float, float, float]: (sweep_deg, dihedral_deg, incidence_deg)
        """
        pass

    @abstractmethod
    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        """Generates recommendations tailored for this strategy."""
        pass


class BaseWingStrategy(WingStrategy):
    """
    Common base implementation of WingStrategy.
    """

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.TAPERED

    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        # Default angles: 0 deg sweep, 3 deg dihedral, 2 deg incidence
        return 0.0, 3.0, 2.0


class LongEnduranceWingStrategy(BaseWingStrategy):
    """Strategy for highly efficient, high-glide long endurance wings."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_target_aspect_ratio(self) -> float:
        return 16.0  # High AR glider wings

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 8.0  # Light wing loading to minimize sink speed

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.ELLIPTICAL  # Minimizes induced drag

    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        # Low sweep for low speed efficiency, minor dihedral
        return 0.0, 2.5, 2.5

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Use high modulus carbon fiber wing spars to prevent excessive tip deflection under load.",
            "Choose a laminar-flow airfoil (e.g. Wortmann FX series or SD7037) for low-drag cruise.",
            "Add minor tip washout (twist) of -1.5 degrees to guarantee gentle stall characteristics.",
        ]


class SurveillanceWingStrategy(BaseWingStrategy):
    """Strategy for tactical surveillance, security, and infrastructure inspection wings."""

    @property
    def name(self) -> str:
        return "Surveillance"

    def get_target_aspect_ratio(self) -> float:
        return 9.0  # Moderate aspect ratio balancing aerodynamic efficiency with practical root chord

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 13.5  # Tactical patrol wing loading for gust tolerance and loiter speed

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.TAPERED

    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        # Low sweep for cruise efficiency, moderate dihedral for spiral stability
        return 0.0, 3.5, 2.0

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Select a gentle-stall airfoil (e.g. NACA 4415 or Clark Y) to ensure stable loiter behavior.",
            "Maintain adequate root chord width to prevent fuselage-wing junction aerodynamic blockage.",
            "Incorporate wingtip fences or modest dihedral to improve spiral stability during surveillance turns.",
        ]


class SurveyWingStrategy(BaseWingStrategy):
    """Strategy for survey and mapping wings requiring stable flight lines."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_target_aspect_ratio(self) -> float:
        return 10.5

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 13.0

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.TAPERED

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Implement a highly stable airfoil (e.g. Clark Y or NACA 4412) to minimize attitude deviations.",
            "Integrate wing tip winglets to reduce wingtip vortices and stabilize yaw.",
        ]


class CargoWingStrategy(BaseWingStrategy):
    """Strategy for heavy cargo transporters requiring structural rigidity and lift capability."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_target_aspect_ratio(self) -> float:
        return 8.2

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 35.0  # Heavy wing loading for flight speed and structural scaling

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.TRAPEZOIDAL

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Select high-lift airfoils (e.g. Selig 1223 or Eppler 423) to generate maximum lift during takeoff.",
            "Equip slotted flaps across 60% of trailing span to reduce landing runway requirements.",
            "Construct dual shear web spars to handle high torsional moments from twin wing engines.",
        ]


class AgricultureWingStrategy(BaseWingStrategy):
    """Strategy for agricultural sprayers requiring maneuverability and wing booms."""

    @property
    def name(self) -> str:
        return "Agriculture"

    def get_target_aspect_ratio(self) -> float:
        return 7.5

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 22.0

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.RECTANGULAR  # simple, sturdy, benign stall

    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        # Low wings need higher dihedral for roll stability
        return 0.0, 5.0, 3.0

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Reinforce the wing trailing spar to accept spray boom mounting loads.",
            "Ensure wing tips have high-strength skid plates to protect control surfaces in low altitude turns.",
        ]


class TrainingWingStrategy(BaseWingStrategy):
    """Strategy for trainers requiring simple manufacturing and docile stall behavior."""

    @property
    def name(self) -> str:
        return "Training"

    def get_target_aspect_ratio(self) -> float:
        return 6.5

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 8.5  # docile slow speeds

    def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
        if requirements.preferred_planform is not None:
            return requirements.preferred_planform
        return PlanformType.RECTANGULAR

    def get_sweep_and_dihedral(self, requirements: WingRequirements) -> Tuple[float, float, float]:
        # High dihedral for self-righting stability
        return 0.0, 6.0, 2.0

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Use a flat-bottomed airfoil (e.g. Clark Y) for extreme ease of construction and docile stall behavior.",
            "Incorporate rubber band wing-retention mountings to isolate impact energy during crashes.",
        ]


class ResearchWingStrategy(BaseWingStrategy):
    """Strategy for research and academic UAV platforms."""

    @property
    def name(self) -> str:
        return "Research"

    def get_target_aspect_ratio(self) -> float:
        return 9.5

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 14.0

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Design the wing panels with modular split joints to allow span extensions for varying configurations.",
            "Provide internal conduit routing in the leading edge for sensor wiring.",
        ]


class BalancedWingStrategy(BaseWingStrategy):
    """Default balanced strategy for general configurations."""

    @property
    def name(self) -> str:
        return "Balanced"

    def get_target_aspect_ratio(self) -> float:
        return 8.5

    def get_typical_wing_loading_kg_m2(self) -> float:
        return 15.0

    def get_recommendations(self, geometry: WingGeometry) -> List[str]:
        return [
            "Use a standard NACA 4415 airfoil for clean, multi-role cruise capabilities.",
            "Install dual aileron servos for redundancy and precise lateral control.",
        ]
