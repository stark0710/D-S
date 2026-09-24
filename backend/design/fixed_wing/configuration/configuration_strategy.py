"""
Fixed-Wing Aircraft Configuration Strategy Subsystem

Purpose:
    Defines the `ConfigurationStrategy` interface and concrete implementations for different aircraft types.

Role in Architecture:
    Each strategy implements the logic to select the optimal layout and evaluate its suitability
    according to its specific design objectives (e.g. range vs. cargo volume).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)


class ConfigurationStrategy(ABC):
    """
    Abstract base class for fixed-wing aircraft configuration strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        """
        Determines the optimal architectural layout mapping.
        
        Returns:
            Dict[str, str]: Mappings for:
                - 'wing_position'
                - 'propulsion_layout'
                - 'tail_configuration'
                - 'landing_gear_configuration'
                - 'engine_count'
                - 'payload_arrangement'
                - 'architecture'
        """
        pass

    @abstractmethod
    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Evaluates scores for suitability, cost, simplicity, etc., for a layout (0.0 to 100.0).

        Returns:
            Dict[str, float]: Mappings for:
                - 'suitability'
                - 'simplicity'
                - 'manufacturability'
                - 'aerodynamics'
                - 'stability'
                - 'maintenance'
                - 'cost'
        """
        pass

    @abstractmethod
    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        """Returns layout-specific recommendations."""
        pass

    @abstractmethod
    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        """Returns the rationale explaining why this layout was selected."""
        pass


class BaseConfigurationStrategy(ConfigurationStrategy):
    """
    Base configuration strategy containing common evaluation scoring heuristics.
    """

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        # Provide base scores that concrete strategies will override or modify
        scores = {
            "suitability": 80.0,
            "simplicity": 75.0,
            "manufacturability": 75.0,
            "aerodynamics": 70.0,
            "stability": 75.0,
            "maintenance": 80.0,
            "cost": 75.0,
        }
        return scores


class LongEnduranceConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for endurance and low-drag gliding flight."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        # Long endurance prefers:
        # High Wing or Shoulder Wing for roll stability and aerodynamic efficiency.
        # Pusher or Twin Boom Pusher to keep nose clean and maximize camera/sensor view.
        # V-Tail to minimize drag (fewer surfaces) or Twin Boom for Pusher stability.
        # Skid (belly landing) to eliminate landing gear drag/weight entirely, or retractable.
        mission = requirements.mission_result.mission_profile
        
        # Override with user preferences if specified
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TWIN_BOOM_PUSHER
        tail = requirements.preferred_tail_configuration or TailConfiguration.TWIN_BOOM
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.SKID
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "CG Bay (Internal)",
            "architecture": "Twin-Boom Pusher Long-Endurance Monoplane",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 95.0,
            "simplicity": 60.0, # Twin boom is structurally more complex
            "manufacturability": 65.0,
            "aerodynamics": 95.0, # Very clean aerodynamic layout
            "stability": 90.0,
            "maintenance": 70.0,
            "cost": 65.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Use a thin, high-aspect ratio wing to minimize induced drag.",
            "Consider a folding propeller to minimize drag during gliding phases.",
            "Integrate solar cells on the wing upper surface if day-long endurance is targeted.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        wing_str = layout.get("wing_position", "High Wing")
        prop_str = layout.get("propulsion_layout", "Pusher")
        tail_str = layout.get("tail_configuration", "Twin-Boom")
        gear_str = layout.get("landing_gear_configuration", "Skids")
        return (
            f"The combination of a {wing_str} and {prop_str} layout with {tail_str} tail was chosen to optimize cruise "
            "aerodynamic efficiency. This layout isolates or clears payloads from propwash while maintaining stability, "
            f"and {gear_str} landing configuration minimizes parasitic drag and structural weight to maximize flight endurance."
        )


class SurveillanceConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for tactical surveillance, security patrols, and aerial inspection."""

    @property
    def name(self) -> str:
        return "Surveillance"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.PUSHER
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        
        ld_method = getattr(requirements.mission_result.mission_profile, "landing_method", None)
        is_runway = ld_method is not None and ("RUNWAY" in str(ld_method).upper())
        default_gear = LandingGearConfiguration.TRICYCLE if is_runway else LandingGearConfiguration.BELLY_LANDING
        gear = requirements.preferred_landing_gear or default_gear
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "Nose / Underside EO/IR Turret",
            "architecture": "High-Wing Pusher Tactical Surveillance Monoplane",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 92.0,
            "simplicity": 80.0,
            "manufacturability": 80.0,
            "aerodynamics": 85.0,
            "stability": 88.0,
            "maintenance": 82.0,
            "cost": 80.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Use a pusher or clean-nose layout to provide unobstructed camera field of view.",
            "Incorporate a rugged landing gear or skid design suited for remote surveillance operations.",
            "Ensure fuselage payload bay dimensions provide ample clearance for the forward gimbal assembly.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        prop_str = layout.get("propulsion_layout", "Pusher")
        wing_str = layout.get("wing_position", "High Wing")
        tail_str = layout.get("tail_configuration", "Conventional")
        return (
            f"A {wing_str} configuration with {prop_str} propulsion and {tail_str} tail was selected for the "
            "Surveillance mission profile. This architecture isolates optical/infrared sensors from motor propwash, "
            "ensures clear forward-and-downward viewing angles, and maintains high roll/pitch stability during low-speed loiter."
        )


class SurveyConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for aerial survey and mapping operations."""

    @property
    def name(self) -> str:
        return "Survey"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.PUSHER
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        
        ld_method = getattr(requirements.mission_result.mission_profile, "landing_method", None)
        is_runway = ld_method is not None and ("RUNWAY" in str(ld_method).upper())
        default_gear = LandingGearConfiguration.TRICYCLE if is_runway else LandingGearConfiguration.BELLY_LANDING
        gear = requirements.preferred_landing_gear or default_gear
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "Under-Nose Camera Bay",
            "architecture": "High-Wing Rear-Pusher Survey Drone",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 92.0,
            "simplicity": 85.0, # High wing pusher is simple to build
            "manufacturability": 85.0,
            "aerodynamics": 80.0,
            "stability": 88.0,
            "maintenance": 90.0,
            "cost": 85.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Use an inverted V-Tail or Conventional tail to clear rear engine exhaust/airflow.",
            "Install a protective dome or sapphire window for the downward camera sensor.",
            "Ensure the fuselage has quick-access hatches for camera payload swapping.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        gear_cfg = layout.get("landing_gear_configuration", "Belly")
        if "Tricycle" in gear_cfg:
            gear_text = "Tricycle landing gear is selected to provide directional control and stability during runway operations."
        elif "Taildragger" in gear_cfg:
            gear_text = "Taildragger landing gear is selected to maximize ground clearance and rough field capability."
        elif "Skids" in gear_cfg:
            gear_text = "Skid landing gear is selected to facilitate safe touchdown on rugged terrain."
        else:
            gear_text = "Belly Landing gear is selected to simplify field operations in semi-prepared rural sites."

        return (
            "A High-Wing Pusher configuration provides a completely unobstructed view for downward-facing "
            "mapping sensors. The high wing offers excellent roll stability, which is vital for consistent photogrammetric overlaps. "
            f"{gear_text}"
        )


class CargoConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for heavy lifting and payload volume."""

    @property
    def name(self) -> str:
        return "Cargo"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TWIN_TRACTOR
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.TRICYCLE
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "2",
            "payload_arrangement": "Fuselage Cargo Compartment (CG)",
            "architecture": "Twin-Engine High-Wing Cargo Transport",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 96.0,
            "simplicity": 70.0,
            "manufacturability": 70.0,
            "aerodynamics": 75.0,
            "stability": 85.0,
            "maintenance": 85.0,
            "cost": 65.0,
        }

    def get_recommendations(self, requirements: MissionRequirements if not hasattr(ConfigurationRequirements, 'mission_result') else ConfigurationRequirements) -> List[str]:
        return [
            "Incorporate a rear-loading ramp or split-nose opening for cargo access.",
            "Use dual spars across the wing center section to support heavy payload weight.",
            "Employ twin engines to distribute thrust loads and provide engine-out flight safety margin.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        return (
            "A Twin-Engine High-Wing layout is the standard for cargo transport. High wings leave the fuselage "
            "low to the ground for easy loading and maintain wing clearance. Twin tractor engines distribute thrust and structural "
            "bending moments, while Tricycle gear ensures stability during heavy taxiing and runway operations."
        )


class AgricultureConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for low-altitude crop spraying and rugged field work."""

    @property
    def name(self) -> str:
        return "Agriculture"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.LOW_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TRACTOR
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.TAILDRAGGER
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "Lower Fuselage Spray Tank",
            "architecture": "Low-Wing Single-Tractor Agricultural Sprayer",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 90.0,
            "simplicity": 85.0,
            "manufacturability": 85.0,
            "aerodynamics": 70.0,
            "stability": 78.0,
            "maintenance": 92.0, # High maintenance accessibility
            "cost": 80.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Mount spray nozzles on trailing edge booms beneath the low wing to utilize prop wash for dispersion.",
            "Protect flight control linkages and electronics from chemical corrosion.",
            "Select a taildragger landing gear for maximum propeller ground clearance on rough soil.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        return (
            "A Low-Wing layout is selected for agricultural spraying because it places the spray booms close "
            "to the crops, maximizing spray downwash. Single-Tractor propulsion is mechanically simple and reliable. "
            "Taildragger gear is ideal for rough, unpaved agricultural strips, providing propeller protection from tall weeds."
        )


class ResearchConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for flexible instrumentation and modular payloads."""

    @property
    def name(self) -> str:
        return "Research"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TRACTOR
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.TRICYCLE
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "Modular Nose/Center Bay",
            "architecture": "High-Wing Conventional Research UAV",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 88.0,
            "simplicity": 90.0,
            "manufacturability": 90.0,
            "aerodynamics": 75.0,
            "stability": 88.0,
            "maintenance": 88.0,
            "cost": 85.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Use modular nose cones and bay swap mechanisms to support diverse sensor groups.",
            "Incorporate external wing hardpoints for atmospheric sampling probes.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        return (
            "A High-Wing Conventional configuration represents a highly predictable, low-risk aerodynamic testbed. "
            "Conventional layouts provide stable, linear handling qualities, making research data acquisition reliable. "
            "Tricycle gear is selected to simplify ground handling during takeoff and landings."
        )


class TrainingConfigurationStrategy(BaseConfigurationStrategy):
    """Strategy optimized for durability, cost, and ease of maintenance."""

    @property
    def name(self) -> str:
        return "Training"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TRACTOR
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.TRICYCLE
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "Fuselage (Internal)",
            "architecture": "High-Wing Tractor Trainer",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 95.0,
            "simplicity": 95.0, # Highly simple structure
            "manufacturability": 95.0,
            "aerodynamics": 70.0,
            "stability": 92.0, # High passive stability
            "maintenance": 95.0,
            "cost": 95.0, # Low cost
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Ensure the wing uses a high dihedral angle to provide natural roll stability.",
            "Make all control surface linkages external for easy inspections and adjustments.",
            "Use rubber-band wing mounting for crash load relief.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        return (
            "A High-Wing Tractor layout is the gold standard for pilot training and educational platforms. "
            "It offers the highest passive stability, is simple to repair, and has low construction and material cost. "
            "Tricycle gear is selected for straightforward runway steering and nose protection during landings."
        )


class BalancedConfigurationStrategy(BaseConfigurationStrategy):
    """Default balanced strategy for general or multi-role missions."""

    @property
    def name(self) -> str:
        return "Balanced"

    def select_best_layout(self, requirements: ConfigurationRequirements) -> Dict[str, str]:
        wing = requirements.preferred_wing_position or WingPosition.HIGH_WING
        prop = requirements.preferred_propulsion_layout or PropulsionLayout.TRACTOR
        tail = requirements.preferred_tail_configuration or TailConfiguration.CONVENTIONAL
        gear = requirements.preferred_landing_gear or LandingGearConfiguration.TRICYCLE
        
        return {
            "wing_position": wing.value if hasattr(wing, 'value') else wing,
            "propulsion_layout": prop.value if hasattr(prop, 'value') else prop,
            "tail_configuration": tail.value if hasattr(tail, 'value') else tail,
            "landing_gear_configuration": gear.value if hasattr(gear, 'value') else gear,
            "engine_count": "1",
            "payload_arrangement": "CG Fuselage Bay",
            "architecture": "High-Wing Tractor Conventional Monoplane",
        }

    def evaluate_layout_suitability(
        self, requirements: ConfigurationRequirements, layout: Dict[str, str]
    ) -> Dict[str, float]:
        return {
            "suitability": 85.0,
            "simplicity": 85.0,
            "manufacturability": 85.0,
            "aerodynamics": 75.0,
            "stability": 85.0,
            "maintenance": 85.0,
            "cost": 85.0,
        }

    def get_recommendations(self, requirements: ConfigurationRequirements) -> List[str]:
        return [
            "Adopt standard wing dihedral (1 to 3 degrees) for balanced roll authority.",
            "Provide ample room in the center fuselage for battery or payload placement adjustments.",
        ]

    def get_engineering_rationale(self, requirements: ConfigurationRequirements, layout: Dict[str, str]) -> str:
        return (
            "A High-Wing Conventional layout with Tractor propulsion is selected as the default balanced configuration. "
            "It provides high roll stability, straightforward yaw/pitch control, and is mechanically robust and inexpensive."
        )
