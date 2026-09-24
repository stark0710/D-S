"""
Fixed-Wing Mission Constraints Subsystem

Purpose:
    Defines the `MissionConstraints` domain model representing the parsed, normalized operational constraints.

Role in Architecture:
    `MissionConstraints` is a key component of the `MissionResult`. It represents the hard limits,
    minimum bounds, and design targets derived from raw requirements.
"""

from dataclasses import dataclass
from backend.design.fixed_wing.mission.mission_requirements import (
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)


@dataclass(slots=True)
class MissionConstraints:
    """
    Consolidated operational and physical constraints for fixed-wing aircraft design.

    Attributes:
        minimum_payload_kg (float): Mandatory minimum payload mass capacity in kilograms.
        minimum_range_km (float): Mandatory minimum range in kilometers.
        minimum_endurance_min (float): Mandatory minimum endurance/flight time in minutes.
        target_cruise_speed_kmh (float): Target cruise speed in km/h.
        maximum_stall_speed_kmh (float | None): Maximum allowable stall speed in km/h.
        maximum_takeoff_weight_kg (float | None): Optional upper limit on MTOW in kilograms.
        budget_limit (float | None): Optional upper limit on financial budget.
        required_launch_method (LaunchMethod): Required launch method.
        required_landing_method (LandingMethod): Required landing method.
        operating_environment (EnvironmentType): Operating environment.
        required_autonomy_level (AutonomyLevel): Minimum operational autonomy level.
    """

    minimum_payload_kg: float
    minimum_range_km: float
    minimum_endurance_min: float
    target_cruise_speed_kmh: float
    maximum_stall_speed_kmh: float | None
    maximum_takeoff_weight_kg: float | None
    budget_limit: float | None
    required_launch_method: LaunchMethod
    required_landing_method: LandingMethod
    operating_environment: EnvironmentType
    required_autonomy_level: AutonomyLevel
