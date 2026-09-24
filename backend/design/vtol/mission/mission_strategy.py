"""
VTOL Mission Strategy Subsystem

Purpose:
    Defines the `MissionStrategy` abstract base class and concrete strategies
    for different VTOL mission categories.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from backend.design.vtol.mission.mission_requirements import (
    MissionRequirements,
    VTOLMissionCategory,
    TakeoffMethod,
    LandingMethod,
    EnvironmentType,
)
from backend.design.vtol.mission.mission_profile import MissionProfile


class MissionStrategy(ABC):
    """
    Abstract base class defining the interface for VTOL mission strategies.
    """

    @property
    @abstractmethod
    def category(self) -> VTOLMissionCategory:
        """The mission category this strategy represents."""
        pass

    @abstractmethod
    def get_hover_priority(self) -> float:
        """Returns hover flight regime priority (0.0 to 1.0)."""
        pass

    @abstractmethod
    def get_cruise_priority(self) -> float:
        """Returns cruise flight regime priority (0.0 to 1.0)."""
        pass

    @abstractmethod
    def get_transition_complexity(self) -> float:
        """Returns transition phase baseline complexity (0.0 to 1.0)."""
        pass

    @abstractmethod
    def get_lift_to_drag_ratio(self) -> float:
        """Returns typical Lift-to-Drag ratio at cruise."""
        pass

    @abstractmethod
    def get_hover_thrust_to_weight(self) -> float:
        """Returns required hover thrust-to-weight ratio."""
        pass

    @abstractmethod
    def get_target_payload_fraction(self) -> float:
        """Returns target ratio of payload weight to MTOW."""
        pass

    @abstractmethod
    def get_hover_power_efficiency_index(self) -> float:
        """Returns motor/propeller efficiency factor in hover (0.0 to 1.0)."""
        pass

    @abstractmethod
    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        """Provides custom engineering recommendations for the sizing team."""
        pass


class BaseMissionStrategy(MissionStrategy):
    """
    Base implementation containing physical estimation logic common to most VTOL configurations.
    """

    def estimate_mtow(self, requirements: MissionRequirements) -> float:
        """Estimates Maximum Takeoff Weight (MTOW) based on payload fraction."""
        payload_frac = self.get_target_payload_fraction()
        estimated = requirements.payload_kg / payload_frac

        # Reconcile with MTOW limit if provided by the user
        limit = requirements.metadata.get("maximum_takeoff_weight_limit_kg")
        if limit is not None:
            return min(estimated, float(limit))
        return estimated

    def get_hover_power_efficiency_index(self) -> float:
        return 0.70  # Default efficiency for hover rotors

    def get_hover_thrust_to_weight(self) -> float:
        return 1.30  # Default thrust margin

    def get_transition_complexity(self) -> float:
        return 0.50

    def estimate_physics(
        self,
        requirements: MissionRequirements,
        mtow: float,
        air_density_hover: float,
        air_density_cruise: float,
    ) -> Dict[str, float]:
        """
        Estimates the mission phase energies and overall metrics.
        """
        # 1. Hover segment
        # Sized hover power using basic momentum theory approximation
        # P_hover = (Weight * gravity) * (induced velocity factor) / efficiency
        weight_n = mtow * 9.80665
        hover_thrust_margin = self.get_hover_thrust_to_weight()
        eff_hover = self.get_hover_power_efficiency_index()
        # Scale factor representing typical W/N for medium-scale multirotors
        power_hover_w = (weight_n) * 11.5 * (1.20 / air_density_hover) / eff_hover
        energy_hover_kwh = (power_hover_w * (requirements.hover_reqs.hover_duration_min / 60.0)) / 1000.0

        # 2. Transition segment
        # High power draw during transition (typically 1.4x hover power)
        power_trans_w = power_hover_w * 1.4
        energy_trans_kwh = (power_trans_w * (requirements.transition_reqs.transition_duration_s / 3600.0)) / 1000.0

        # 3. Cruise segment
        v_cruise = requirements.cruise_reqs.cruise_speed_kmh / 3.6
        l_d = self.get_lift_to_drag_ratio()
        eff_prop = 0.65  # cruise propeller efficiency
        power_cruise_w = (weight_n / l_d) * v_cruise / eff_prop

        # Avionics and payload power baseline
        avionics_payload_w = 25.0 + (requirements.payload_kg * 8.0)
        total_cruise_power_w = power_cruise_w + avionics_payload_w
        energy_cruise_kwh = (total_cruise_power_w * (requirements.cruise_reqs.cruise_endurance_min / 60.0)) / 1000.0

        # Combined totals
        total_energy = energy_hover_kwh + energy_trans_kwh + energy_cruise_kwh

        # Complexity components
        env_comp = 0.1
        if requirements.environment == EnvironmentType.URBAN:
            env_comp += 0.5
        elif requirements.environment in (EnvironmentType.MOUNTAIN, EnvironmentType.MARINE):
            env_comp += 0.4
        elif requirements.environment in (EnvironmentType.FOREST, EnvironmentType.DESERT):
            env_comp += 0.2

        launch_comp = 0.2
        if requirements.takeoff_method in (TakeoffMethod.RUNWAY, TakeoffMethod.CATAPULT):
            launch_comp += 0.1

        recovery_comp = 0.2
        if requirements.landing_method == LandingMethod.BELLY_LANDING:
            recovery_comp += 0.3
        elif requirements.landing_method == LandingMethod.PARACHUTE:
            recovery_comp += 0.1

        risk_score = 0.15
        if requirements.payload_kg > 15.0:
            risk_score += 0.20
        if requirements.max_altitude_m > 3000.0:
            risk_score += 0.15
        if total_energy > 2.0:
            risk_score += 0.20

        complexity_val = min(1.0, (env_comp + launch_comp + recovery_comp + risk_score) / 4.0 + self.get_transition_complexity() * 0.4)

        return {
            "power_hover_w": round(power_hover_w, 1),
            "power_cruise_w": round(total_cruise_power_w, 1),
            "energy_hover_kwh": round(energy_hover_kwh, 4),
            "energy_transition_kwh": round(energy_trans_kwh, 4),
            "energy_cruise_kwh": round(energy_cruise_kwh, 4),
            "total_energy_kwh": round(total_energy, 4),
            "complexity_score": round(complexity_val, 2),
            "risk_score": round(risk_score, 2),
        }


class SurveyMissionStrategy(BaseMissionStrategy):
    """Optimized for long-range, grid-based mapping and survey tasks."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.SURVEY

    def get_hover_priority(self) -> float:
        return 0.30

    def get_cruise_priority(self) -> float:
        return 0.70

    def get_lift_to_drag_ratio(self) -> float:
        return 13.5

    def get_target_payload_fraction(self) -> float:
        return 0.18

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Use a rigid multi-rotor wing clamp design (e.g. Lift+Cruise) to maximize stability during mapping sweeps.",
            "Select high-efficiency cruise propellers to minimize cruise power draw.",
            "Integrate high-accuracy RTK GPS receivers to ensure accurate georeferencing.",
        ]


class CargoMissionStrategy(BaseMissionStrategy):
    """Optimized for heavy payload lifting and delivery missions."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CARGO

    def get_hover_priority(self) -> float:
        return 0.60

    def get_cruise_priority(self) -> float:
        return 0.40

    def get_lift_to_drag_ratio(self) -> float:
        return 10.0

    def get_target_payload_fraction(self) -> float:
        return 0.32

    def get_hover_thrust_to_weight(self) -> float:
        return 1.45  # More hover margin for payload hoisting

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Ensure structural motor booms are optimized for torsion loads under heavy payloads.",
            "Provide mechanical/magnetic cargo quick-release undercarriage mounts.",
            "Design for thick high-lift airfoils to support large operational empty weight margins.",
        ]


class MappingMissionStrategy(BaseMissionStrategy):
    """Optimized for high-altitude orthomosaic mapping."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MAPPING

    def get_hover_priority(self) -> float:
        return 0.25

    def get_cruise_priority(self) -> float:
        return 0.75

    def get_lift_to_drag_ratio(self) -> float:
        return 14.5

    def get_target_payload_fraction(self) -> float:
        return 0.15

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Utilize composite structural layups to reduce aircraft weight and maximize range.",
            "Incorporate a nadir camera port with vibration isolators.",
            "Configure automatic airspeed sensors to counter high-altitude headwind transitions.",
        ]


class LongEnduranceMissionStrategy(BaseMissionStrategy):
    """Optimized to stay aloft for maximum duration."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.LONG_ENDURANCE

    def get_hover_priority(self) -> float:
        return 0.20

    def get_cruise_priority(self) -> float:
        return 0.80

    def get_lift_to_drag_ratio(self) -> float:
        return 16.5  # Streamlined aspect ratio and airfoil

    def get_target_payload_fraction(self) -> float:
        return 0.12

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Select high aspect ratio wings with low drag profiles.",
            "Utilize a tilt-rotor configuration to reduce hover propulsion weight penalty.",
            "Verify cell temperature limits under prolonged low-current discharge.",
        ]


class EmergencyMissionStrategy(BaseMissionStrategy):
    """Optimized for rapid response and high reliability."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.EMERGENCY_RESPONSE

    def get_hover_priority(self) -> float:
        return 0.50

    def get_cruise_priority(self) -> float:
        return 0.50

    def get_lift_to_drag_ratio(self) -> float:
        return 11.0

    def get_target_payload_fraction(self) -> float:
        return 0.25

    def get_hover_thrust_to_weight(self) -> float:
        return 1.40  # Extra control margin under gusty rescue conditions

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Include dual-BEC avionics power supply rails for maximum reliability.",
            "Ensure IP54 rain and dust ingress sealing on electronics bays.",
            "Design for rapid battery swapping during emergency turnaround times.",
        ]


class MilitaryMissionStrategy(BaseMissionStrategy):
    """Optimized for tactical surveillance and rugged operations."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.MILITARY

    def get_hover_priority(self) -> float:
        return 0.40

    def get_cruise_priority(self) -> float:
        return 0.60

    def get_lift_to_drag_ratio(self) -> float:
        return 12.0

    def get_target_payload_fraction(self) -> float:
        return 0.28

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Incorporate military-grade encrypted RF data links.",
            "Structure components for quick field assembly without specialty tools.",
            "Verify low-visibility paint schemes and noise-dampening prop shapes.",
        ]


class ResearchMissionStrategy(BaseMissionStrategy):
    """Optimized for atmospheric sensors and custom payloads."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.RESEARCH

    def get_hover_priority(self) -> float:
        return 0.45

    def get_cruise_priority(self) -> float:
        return 0.55

    def get_lift_to_drag_ratio(self) -> float:
        return 12.5

    def get_target_payload_fraction(self) -> float:
        return 0.20

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Incorporate standardized payload bay rail interfaces (e.g. modular brackets).",
            "Provide ample auxiliary 5V/12V regulated power rails.",
            "Verify electromagnetic shielding between telemetry antennas and research sensors.",
        ]


class BalancedMissionStrategy(BaseMissionStrategy):
    """General strategy for multi-purpose or custom missions."""

    @property
    def category(self) -> VTOLMissionCategory:
        return VTOLMissionCategory.CUSTOM

    def get_hover_priority(self) -> float:
        return 0.50

    def get_cruise_priority(self) -> float:
        return 0.50

    def get_lift_to_drag_ratio(self) -> float:
        return 12.0

    def get_target_payload_fraction(self) -> float:
        return 0.22

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Ensure a balanced configuration design (e.g. Lift+Cruise) is chosen for ease of maintenance.",
            "Verify that total energy capacity matches requirements with a 15% safety factor.",
        ]
