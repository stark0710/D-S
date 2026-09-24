"""
Fixed-Wing Tail Strategy Subsystem

Purpose:
    Defines the `TailStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates target horizontal/vertical tail volume coefficients, control surface ratios,
    taper, sweep, and typical configuration preferences (Conventional, V-Tail, Twin Boom) based on mission type.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis


class TailStrategy(ABC):
    """
    Abstract base class for all fixed-wing tail selection strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        """
        Target horizontal and vertical volume coefficients.
        
        Returns:
            Tuple[float, float]: (target_V_h, target_V_v)
        """
        pass

    @abstractmethod
    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        """
        Target aspect ratios.
        
        Returns:
            Tuple[float, float]: (horizontal_AR, vertical_AR)
        """
        pass

    @abstractmethod
    def get_sweep_and_taper(self) -> Tuple[float, float, float, float]:
        """
        Horizontal and vertical sweep and taper settings.
        
        Returns:
            Tuple[float, float, float, float]: (horiz_sweep_deg, horiz_taper, vert_sweep_deg, vert_taper)
        """
        pass

    @abstractmethod
    def select_tail_style(self, requirements: TailRequirements) -> TailConfigType:
        """Determines the tail assembly style."""
        pass

    @abstractmethod
    def get_control_surface_ratios(self) -> Tuple[float, float]:
        """
        Target chord ratios.
        
        Returns:
            Tuple[float, float]: (elevator_chord_ratio, rudder_chord_ratio)
        """
        pass

    @abstractmethod
    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        """Generates detailed tail design advice."""
        pass


class BaseTailStrategy(TailStrategy):
    """
    Common base implementation of TailStrategy.
    """

    def get_sweep_and_taper(self) -> Tuple[float, float, float, float]:
        # Default: 0 deg horiz sweep, 0.7 horiz taper, 20 deg vert sweep, 0.6 vert taper
        return 0.0, 0.7, 20.0, 0.6

    def select_tail_style(self, requirements: TailRequirements) -> TailConfigType:
        if requirements.preferred_tail_configuration is not None:
            return requirements.preferred_tail_configuration

        # Fallback to configuration selection layout
        layout = requirements.configuration_result.selected_configuration
        tail_val = layout.get("tail_configuration", "Conventional")
        
        # Match config string to enum
        for style in TailConfigType:
            if style.value.lower() == tail_val.lower():
                return style
        return TailConfigType.CONVENTIONAL

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        return [
            "Use stiff hinge mechanisms to prevent control surface flutter at high speeds.",
            "Verify trim authority under maximum payload and forward Center of Gravity limits.",
        ]


class LongEnduranceTailStrategy(BaseTailStrategy):
    """Strategy optimized for low drag and lightweight structural configurations."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.45, 0.035  # lower volumes to minimize skin friction drag

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 5.5, 2.5  # higher aspect ratio horizontal stabilizer reduces induced drag

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.25, 0.25  # minimal control surface chord ratio since maneuvering is gentle

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Select V-Tail or Twin Boom configurations to minimize parasite drag and interference.",
            "Design horizontal tail span within wing dihedral tips to avoid ground strikes during rotation.",
        ])
        return recs


class SurveyTailStrategy(BaseTailStrategy):
    """Strategy optimized for steady tracking mapping runs."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.50, 0.040

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 4.5, 2.0

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.28, 0.28

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Use Conventional or T-Tail designs to keep elevator out of main pusher propeller wake wash.",
        ])
        return recs


class CargoTailStrategy(BaseTailStrategy):
    """Strategy optimized for heavy payloads and wide CG stability ranges."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.65, 0.050  # Large volumes are required to counter large CG travel under cargo loads

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 4.0, 1.8  # sturdy low aspect ratio

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.35, 0.35  # wide elevator/rudder chord for maximum pitch/yaw control authority

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Cargo loading causes significant CG movement. Confirm trim authority at both extreme forward and aft CG.",
            "For Twin Boom tail styles, ensure horizontal tail spar handles high torsional loads under side-slip.",
        ])
        return recs


class TrainerTailStrategy(BaseTailStrategy):
    """Strategy optimized for predictability and easy repair."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.55, 0.045  # high pitch/yaw damping

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 4.0, 1.5

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.30, 0.30

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Use thick symmetrical airfoils (e.g. NACA 0012) on tail surfaces for linear and docile control.",
        ])
        return recs


class AerobaticTailStrategy(BaseTailStrategy):
    """Strategy optimized for maximum pitch/yaw authority and quick recovery."""

    @property
    def name(self) -> str:
        return "Aerobatic"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.50, 0.040

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 4.5, 2.0

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.40, 0.40  # extremely wide elevator/rudder chord ratios for high-rate rotation

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        recs.extend([
            "Aerobatic pitch rates require deflection limit brackets of +/- 35 degrees on elevators.",
        ])
        return recs


class BalancedTailStrategy(BaseTailStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"

    def get_target_volume_coefficients(self) -> Tuple[float, float]:
        return 0.50, 0.040

    def get_typical_aspect_ratios(self) -> Tuple[float, float]:
        return 4.5, 2.0

    def get_control_surface_ratios(self) -> Tuple[float, float]:
        return 0.30, 0.30

    def get_recommendations(self, analysis: TailAnalysis) -> List[str]:
        recs = super().get_recommendations(analysis)
        return recs
