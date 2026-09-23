"""
Fixed-Wing Flight Performance Specification Model
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(slots=True)
class FlightPerformanceSpecification:
    """
    Standardized specification containing the predicted aircraft flight performance envelope,
    takeoff/landing rolls, climb rate, range, endurance, power margins, and mission completion probability.
    """
    stall_speed_kmh: float
    cruise_speed_kmh: float
    maximum_speed_kmh: float
    takeoff_distance_m: float
    landing_distance_m: float
    rate_of_climb_m_s: float
    range_km: float
    endurance_min: float
    power_required_w: float
    power_available_w: float
    energy_consumption_wh_km: float
    mission_margin_pct: float
    performance_score: float
    reasoning: str
