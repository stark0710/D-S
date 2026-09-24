"""
RangeAnalysis Subsystem

Purpose:
    Defines the `RangeAnalysis` class for flight range distance calculations.

Role in Architecture:
    `RangeAnalysis` calculates maximum flight range distance in km based on cruise speed and mission endurance.
"""


class RangeAnalysis:
    """
    Analysis service for multirotor flight range.

    Design Principles:
        - Single Responsibility Principle: Operational range distance estimation only.
    """

    def calculate_range(
        self,
        mission_endurance_min: float,
        cruise_speed_kmh: float,
        reserve_margin_percent: float = 20.0
    ) -> float:
        """
        Calculates maximum operational flight range in km with energy reserves.

        Args:
            mission_endurance_min (float): Mission endurance in minutes.
            cruise_speed_kmh (float): Cruise speed in km/h.
            reserve_margin_percent (float): Reserve margin percentage (default 20%).

        Returns:
            float: Maximum flight range in km.
        """
        available_time_min = mission_endurance_min * (1.0 - (reserve_margin_percent / 100.0))
        available_hours = available_time_min / 60.0

        range_km = available_hours * cruise_speed_kmh
        return round(max(0.0, range_km), 1)
