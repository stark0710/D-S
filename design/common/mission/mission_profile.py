"""
MissionProfile Subsystem

Purpose:
    Defines the `MissionProfile` domain model representing the canonical engineering interpretation of user requirements.

Role in Architecture:
    `MissionProfile` is constructed by the Mission Analysis Platform to provide structured physics inputs and
    engineering constraints to the Vehicle Recommendation Engine and category-specific design studios.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.mission.mission_complexity import MissionComplexity
from backend.design.common.mission.mission_constraints import MissionConstraints


@dataclass(slots=True)
class MissionProfile:
    """
    Canonical engineering interpretation of an aircraft design mission.

    Attributes:
        mission_type (MissionType): Operational mission category.
        mission_summary (str): Engineering summary of mission objectives and constraints.
        payload_requirement (float): Payload mass requirement in kilograms.
        range_requirement (float): Range requirement in kilometers.
        flight_time_requirement (float): Endurance requirement in minutes.
        cruise_speed_requirement (float): Desired cruise speed in km/h.
        takeoff_requirement (TakeoffType): Required takeoff operational mode.
        landing_requirement (LandingType): Required landing operational mode.
        environment (OperatingEnvironment): Target operating environment.
        optimization_priority (OptimizationPriority): Priority target for design optimization.
        mission_complexity (MissionComplexity): Assessed deterministic complexity level.
        constraints (MissionConstraints): Consolidated physics and budget constraints.
        metadata (dict[str, Any]): Additional operational analysis metadata.
    """

    mission_type: MissionType
    mission_summary: str
    payload_requirement: float
    range_requirement: float
    flight_time_requirement: float
    cruise_speed_requirement: float
    takeoff_requirement: TakeoffType
    landing_requirement: LandingType
    environment: OperatingEnvironment
    optimization_priority: OptimizationPriority
    mission_complexity: MissionComplexity
    constraints: MissionConstraints
    metadata: dict[str, Any] = field(default_factory=dict)
