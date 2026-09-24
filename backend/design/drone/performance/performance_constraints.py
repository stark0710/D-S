"""
PerformanceConstraints Subsystem

Purpose:
    Defines the `PerformanceConstraints` domain model representing flight performance design constraints.

Role in Architecture:
    `PerformanceConstraints` specifies minimum flight time in min, minimum thrust margin, minimum energy reserve %,
    and maximum safe descent rate in m/s.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PerformanceConstraints:
    """
    Multirotor flight performance engineering design constraints.

    Attributes:
        min_flight_time_min (float): Lower allowable limit on flight time in minutes.
        min_thrust_margin (float): Minimum thrust-to-weight ratio limit (default 1.5).
        min_energy_reserve_percent (float): Minimum energy reserve percentage (default 15%).
        max_vortex_ring_descent_rate_m_s (float): Maximum safe descent rate in m/s (default 5.0 m/s).
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    min_flight_time_min: float = 12.0
    min_thrust_margin: float = 1.5
    min_energy_reserve_percent: float = 15.0
    max_vortex_ring_descent_rate_m_s: float = 5.0
    metadata: dict[str, Any] = field(default_factory=dict)
