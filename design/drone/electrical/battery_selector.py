"""
BatterySelector Subsystem

Purpose:
    Defines the `BatterySelector` class responsible for sizing and selecting battery engineering specifications.

Role in Architecture:
    `BatterySelector` calculates required cell count S, capacity in mAh, discharge C-rating, battery pack weight,
    and chemistry ('LiPo', 'LiHV', 'Li-Ion').
"""

from typing import Any


class BatterySelector:
    """
    Selection service for multirotor battery pack engineering specifications.

    Design Principles:
        - Single Responsibility Principle: Battery chemistry, S-count, capacity mAh, C-rating, and pack mass sizing only.
    """

    def select_battery(
        self,
        voltage_v: float,
        target_endurance_min: float,
        hover_power_w: float,
        chemistry: str = "LiPo"
    ) -> dict[str, Any]:
        """
        Determines optimal battery specifications.

        Args:
            voltage_v (float): Desired operating voltage in Volts.
            target_endurance_min (float): Target flight time in minutes.
            hover_power_w (float): Hover power consumption in Watts.
            chemistry (str): Battery chemistry ('LiPo', 'LiHV', 'Li-Ion').

        Returns:
            dict[str, Any]: Selected battery specifications dictionary.
        """
        if chemistry == "LiHV":
            cell_nom = 3.8
            wh_per_kg = 185.0
        elif chemistry == "Li-Ion":
            cell_nom = 3.6
            wh_per_kg = 240.0
        else:  # LiPo
            cell_nom = 3.7
            wh_per_kg = 160.0

        cell_count_s = int(round(voltage_v / cell_nom))
        cell_count_s = max(3, min(14, cell_count_s))
        nominal_v = cell_count_s * cell_nom

        # Energy required in Wh = (power_w * (time_min / 60)) / 0.80 (80% DOD limit)
        req_wh = (hover_power_w * (target_endurance_min / 60.0)) / 0.80
        capacity_ah = req_wh / nominal_v if nominal_v > 0 else 5.0
        capacity_mah = round(capacity_ah * 1000.0, -2)  # Round to nearest 100 mAh

        pack_weight_g = round((req_wh / (wh_per_kg / 1000.0)), 1)

        # Standard C-rating recommendation
        discharge_c = 45.0 if chemistry == "LiPo" else 20.0

        return {
            "battery_model": f"{chemistry} {cell_count_s}S {capacity_mah:.0f}mAh {discharge_c:.0f}C Pack",
            "chemistry": chemistry,
            "cell_count_s": cell_count_s,
            "nominal_voltage_v": round(nominal_v, 2),
            "capacity_mah": capacity_mah,
            "discharge_rating_c": discharge_c,
            "total_energy_wh": round((capacity_mah / 1000.0) * nominal_v, 1),
            "estimated_battery_weight_g": pack_weight_g,
        }
