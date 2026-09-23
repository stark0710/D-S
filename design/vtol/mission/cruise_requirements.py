"""
VTOL Mission Cruise Requirements Subsystem

Purpose:
    Defines the `CruiseRequirements` dataclass capturing parameters specific to the cruise phase.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class CruiseRequirements:
    """
    Requirements specific to the VTOL forward flight (cruise) regime.

    Attributes:
        cruise_speed_kmh (float): Airspeed in forward flight in km/h.
        cruise_altitude_m (float): Operational altitude during cruise in meters above sea level.
        cruise_range_km (float): Target cruise range in kilometers.
        cruise_endurance_min (float): Target cruise flight duration in minutes.
        wind_limit_cruise_kts (float): Maximum wind speed for safe cruise operations in knots.
        metadata (Dict[str, Any]): Additional unstructured parameters or settings.
    """

    cruise_speed_kmh: float
    cruise_altitude_m: float
    cruise_range_km: float
    cruise_endurance_min: float
    wind_limit_cruise_kts: float
    metadata: Dict[str, Any] = field(default_factory=dict)
