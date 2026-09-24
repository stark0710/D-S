"""
PerformanceProfile Subsystem

Purpose:
    Defines the `PerformanceProfile` domain model representing multirotor flight performance parameters.

Role in Architecture:
    `PerformanceProfile` encapsulates maximum flight time in min, maximum range in km, cruise speed in kmh,
    max speed in kmh, max climb rate in m/s, and max wind speed tolerance in m/s.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PerformanceProfile:
    """
    Multirotor flight performance specification profile.

    Attributes:
        max_flight_time_min (float): Maximum flight time in minutes.
        max_range_km (float): Maximum flight range in km.
        cruise_speed_kmh (float): Optimal cruise speed in km/h.
        max_speed_kmh (float): Maximum horizontal speed in km/h.
        max_climb_rate_m_s (float): Maximum vertical climb rate in m/s.
        max_wind_speed_m_s (float): Maximum wind speed tolerance in m/s.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    max_flight_time_min: float
    max_range_km: float
    cruise_speed_kmh: float
    max_speed_kmh: float
    max_climb_rate_m_s: float
    max_wind_speed_m_s: float
    metadata: dict[str, Any] = field(default_factory=dict)
