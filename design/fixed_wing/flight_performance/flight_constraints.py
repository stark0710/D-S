"""
Fixed-Wing Flight Sizing Constraints Subsystem

Purpose:
    Defines the `FlightConstraints` class to hold physical bounds.

Role in Architecture:
    `FlightConstraints` collects target takeoff distances, glide ratios, and range minimums.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class FlightConstraints:
    """
    Sizing bounds restricting performance predictions.

    Attributes:
        min_range_km (float): Sized min range to pass feasibility.
        min_endurance_min (float): Sized min flight time.
        max_takeoff_distance_m (float): Sized upper limit on ground roll.
        max_landing_distance_m (float): Sized upper limit on braking run.
        min_rate_of_climb_m_s (float): Minimum rate of climb.
    """

    min_range_km: float = 10.0
    min_endurance_min: float = 30.0
    max_takeoff_distance_m: float = 50.0
    max_landing_distance_m: float = 50.0
    min_rate_of_climb_m_s: float = 1.0
