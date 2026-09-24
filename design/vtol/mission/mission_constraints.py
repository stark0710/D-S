"""
VTOL Mission Constraints Subsystem

Purpose:
    Defines the `MissionConstraints` class which consolidates operational physical limits.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from backend.design.vtol.mission.mission_requirements import VTOLType, TakeoffMethod, LandingMethod


@dataclass(slots=True)
class MissionConstraints:
    """
    Physical and economic limits derived for the VTOL sizing loop.

    Attributes:
        minimum_payload_kg (float): Minimum payload weight capacity.
        minimum_range_km (float): Minimum cruise range.
        minimum_endurance_min (float): Minimum cumulative flight time.
        required_vtol_type (VTOLType): VTOL mechanical architecture.
        required_takeoff_method (TakeoffMethod): Takeoff method.
        required_landing_method (LandingMethod): Recovery method.
        max_wind_limit_kts (float): Limit of safe operations.
        temperature_bounds_c (Tuple[float, float]): Minimum and maximum ambient temperatures.
        budget_limit (float | None): Limit on production/operational budget.
        metadata (Dict[str, Any]): Additional operational limits.
    """

    minimum_payload_kg: float
    minimum_range_km: float
    minimum_endurance_min: float
    required_vtol_type: VTOLType
    required_takeoff_method: TakeoffMethod
    required_landing_method: LandingMethod
    max_wind_limit_kts: float
    temperature_bounds_c: Tuple[float, float]
    budget_limit: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
