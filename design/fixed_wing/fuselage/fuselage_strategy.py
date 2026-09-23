"""
Fixed-Wing Fuselage Strategy Subsystem

Purpose:
    Defines the `FuselageStrategy` base class and concrete strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates target fineness ratios, cross sections, and structural styles
    (Conventional, Pod-and-Boom, Twin Boom) based on mission type.
"""

from abc import ABC, abstractmethod
from typing import List
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements, FuselageType
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysis


class FuselageStrategy(ABC):
    """
    Abstract base class for all fixed-wing fuselage selection strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_fuselage_type(self, requirements: FuselageRequirements) -> FuselageType:
        """Determines the structural fuselage layout style."""
        pass

    @abstractmethod
    def get_typical_fineness_ratio(self) -> float:
        """Target length-to-diameter ratio."""
        pass

    @abstractmethod
    def get_cross_section_type(self) -> str:
        """Cross-sectional profile shape (Rectangular, Circular, etc.)."""
        pass

    @abstractmethod
    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        """Generates detailed fuselage and component design advice."""
        pass


class BaseFuselageStrategy(FuselageStrategy):
    """
    Common base implementation of FuselageStrategy.
    """

    def select_fuselage_type(self, requirements: FuselageRequirements) -> FuselageType:
        if requirements.preferred_fuselage_type is not None:
            return requirements.preferred_fuselage_type

        # Fallback to configuration selection layout
        layout = requirements.configuration_result.selected_configuration
        tail_val = layout.get("tail_configuration", "")
        
        if tail_val == "Twin Boom":
            return FuselageType.TWIN_BOOM
        elif tail_val in ("Tailless", "Flying Wing"):
            return FuselageType.FLYING_WING_CENTER
        
        return FuselageType.CONVENTIONAL

    def get_typical_fineness_ratio(self) -> float:
        return 6.5

    def get_cross_section_type(self) -> str:
        return "Rectangular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        return [
            "Use vibration-damping gel pads under the Flight Controller to isolate high-frequency propeller vibration.",
            "Route power wiring along the fuselage floor and signal wires along the roof to avoid EM interference.",
        ]


class LongEnduranceFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for low drag and lightweight structural configurations."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def select_fuselage_type(self, requirements: FuselageRequirements) -> FuselageType:
        if requirements.preferred_fuselage_type is not None:
            return requirements.preferred_fuselage_type
        # Pod-and-boom minimizes fuselage skin friction drag
        return FuselageType.POD_AND_BOOM

    def get_typical_fineness_ratio(self) -> float:
        return 7.5  # Slender body for minimum drag

    def get_cross_section_type(self) -> str:
        return "Circular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Use carbon fiber boom extensions for the tail to minimize fuselage tail cone drag.",
            "Intake scoops should be placed in the high-pressure stagnation zone on the nose for motor cooling.",
        ])
        return recs


class SurveyFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for downward-facing sensor mounts."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_typical_fineness_ratio(self) -> float:
        return 6.0

    def get_cross_section_type(self) -> str:
        return "Rectangular"  # Flat bottom simplifies camera portal cutout

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Design a flat bottom access panel with optical glass window for nadir photogrammetry camera placement.",
            "Isolate the camera gimbal structure from the main battery bay load frame.",
        ])
        return recs


class CargoFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for loading and carrying high volume box payloads."""

    @property
    def name(self) -> str:
        return "Cargo"

    def select_fuselage_type(self, requirements: FuselageRequirements) -> FuselageType:
        if requirements.preferred_fuselage_type is not None:
            return requirements.preferred_fuselage_type
        # Twin boom tail allows clear access to rear fuselage cargo doors
        return FuselageType.TWIN_BOOM

    def get_typical_fineness_ratio(self) -> float:
        return 5.0  # Stubby body to maximize volume payload bay width

    def get_cross_section_type(self) -> str:
        return "Rectangular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Cargo loading causes significant CG movement. Install slide rails to easily lock cargo boxes at the CG center.",
            "Install a quick-release rear hatch for loading cargo packages without removing the wing.",
        ])
        return recs


class AgricultureFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for liquid spray tank plumbing."""

    @property
    def name(self) -> str:
        return "Agriculture"

    def get_typical_fineness_ratio(self) -> float:
        return 5.5

    def get_cross_section_type(self) -> str:
        return "Circular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Locate liquid pesticide tanks exactly on the CG center to avoid CG shift as chemical fluid empties.",
            "Provide sealed drainage holes at the bottom of the fuselage to drain any chemical spillages.",
        ])
        return recs


class TrainerFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for ease of build and impact resilience."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_typical_fineness_ratio(self) -> float:
        return 6.0

    def get_cross_section_type(self) -> str:
        return "Rectangular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Use heavy plywood doublers around the nose landing gear block to handle hard landings.",
            "Use rubber band wing mounts rather than hard bolts for automatic wing pop-off crash protection.",
        ])
        return recs


class ResearchFuselageStrategy(BaseFuselageStrategy):
    """Strategy optimized for custom sensors and telemetry payloads."""

    @property
    def name(self) -> str:
        return "Research"

    def get_typical_fineness_ratio(self) -> float:
        return 6.5

    def get_cross_section_type(self) -> str:
        return "Rectangular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Install breadboard mounting plates inside the payload compartment for sensor prototyping.",
        ])
        return recs


class BalancedFuselageStrategy(BaseFuselageStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"

    def get_typical_fineness_ratio(self) -> float:
        return 6.5

    def get_cross_section_type(self) -> str:
        return "Rectangular"

    def get_recommendations(self, analysis: FuselageAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        return recs
