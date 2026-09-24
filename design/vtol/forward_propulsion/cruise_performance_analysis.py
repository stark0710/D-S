"""
VTOL Cruise Performance Analysis Subsystem

Purpose:
    Defines the `CruisePerformanceAnalysis` class estimating rate of climb and speed boundaries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class CruisePerformanceAnalysis:
    """
    Flight envelope limits during forward wing-borne stages.

    Attributes:
        max_speed_kmh (float): Estimated terminal level-flight airspeed limit.
        rate_of_climb_m_s (float): Peak continuous rate of climb at climb power.
        climb_angle_deg (float): Sized climb gradient angle.
        propulsive_efficiency (float): propeller mechanical efficiency index.
        cruise_range_margin_km (float): Range capability margin.
        metadata (Dict[str, Any]): Aerodynamic lift/drag splits.
    """

    max_speed_kmh: float
    rate_of_climb_m_s: float
    climb_angle_deg: float
    propulsive_efficiency: float
    cruise_range_margin_km: float
    metadata: Dict[str, Any] = field(default_factory=dict)
