"""
Fixed-Wing Mission Strategy Subsystem

Purpose:
    Defines the `MissionStrategy` base class and concrete strategy implementations
    for various mission types.

Role in Architecture:
    The strategy pattern isolates the mission-specific physics parameters, weight estimations,
    recommendations, and complexity modifiers. The engine calls the active strategy to populate
    the details of the mission profile.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
)
from backend.design.fixed_wing.mission.mission_profile import MissionProfile


class MissionStrategy(ABC):
    """
    Abstract base class for all fixed-wing mission strategies.
    
    Adheres to:
        - Strategy Pattern: Encapsulates mission-specific algorithms and recommendations.
        - Dependency Inversion: Exposes a clean abstract interface.
    """

    @property
    @abstractmethod
    def category(self) -> MissionCategory:
        """Returns the mission category this strategy belongs to."""
        pass

    @abstractmethod
    def estimate_physics(self, requirements: MissionRequirements, air_density: float) -> Dict[str, float]:
        """
        Estimates the mission-specific physics characteristics (energy demand, emphases, risks).

        Args:
            requirements (MissionRequirements): The raw mission requirements.
            air_density (float): Standard air density at target altitude.

        Returns:
            Dict[str, float]: Dict containing estimated values for:
                - 'energy_demand_kwh'
                - 'cruise_emphasis'
                - 'payload_emphasis'
                - 'launch_recovery_complexity'
                - 'environmental_complexity'
                - 'operational_risk_score'
        """
        pass

    @abstractmethod
    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        """Returns a list of engineering recommendations tailored for the specific mission strategy."""
        pass


class BaseMissionStrategy(MissionStrategy):
    """
    Common base implementation of MissionStrategy that handles generic fixed-wing physics estimations.
    Specific strategies inherit from this to override specific ratios or parameters.
    """

    def _estimate_mtow(self, requirements: MissionRequirements) -> float:
        """Estimates Maximum Takeoff Weight (MTOW) in kg based on payload weight and typical payload fraction."""
        payload_fraction = self.get_target_payload_fraction()
        estimated_mtow = requirements.payload_kg / payload_fraction
        
        if requirements.maximum_takeoff_weight_limit_kg is not None:
            # Reconcile with user limits: if user limit is lower, try to respect it but bound logically
            return min(estimated_mtow, requirements.maximum_takeoff_weight_limit_kg)
        return estimated_mtow

    @abstractmethod
    def get_target_payload_fraction(self) -> float:
        """Returns target ratio of payload mass to MTOW."""
        pass

    @abstractmethod
    def get_lift_to_drag_ratio(self) -> float:
        """Returns estimated Lift-to-Drag ratio (L/D) at cruise."""
        pass

    def estimate_physics(self, requirements: MissionRequirements, air_density: float) -> Dict[str, float]:
        # Estimate MTOW
        mtow = self._estimate_mtow(requirements)
        
        # Physics calculations
        # Speed in m/s
        v_cruise = requirements.cruise_speed_kmh / 3.6
        
        # Lift-to-Drag ratio
        l_d = self.get_lift_to_drag_ratio()
        
        # Propulsion system efficiency (typical: 60-70% for small UAVs)
        prop_efficiency = 0.65
        
        # Drag Power = Thrust * Velocity = (Weight / L_D) * Velocity
        # Weight in Newtons
        weight_n = mtow * 9.80665
        power_required_w = (weight_n / l_d) * v_cruise / prop_efficiency
        
        # Avionics and payload power baseline (typical small fixed-wing)
        avionics_payload_w = 20.0 + (requirements.payload_kg * 10.0) # baseline payload power
        total_power_w = power_required_w + avionics_payload_w
        
        # Energy in kWh
        endurance_hours = requirements.flight_time_min / 60.0
        energy_demand_kwh = (total_power_w * endurance_hours) / 1000.0

        # Base complexity factor for launch and recovery
        launch_comp = 0.3
        if requirements.launch_method in (LaunchMethod.CATAPULT, LaunchMethod.BUNGEE):
            launch_comp += 0.3
        elif requirements.launch_method == LaunchMethod.RUNWAY:
            launch_comp += 0.1

        landing_comp = 0.3
        if requirements.landing_method in (LandingMethod.NET_RECOVERY, LandingMethod.PARACHUTE):
            landing_comp += 0.4
        elif requirements.landing_method == LandingMethod.BELLY_LANDING:
            landing_comp += 0.2

        launch_recovery_complexity = min(1.0, (launch_comp + landing_comp) / 2.0)

        # Base complexity factor for environment
        env_comp = 0.2
        if requirements.environment in (EnvironmentType.MOUNTAIN, EnvironmentType.MARINE):
            env_comp += 0.5
        elif requirements.environment in (EnvironmentType.DESERT, EnvironmentType.FOREST):
            env_comp += 0.3
        elif requirements.environment == EnvironmentType.URBAN:
            env_comp += 0.6
        
        environmental_complexity = min(1.0, env_comp)

        # Base operational risk
        risk = 0.2
        if requirements.payload_kg > 10.0:
            risk += 0.2
        if requirements.flight_time_min > 180.0:
            risk += 0.2
        if environmental_complexity > 0.5:
            risk += 0.2
        operational_risk_score = min(1.0, risk)

        return {
            "energy_demand_kwh": round(energy_demand_kwh, 4),
            "cruise_emphasis": self.get_cruise_emphasis(),
            "payload_emphasis": self.get_payload_emphasis(),
            "launch_recovery_complexity": round(launch_recovery_complexity, 2),
            "environmental_complexity": round(environmental_complexity, 2),
            "operational_risk_score": round(operational_risk_score, 2),
        }

    def get_cruise_emphasis(self) -> float:
        return 0.5

    def get_payload_emphasis(self) -> float:
        return 0.5


class SurveyMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for Survey missions."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.SURVEY

    def get_target_payload_fraction(self) -> float:
        return 0.20  # Lighter camera payloads

    def get_lift_to_drag_ratio(self) -> float:
        return 14.0  # Clean aerodynamics for survey grids

    def get_cruise_emphasis(self) -> float:
        return 0.7  # High emphasis on range & speed stability

    def get_payload_emphasis(self) -> float:
        return 0.3

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Use a high-resolution downward-facing RGB/Multispectral camera payload.",
            "Optimize wing design for steady roll/pitch holding to ensure clear mapping images.",
            "Design for an autopilot system capable of grid-based waypoint flight patterns.",
        ]


class LongEnduranceMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for Long Endurance missions."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.LONG_ENDURANCE

    def get_target_payload_fraction(self) -> float:
        return 0.15  # Minimal payload weight to maximize fuel/battery fraction

    def get_lift_to_drag_ratio(self) -> float:
        return 18.0  # Glider-like high aspect ratio wing for maximum glide and efficiency

    def get_cruise_emphasis(self) -> float:
        return 0.9  # Extreme cruise endurance emphasis

    def get_payload_emphasis(self) -> float:
        return 0.1

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Select high aspect ratio wings (AR > 12) with laminar flow airfoils.",
            "Consider gas-electric hybrid propulsion or high-density Li-Ion cell packs.",
            "Minimize fuselage frontal area to reduce parasitic drag.",
        ]


class SurveillanceMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for tactical surveillance, security patrols, and aerial inspection."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.SURVEILLANCE

    def get_target_payload_fraction(self) -> float:
        return 0.25  # Electro-optical / infrared gimbal payload capacity

    def get_lift_to_drag_ratio(self) -> float:
        return 13.5  # Balanced tactical aerodynamic efficiency with sensor turret / pod drag

    def get_cruise_emphasis(self) -> float:
        return 0.6  # Balanced between loiter endurance and loiter maneuvering

    def get_payload_emphasis(self) -> float:
        return 0.4

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Select moderate aspect ratio wings (AR 8.0 - 10.0) with stable handling airfoils.",
            "Integrate nose or under-fuselage sensor gimbals with vibration isolation.",
            "Maintain adequate wing chord margins to accommodate fuselage payload bay integration.",
        ]


class CargoMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for Cargo and delivery missions."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.CARGO

    def get_target_payload_fraction(self) -> float:
        return 0.35  # Heavy payload relative to empty weight

    def get_lift_to_drag_ratio(self) -> float:
        return 11.0  # High lift airfoils, thicker wing sections, larger drag penalty

    def get_cruise_emphasis(self) -> float:
        return 0.3

    def get_payload_emphasis(self) -> float:
        return 0.8  # Strong emphasis on payload lift & volume

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Design a structural center section with high wing spars to support heavy loads.",
            "Use thick high-lift airfoils (e.g. NACA 4415 or Selig 1223) to increase lift capability.",
            "Incorporate a dedicated internal cargo bay near the CG location to maintain stability regardless of load.",
        ]


class AgricultureMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for agricultural spraying or field assessment."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.AGRICULTURE

    def get_target_payload_fraction(self) -> float:
        return 0.30

    def get_lift_to_drag_ratio(self) -> float:
        return 10.0  # Low speed, low altitude, high payload drag

    def get_cruise_emphasis(self) -> float:
        return 0.4

    def get_payload_emphasis(self) -> float:
        return 0.6

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Equip liquid spray tank or specialized remote sensors close to CG.",
            "Utilize a robust landing gear design for rural or semi-prepared ground landings.",
            "Implement high-lift devices (flaps) for quick turnarounds and short field operations.",
        ]


class ResearchMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for atmospheric or specialized academic research."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.RESEARCH

    def get_target_payload_fraction(self) -> float:
        return 0.22

    def get_lift_to_drag_ratio(self) -> float:
        return 13.0

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Provide modular payload bays with standardized power and data interfaces.",
            "Ensure low electromagnetic interference (EMI) around sensor payload bays.",
            "Design for operational robustness to survive non-standard altitudes and atmospheric profiles.",
        ]


class TrainingMissionStrategy(BaseMissionStrategy):
    """Strategy optimized for training, ease of piloting, and cost efficiency."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.TRAINING

    def get_target_payload_fraction(self) -> float:
        return 0.18

    def get_lift_to_drag_ratio(self) -> float:
        return 12.0

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Use durable material selection (e.g. EPP foam) for easy repair.",
            "Implement high dihedral wing configurations for passive aerodynamic stability.",
            "Integrate flight controller training mode with automated return-to-home overrides.",
        ]


class BalancedMissionStrategy(BaseMissionStrategy):
    """Default balanced strategy for general or custom missions."""

    @property
    def category(self) -> MissionCategory:
        return MissionCategory.CUSTOM  # also used for Racing, Mapping, Surveillance, Balanced, etc.

    def get_target_payload_fraction(self) -> float:
        return 0.25

    def get_lift_to_drag_ratio(self) -> float:
        return 13.0

    def get_recommendations(self, requirements: MissionRequirements, profile: MissionProfile) -> List[str]:
        return [
            "Design a clean, multi-role configuration with a balance of cruise range and payload capacity.",
            "Ensure the propulsion system is efficient at the target cruise speed while retaining power margins.",
        ]
