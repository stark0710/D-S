"""
PerformanceRequirements Subsystem

Purpose:
    Defines the `PerformanceRequirements` domain model representing input requirements for flight performance engineering.

Role in Architecture:
    `PerformanceRequirements` specifies required flight time in min, required range in km, required cruise speed in kmh,
    and max operating wind speed in m/s.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PerformanceRequirements:
    """
    Multirotor flight performance engineering requirements model.

    Attributes:
        required_flight_time_min (float): Required mission flight time in minutes.
        required_range_km (float): Required operational range in km.
        required_cruise_speed_kmh (float): Required cruise speed in km/h.
        max_wind_speed_m_s (float): Maximum operating wind speed in m/s.
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    required_flight_time_min: float = 20.0
    required_range_km: float = 10.0
    required_cruise_speed_kmh: float = 40.0
    max_wind_speed_m_s: float = 10.0
    metadata: dict[str, Any] = field(default_factory=dict)
