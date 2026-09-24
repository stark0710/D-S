"""
RequirementModel Subsystem

Purpose:
    Defines the `RequirementModel` domain model representing user-specified design requirements.

Role in Architecture:
    `RequirementModel` is the canonical domain object carrying user design intent prior to requirement validation,
    mission physics analysis, vehicle category recommendation, and specialized design studio sizing.
    It contains raw data attributes without business logic, validation methods, or engineering calculations.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode


@dataclass(slots=True)
class RequirementModel:
    """
    Canonical domain model encapsulating user-specified aircraft design requirements.

    Attributes:
        mission_type (MissionType): Operational mission classification (e.g. SURVEY, DELIVERY, AGRICULTURE).
        payload_weight_kg (float): Required payload mass in kilograms.
        target_flight_time_min (float): Target endurance/flight time in minutes.
        target_range_km (float): Target operational range in kilometers.
        cruise_speed_kmh (float): Desired cruise flight speed in km/h.
        aircraft_type (AircraftType | None): Selected aircraft configuration category. Optional in ENGINEERING_ADVISOR mode.
        maximum_takeoff_weight_kg (float | None): Optional upper limit constraint on MTOW in kilograms.
        budget (float | None): Optional target financial budget limit.
        takeoff_type (TakeoffType): Preferred takeoff operational mode (default VERTICAL).
        landing_type (LandingType): Preferred landing operational mode (default VERTICAL).
        environment (OperatingEnvironment): Target flight terrain/environment (default RURAL).
        optimization_priority (OptimizationPriority): Design optimization target priority (default BALANCED).
        design_mode (DesignMode): Execution design workflow mode (default ENGINEERING_ADVISOR).
        metadata (dict[str, Any]): Additional operational or custom user metadata.

    Design Principles:
        - Pure Domain Model: Stores state only; contains no validation or sizing logic.
        - Immutable Attribute Access: Memory optimized via `@dataclass(slots=True)`.
    """

    mission_type: MissionType
    payload_weight_kg: float
    target_flight_time_min: float
    target_range_km: float
    cruise_speed_kmh: float
    aircraft_type: AircraftType | None = None
    maximum_takeoff_weight_kg: float | None = None
    budget: float | None = None
    takeoff_type: TakeoffType = TakeoffType.VERTICAL
    landing_type: LandingType = LandingType.VERTICAL
    environment: OperatingEnvironment = OperatingEnvironment.RURAL
    optimization_priority: OptimizationPriority = OptimizationPriority.BALANCED
    design_mode: DesignMode = DesignMode.ENGINEERING_ADVISOR
    metadata: dict[str, Any] = field(default_factory=dict)
