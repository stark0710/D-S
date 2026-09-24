"""
MissionConstraints Subsystem

Purpose:
    Defines the `MissionConstraints` domain model representing explicit operational and physical constraints.

Role in Architecture:
    `MissionConstraints` consolidates minimum performance bounds (payload, range, endurance), operational limits,
    and financial/weight budget boundaries derived from user requirements.
"""

from dataclasses import dataclass
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment


@dataclass(slots=True)
class MissionConstraints:
    """
    Consolidated operational and physical constraints.

    Attributes:
        minimum_payload_kg (float): Mandatory minimum payload mass capacity in kilograms.
        minimum_range_km (float): Mandatory minimum operational range in kilometers.
        minimum_endurance_min (float): Mandatory minimum endurance in minutes.
        required_takeoff_type (TakeoffType): Required takeoff operational mode.
        required_landing_type (LandingType): Required landing operational mode.
        operating_environment (OperatingEnvironment): Required operational terrain/environment.
        budget_limit (float | None): Optional upper limit on financial budget.
        weight_limit (float | None): Optional upper limit on maximum takeoff weight (MTOW) in kilograms.
    """

    minimum_payload_kg: float
    minimum_range_km: float
    minimum_endurance_min: float
    required_takeoff_type: TakeoffType
    required_landing_type: LandingType
    operating_environment: OperatingEnvironment
    budget_limit: float | None = None
    weight_limit: float | None = None
