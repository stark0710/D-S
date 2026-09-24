"""
Fixed-Wing Mission Requirements Subsystem

Purpose:
    Defines the `MissionRequirements` domain model, which captures and stores raw user-specified mission constraints and inputs.

Role in Architecture:
    `MissionRequirements` is the initial input payload for the Fixed-Wing Mission Engineering Framework.
    It contains raw data attributes without execution or validation logic, conforming to Clean Architecture boundaries.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from backend.design.common.requirements.optimization_priority import OptimizationPriority


class MissionCategory(str, Enum):
    """Supported mission categories for fixed-wing UAVs."""
    SURVEY = "Survey"
    MAPPING = "Mapping"
    LONG_ENDURANCE = "Long Endurance"
    CARGO = "Cargo"
    AGRICULTURE = "Agriculture"
    RESEARCH = "Research"
    SURVEILLANCE = "Surveillance"
    TRAINING = "Training"
    RACING = "Racing"
    CUSTOM = "Custom"


class LaunchMethod(str, Enum):
    """Launch methods for fixed-wing UAVs."""
    HAND_LAUNCH = "Hand Launch"
    CATAPULT = "Catapult"
    RUNWAY = "Runway"
    BUNGEE = "Bungee"
    CUSTOM = "Custom"


class LandingMethod(str, Enum):
    """Landing and recovery methods for fixed-wing UAVs."""
    BELLY_LANDING = "Belly Landing"
    PARACHUTE = "Parachute"
    NET_RECOVERY = "Net Recovery"
    DEEP_STALL = "Deep Stall"
    RUNWAY = "Runway"
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
    """Levels of operational autonomy."""
    MANUAL = "Manual"
    ASSISTED = "Assisted"
    SEMI_AUTONOMOUS = "Semi-Autonomous"
    FULLY_AUTONOMOUS = "Fully Autonomous"


@dataclass(slots=True)
class MissionRequirements:
    """
    Domain model representing the raw user-specified mission requirements.

    Attributes:
        mission_category (MissionCategory): General class of the mission.
        payload_kg (float): Required payload weight capacity in kilograms.
        flight_time_min (float): Target flight time (endurance) in minutes.
        cruise_speed_kmh (float): Desired cruise speed in km/h.
        stall_speed_target_kmh (float | None): Optional target stall speed constraint in km/h.
        maximum_takeoff_weight_limit_kg (float | None): Optional limit on MTOW in kilograms.
        operational_altitude_m (float): Target operational altitude above sea level in meters.
        mission_range_km (float): Required operational range in kilometers.
        launch_method (LaunchMethod): Method used to launch the aircraft.
        landing_method (LandingMethod): Method used to recover the aircraft.
        budget (float | None): Optional financial budget constraint.
        environment (EnvironmentType): The primary operating environment.
        autonomy_level (AutonomyLevel): Expected level of drone autonomy.
        metadata (dict[str, Any]): Additional unstructured parameters or settings.
    """

    mission_category: MissionCategory
    payload_kg: float
    flight_time_min: float
    cruise_speed_kmh: float
    stall_speed_target_kmh: float | None
    maximum_takeoff_weight_limit_kg: float | None
    operational_altitude_m: float
    mission_range_km: float
    launch_method: LaunchMethod
    landing_method: LandingMethod
    budget: float | None
    environment: EnvironmentType
    autonomy_level: AutonomyLevel
    optimization_priority: OptimizationPriority = OptimizationPriority.BALANCED
    metadata: dict[str, Any] = field(default_factory=dict)
