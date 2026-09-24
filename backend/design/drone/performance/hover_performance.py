"""
HoverPerformance Subsystem

Purpose:
    Defines the `HoverPerformance` class and `HoverPerformanceResult` dataclass for hover aerodynamic and power evaluation.

Role in Architecture:
    `HoverPerformance` calculates hover power in Watts, hover thrust margin, disk loading in kg/m^2,
    power loading in g/W, and hover throttle percentage.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HoverPerformanceResult:
    """
    Multirotor hover performance evaluation output model.

    Attributes:
        hover_power_w (float): Hover power consumption in Watts.
        hover_thrust_margin (float): Available thrust margin during hover (Max Thrust / AUW).
        disk_loading_kg_m2 (float): Total rotor disk loading in kg/m^2.
        power_loading_g_w (float): Hover efficiency power loading in grams/Watt.
        hover_throttle_percent (float): Hover throttle percentage.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    hover_power_w: float
    hover_thrust_margin: float
    disk_loading_kg_m2: float
    power_loading_g_w: float
    hover_throttle_percent: float
    metadata: dict[str, Any] = field(default_factory=dict)


class HoverPerformance:
    """
    Analysis service for hover flight performance.

    Design Principles:
        - Single Responsibility Principle: Hover aerodynamic power, disk loading, and efficiency analysis only.
    """

    def analyze_hover(
        self,
        total_mass_kg: float,
        rotor_count: int,
        propeller_diameter_inch: float,
        hover_power_w: float,
        actual_tw_ratio: float,
        hover_throttle_percent: float
    ) -> HoverPerformanceResult:
        """
        Evaluates hover performance parameters.

        Args:
            total_mass_kg (float): Aircraft AUW mass in kg.
            rotor_count (int): Total rotor count.
            propeller_diameter_inch (float): Propeller diameter in inches.
            hover_power_w (float): Total hover power in Watts.
            actual_tw_ratio (float): Available thrust-to-weight ratio.
            hover_throttle_percent (float): Hover throttle percentage.

        Returns:
            HoverPerformanceResult: Computed hover performance output.
        """
        # Disk area calculation
        r_m = (propeller_diameter_inch * 0.0254) / 2.0
        total_area = 3.14159 * (r_m ** 2) * rotor_count
        disk_loading = total_mass_kg / total_area if total_area > 0 else 10.0

        # Power loading g/W = (Mass in g) / (Power in W)
        power_loading = (total_mass_kg * 1000.0) / hover_power_w if hover_power_w > 0 else 8.0

        return HoverPerformanceResult(
            hover_power_w=round(hover_power_w, 1),
            hover_thrust_margin=round(actual_tw_ratio, 2),
            disk_loading_kg_m2=round(disk_loading, 2),
            power_loading_g_w=round(power_loading, 2),
            hover_throttle_percent=round(hover_throttle_percent, 1)
        )
