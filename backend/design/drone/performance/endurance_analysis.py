"""
EnduranceAnalysis Subsystem

Purpose:
    Defines the `EnduranceAnalysis` class for hover and mission flight time endurance calculations.

Role in Architecture:
    `EnduranceAnalysis` calculates maximum hover flight time in minutes and realistic mission profile flight time in minutes.
"""


class EnduranceAnalysis:
    """
    Analysis service for multirotor flight endurance.

    Design Principles:
        - Single Responsibility Principle: Hover time and mission profile endurance calculation only.
    """

    def calculate_endurance(
        self,
        usable_energy_wh: float,
        hover_power_w: float,
        cruise_power_w: float,
        hover_fraction: float = 0.30
    ) -> dict[str, float]:
        """
        Calculates max hover time and mission profile flight time.

        Args:
            usable_energy_wh (float): Usable battery energy in Wh.
            hover_power_w (float): Hover power consumption in Watts.
            cruise_power_w (float): Cruise power consumption in Watts.
            hover_fraction (float): Fraction of mission spent hovering (0.0 to 1.0).

        Returns:
            dict[str, float]: Flight endurance dictionary in minutes.
        """
        max_hover_min = (usable_energy_wh / hover_power_w * 60.0) if hover_power_w > 0 else 0.0

        avg_mission_power_w = (hover_power_w * hover_fraction) + (cruise_power_w * (1.0 - hover_fraction))
        mission_endurance_min = (usable_energy_wh / avg_mission_power_w * 60.0) if avg_mission_power_w > 0 else 0.0

        return {
            "max_hover_time_min": round(max_hover_min, 1),
            "mission_endurance_min": round(mission_endurance_min, 1),
        }
