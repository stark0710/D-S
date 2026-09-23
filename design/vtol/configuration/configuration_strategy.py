"""
VTOL Configuration Strategy Subsystem

Purpose:
    Defines the `ConfigurationStrategy` abstract base and concrete implementations
    for evaluating VTOL layout candidates based on the mission category.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any

from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory, VTOLType
from backend.design.vtol.configuration.configuration_profile import ConfigurationProfile


class ConfigurationStrategy(ABC):
    """
    Interface for VTOL configuration evaluation policies.
    """

    @property
    @abstractmethod
    def category(self) -> VTOLMissionCategory:
        """The mission category this strategy maps to."""
        pass

    @abstractmethod
    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        """Scores compatibility of a VTOL layout configuration (0.0 to 100.0)."""
        pass

    @abstractmethod
    def get_analysis_weights(self) -> Dict[str, float]:
        """Returns scoring weights for configuration engineering trade-offs."""
        pass

    @abstractmethod
    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        """Provides configuration recommendations."""
        pass


class BaseConfigurationStrategy(ConfigurationStrategy):
    """
    Default sizing scoring and parameters for generic configurations.
    """

    def get_analysis_weights(self) -> Dict[str, float]:
        return {
            "hover_efficiency": 0.20,
            "cruise_efficiency": 0.20,
            "transition_complexity": 0.15,
            "structural_simplicity": 0.15,
            "manufacturability": 0.10,
            "redundancy_score": 0.10,
            "maintenance_accessibility": 0.05,
            "scalability": 0.05,
        }

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        return [
            f"Ensure {profile.vtol_type.value} layout incorporates vibration damping for avionics panels.",
            "Verify clear rotor arc clearances under maximum wing deflection loads.",
        ]


class SurveyConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for steady state scanning grids."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.SURVEY

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 80.0,
            VTOLType.TILT_ROTOR: 85.0,
            VTOLType.TILT_WING: 75.0,
            VTOLType.LIFT_CRUISE: 90.0,
            VTOLType.TAIL_SITTER: 60.0,
            VTOLType.VECTORED_THRUST: 85.0,
            VTOLType.TWIN_BOOM_VTOL: 95.0,  # Twin booms are excellent for survey stability
            VTOLType.BOX_WING_VTOL: 70.0,
            VTOLType.HYBRID_VTOL: 90.0,
            VTOLType.CUSTOM: 50.0,
        }
        return scores.get(vtol_type, 60.0)

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Select Lift + Cruise or Twin Boom configurations to separate lift and cruise components for reliability.",
            "Configure vertical lift booms to fold flat during long-distance shipping.",
        ])
        return recs


class CargoConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for high payload capacity and packaging volume."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CARGO

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 85.0,
            VTOLType.TILT_ROTOR: 70.0,
            VTOLType.TILT_WING: 60.0,
            VTOLType.LIFT_CRUISE: 95.0,  # Stable flat fuselage packing
            VTOLType.TAIL_SITTER: 40.0,  # Tail sitters are difficult to load cargo vertically
            VTOLType.VECTORED_THRUST: 75.0,
            VTOLType.TWIN_BOOM_VTOL: 90.0,
            VTOLType.BOX_WING_VTOL: 80.0,
            VTOLType.HYBRID_VTOL: 90.0,
            VTOLType.CUSTOM: 55.0,
        }
        return scores.get(vtol_type, 50.0)

    def get_analysis_weights(self) -> Dict[str, float]:
        weights = super().get_analysis_weights()
        # Elevate hover efficiency and redundancy for heavy lifting safety
        weights["hover_efficiency"] = 0.25
        weights["redundancy_score"] = 0.15
        weights["cruise_efficiency"] = 0.15
        return weights

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Utilize Lift + Cruise setup with at least 8 lift motors (Octo-Coaxial) for single-motor-out redundancy.",
            "Isolate the payload compartment directly beneath the wing center section to keep CG travel neutral.",
        ])
        return recs


class MappingConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for steady nadir cameras at medium altitude."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MAPPING

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 80.0,
            VTOLType.TILT_ROTOR: 85.0,
            VTOLType.TILT_WING: 75.0,
            VTOLType.LIFT_CRUISE: 90.0,
            VTOLType.TAIL_SITTER: 55.0,
            VTOLType.VECTORED_THRUST: 85.0,
            VTOLType.TWIN_BOOM_VTOL: 95.0,
            VTOLType.BOX_WING_VTOL: 70.0,
            VTOLType.HYBRID_VTOL: 90.0,
            VTOLType.CUSTOM: 50.0,
        }
        return scores.get(vtol_type, 60.0)

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Select high wing configurations to maximize camera gimbal field of view.",
            "Install a dedicated lidar-compatible payload pod forward of landing gears.",
        ])
        return recs


class LongEnduranceConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized to stay in the air for maximum range/time."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.LONG_ENDURANCE

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 65.0,
            VTOLType.TILT_ROTOR: 95.0,  # Eliminates lift motor drag in forward flight
            VTOLType.TILT_WING: 90.0,
            VTOLType.LIFT_CRUISE: 75.0,
            VTOLType.TAIL_SITTER: 85.0,  # Highly aerodynamically clean
            VTOLType.VECTORED_THRUST: 90.0,
            VTOLType.TWIN_BOOM_VTOL: 70.0,
            VTOLType.BOX_WING_VTOL: 75.0,
            VTOLType.HYBRID_VTOL: 95.0,
            VTOLType.CUSTOM: 50.0,
        }
        return scores.get(vtol_type, 50.0)

    def get_analysis_weights(self) -> Dict[str, float]:
        weights = super().get_analysis_weights()
        # Cruise efficiency is paramount
        weights["cruise_efficiency"] = 0.35
        weights["hover_efficiency"] = 0.15
        weights["structural_simplicity"] = 0.10
        weights["manufacturability"] = 0.05
        return weights

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Select tilt-rotor setups to remove the parasitic drag of vertical rotors during cruise.",
            "Ensure low-Cd fuselage nose cones are utilized to extend cruise efficiency.",
        ])
        return recs


class EmergencyConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for rapid deployment and storm/wind tolerance."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.EMERGENCY_RESPONSE

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 90.0,  # Highly reliable and simple
            VTOLType.TILT_ROTOR: 70.0,
            VTOLType.TILT_WING: 60.0,
            VTOLType.LIFT_CRUISE: 95.0,  # Simplest transition dynamics
            VTOLType.TAIL_SITTER: 50.0,
            VTOLType.VECTORED_THRUST: 75.0,
            VTOLType.TWIN_BOOM_VTOL: 90.0,
            VTOLType.BOX_WING_VTOL: 70.0,
            VTOLType.HYBRID_VTOL: 85.0,
            VTOLType.CUSTOM: 50.0,
        }
        return scores.get(vtol_type, 60.0)

    def get_analysis_weights(self) -> Dict[str, float]:
        weights = super().get_analysis_weights()
        weights["redundancy_score"] = 0.20
        weights["manufacturability"] = 0.15
        weights["structural_simplicity"] = 0.15
        return weights

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Design with a Lift + Cruise layout to ensure vertical control is independent of forward flight actuators.",
            "Specify waterproof gaskets for all flight electronics access hatches.",
        ])
        return recs


class MilitaryConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for speed, radar signature, and rugged payload deployment."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MILITARY

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        scores = {
            VTOLType.QUADPLANE: 70.0,
            VTOLType.TILT_ROTOR: 90.0,
            VTOLType.TILT_WING: 80.0,
            VTOLType.LIFT_CRUISE: 80.0,
            VTOLType.TAIL_SITTER: 90.0,  # Very stealthy profile
            VTOLType.VECTORED_THRUST: 95.0,
            VTOLType.TWIN_BOOM_VTOL: 75.0,
            VTOLType.BOX_WING_VTOL: 80.0,
            VTOLType.HYBRID_VTOL: 85.0,
            VTOLType.CUSTOM: 50.0,
        }
        return scores.get(vtol_type, 60.0)

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Utilize vectored thrust configurations for stealthy low-drag high-speed operations.",
            "Integrate modular slide-in camera nose pods for easy swap-outs.",
        ])
        return recs


class ResearchConfigurationStrategy(BaseConfigurationStrategy):
    """Optimized for payload modularity and custom sensors."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.RESEARCH

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        # Research values simplicity and stability
        scores = {
            VTOLType.QUADPLANE: 90.0,
            VTOLType.TILT_ROTOR: 75.0,
            VTOLType.TILT_WING: 70.0,
            VTOLType.LIFT_CRUISE: 95.0,
            VTOLType.TAIL_SITTER: 50.0,
            VTOLType.VECTORED_THRUST: 75.0,
            VTOLType.TWIN_BOOM_VTOL: 90.0,
            VTOLType.BOX_WING_VTOL: 75.0,
            VTOLType.HYBRID_VTOL: 85.0,
            VTOLType.CUSTOM: 70.0,
        }
        return scores.get(vtol_type, 60.0)

    def get_recommendations(self, profile: ConfigurationProfile) -> List[str]:
        recs = super().get_recommendations(profile)
        recs.extend([
            "Select Lift + Cruise configuration for its predictable flight dynamics and stable hover testing.",
            "Equip with high capability logging micro-SD slots on companion boards.",
        ])
        return recs


class BalancedConfigurationStrategy(BaseConfigurationStrategy):
    """Fallback balanced strategy."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CUSTOM

    def score_vtol_type(self, vtol_type: VTOLType) -> float:
        return 75.0
