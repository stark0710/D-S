"""
Fixed-Wing Airfoil Strategy Subsystem

Purpose:
    Defines the `AirfoilStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates mission-specific airfoil type constraints (high lift, laminar flow, symmetrical)
    and maps them to root and tip recommendations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements, AirfoilType
from backend.design.fixed_wing.airfoil.airfoil_analysis import AirfoilAnalysis


class AirfoilStrategy(ABC):
    """
    Abstract base class for all fixed-wing airfoil selection strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        """
        Determines the optimal root and tip airfoil names and their distribution layout.

        Returns:
            Tuple[str, str, str]: (root_airfoil_name, tip_airfoil_name, distribution_description)
        """
        pass

    @abstractmethod
    def get_allowed_types(self) -> List[AirfoilType]:
        """List of acceptable airfoil classes allowed by this strategy."""
        pass

    @abstractmethod
    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        """Generates airfoil-specific detailed design advice."""
        pass


class BaseAirfoilStrategy(AirfoilStrategy):
    """
    Common base implementation of AirfoilStrategy.
    """

    def get_allowed_types(self) -> List[AirfoilType]:
        return [AirfoilType.CAMBERED, AirfoilType.SEMI_SYMMETRICAL]

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        return [
            "Maintain smooth wing surface finishes to minimize skin friction drag.",
            "Verify section lift matching between root and tip to avoid excessive aerodynamic twist loads.",
        ]


class LongEnduranceAirfoilStrategy(BaseAirfoilStrategy):
    """Strategy optimized for low profile drag and high lift-to-drag glide efficiency."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_allowed_types(self) -> List[AirfoilType]:
        return [AirfoilType.LAMINAR_FLOW, AirfoilType.REFLEXED, AirfoilType.CAMBERED]

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        layout = requirements.configuration_result.selected_configuration
        tail = layout.get("tail_configuration", "")

        # If it is a tailless flying wing, we MUST select reflexed airfoils for longitudinal pitch stability
        if tail in ("Tailless", "Flying Wing"):
            root = requirements.preferred_root_airfoil or "MH 45"
            tip = requirements.preferred_tip_airfoil or "MH 45"
            dist = "Single Reflexed Airfoil Layout (CG stable)"
        else:
            root = requirements.preferred_root_airfoil or "MH 32"
            tip = requirements.preferred_tip_airfoil or "MH 32"
            dist = "Laminar Flow Linear Loft (low-drag glide)"

        return root, tip, dist

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Select high aspect ratio wing panels to leverage the laminar flow profile of MH 32.",
            "Add turbulator strips at 60% chord if operations at low Reynolds numbers cause laminar separation bubble drag.",
        ])
        return recs


class SurveyAirfoilStrategy(BaseAirfoilStrategy):
    """Strategy optimized for stable flight tracks and camera visibility."""

    @property
    def name(self) -> str:
        return "Survey"

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        root = requirements.preferred_root_airfoil or "Clark Y"
        tip = requirements.preferred_tip_airfoil or "NACA 0012"  # symmetrical tip preserves aileron control
        return root, tip, "Lofted High-Lift Root to Symmetrical Tip (Stall safe)"

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Lofting Clark Y to a symmetrical NACA 0012 tip provides natural aerodynamic twist (washout), "
            "delaying tip-stall and preserving roll control at low landing speeds.",
        ])
        return recs


class CargoAirfoilStrategy(BaseAirfoilStrategy):
    """Strategy optimized for extreme lift capabilities at heavy takeoff weights."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_allowed_types(self) -> List[AirfoilType]:
        return [AirfoilType.HIGH_LIFT, AirfoilType.CAMBERED]

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        root = requirements.preferred_root_airfoil or "Selig S1223"
        tip = requirements.preferred_tip_airfoil or "Clark Y"
        return root, tip, "Lofted Ultra High-Lift Root to High-Lift Tip (maximum load lift)"

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Selig S1223 has high camber and high negative pitching moment. "
            "Ensure the fuselage structure is stiff and can accept tail down-force loads without deflection.",
            "Use large flap linkages to support the heavy loads generated by this airfoil at takeoff.",
        ])
        return recs


class TrainerAirfoilStrategy(BaseAirfoilStrategy):
    """Strategy optimized for slow, forgiving flight characteristics."""

    @property
    def name(self) -> str:
        return "Trainer"

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        root = requirements.preferred_root_airfoil or "Clark Y"
        tip = requirements.preferred_tip_airfoil or "Clark Y"
        return root, tip, "Constant Clark Y Profile (easy construction)"

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Clark Y is highly forgiving. Flat bottom simplifies manual rib cutting and alignment.",
        ])
        return recs


class AerobaticAirfoilStrategy(BaseAirfoilStrategy):
    """Strategy optimized for symmetrical flight and high roll authority."""

    @property
    def name(self) -> str:
        return "Aerobatic"

    def get_allowed_types(self) -> List[AirfoilType]:
        return [AirfoilType.SYMMETRICAL, AirfoilType.SEMI_SYMMETRICAL]

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        root = requirements.preferred_root_airfoil or "NACA 0012"
        tip = requirements.preferred_tip_airfoil or "NACA 0012"
        return root, tip, "Constant Symmetrical Profile (symmetric inverted lift)"

    def get_recommendations(self, analysis: AirfoilAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Symmetrical NACA 0012 airfoil ensures identical flight characteristics in both upright and inverted states.",
        ])
        return recs


class BalancedAirfoilStrategy(BaseAirfoilStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"

    def select_best_airfoils(self, requirements: AirfoilRequirements) -> Tuple[str, str, str]:
        root = requirements.preferred_root_airfoil or "NACA 4412"
        tip = requirements.preferred_tip_airfoil or "Clark Y"
        return root, tip, "Lofted NACA 4412 Root to Clark Y Tip"
