"""
VTOL Mission Requirements Subsystem

Purpose:
    Defines the `MissionRequirements` class and its associated enums,
    capturing all user inputs for a VTOL design.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from backend.design.vtol.mission.hover_requirements import HoverRequirements
from backend.design.vtol.mission.transition_requirements import TransitionRequirements
from backend.design.vtol.mission.cruise_requirements import CruiseRequirements


class VTOLMissionCategory(str, Enum):
    """Supported mission categories for VTOL aircraft."""
    CARGO = "Cargo"
    SURVEY = "Survey"
    MAPPING = "Mapping"
    INSPECTION = "Inspection"
    AGRICULTURE = "Agriculture"
    LONG_ENDURANCE = "Long Endurance"
    MILITARY = "Military"
    RESEARCH = "Research"
    DELIVERY = "Delivery"
    EMERGENCY_RESPONSE = "Emergency Response"
    SEARCH_AND_RESCUE = "Search and Rescue"
    CUSTOM = "Custom"


class VTOLType(str, Enum):
    """Supported configurations for VTOL aircraft."""
    QUADPLANE = "QuadPlane"
    TILT_ROTOR = "Tilt Rotor"
    TILT_WING = "Tilt Wing"
    TAIL_SITTER = "Tail Sitter"
    LIFT_CRUISE = "Lift + Cruise"
    VECTORED_THRUST = "Vectored Thrust"
    HYBRID_VTOL = "Hybrid VTOL"
    TWIN_BOOM_VTOL = "Twin Boom VTOL"
    BOX_WING_VTOL = "Box Wing VTOL"
    CUSTOM = "Custom"


class TakeoffMethod(str, Enum):
    """VTOL takeoff methods."""
    VERTICAL = "Vertical"
    RUNWAY = "Runway"
    CATAPULT = "Catapult"
    HAND_LAUNCH = "Hand Launch"
    CUSTOM = "Custom"


class LandingMethod(str, Enum):
    """VTOL landing methods."""
    VERTICAL = "Vertical"
    RUNWAY = "Runway"
    BELLY_LANDING = "Belly Landing"
    PARACHUTE = "Parachute"
    CUSTOM = "Custom"


class EnvironmentType(str, Enum):
    """Operating environment types."""
    RURAL = "Rural"
    URBAN = "Urban"
    FOREST = "Forest"
    MOUNTAIN = "Mountain"
    DESERT = "Desert"
    MARINE = "Marine"


class AutonomyLevel(str, Enum):
    """Operational autonomy levels."""
    MANUAL = "Manual"
    ASSISTED = "Assisted"
    SEMI_AUTONOMOUS = "Semi-Autonomous"
    FULLY_AUTONOMOUS = "Fully Autonomous"


@dataclass(slots=True)
class MissionRequirements:
    """
    Consolidated VTOL mission requirements.

    Attributes:
        mission_category (VTOLMissionCategory): Class of the mission.
        vtol_type (VTOLType): Preferred mechanical VTOL layout.
        payload_kg (float): Required payload capacity in kilograms.
        hover_reqs (HoverRequirements): Sizing inputs for hover regime.
        transition_reqs (TransitionRequirements): Sizing inputs for transition regime.
        cruise_reqs (CruiseRequirements): Sizing inputs for cruise regime.
        max_altitude_m (float): Maximum ceiling required above MSL in meters.
        environment (EnvironmentType): Operating environment terrain/location.
        takeoff_method (TakeoffMethod): Takeoff method.
        landing_method (LandingMethod): Landing method.
        wind_limit_max_kts (float): Safe operational wind limit in knots.
        temperature_limit_min_c (float): Minimum temperature limit in Celsius.
        temperature_limit_max_c (float): Maximum temperature limit in Celsius.
        rain_tolerance (str): Rain tolerance description (e.g. None, Light, Heavy).
        autonomy_level (AutonomyLevel): Expected level of drone autonomy.
        safety_requirements (str): Safety features/standards description.
        budget (float | None): Optional financial budget constraint.
        manufacturing_preference (str): Preference for construction (e.g. Composite, Balsa).
        metadata (Dict[str, Any]): Additional unstructured parameters or settings.
    """

    mission_category: VTOLMissionCategory
    vtol_type: VTOLType
    payload_kg: float
    hover_reqs: HoverRequirements
    transition_reqs: TransitionRequirements
    cruise_reqs: CruiseRequirements
    max_altitude_m: float
    environment: EnvironmentType
    takeoff_method: TakeoffMethod
    landing_method: LandingMethod
    wind_limit_max_kts: float
    temperature_limit_min_c: float
    temperature_limit_max_c: float
    rain_tolerance: str
    autonomy_level: AutonomyLevel
    safety_requirements: str
    budget: float | None = None
    manufacturing_preference: str = "Composite"
    metadata: Dict[str, Any] = field(default_factory=dict)
