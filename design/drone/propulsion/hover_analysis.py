"""
HoverAnalysis Subsystem

Purpose:
    Defines the `HoverAnalysis` class and `HoverAnalysisResult` dataclass for multirotor hover performance calculations.

Role in Architecture:
    `HoverAnalysis` calculates hover throttle percentage, hover efficiency (g/W), disk loading (kg/m^2),
    and power loading (g/W).
"""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HoverAnalysisResult:
    """
    Multirotor hover analysis output model.

    Attributes:
        hover_throttle_percent (float): Estimated hover throttle percentage (ideal range: 40-50%).
        hover_efficiency_g_per_w (float): Hover power loading efficiency in grams/Watt (e.g. 7.5 - 10.0 g/W).
        disk_loading_kg_m2 (float): Total rotor disk loading in kg/m^2.
        power_loading_g_per_w (float): Hover power loading ratio in grams/Watt.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    hover_throttle_percent: float
    hover_efficiency_g_per_w: float
    disk_loading_kg_m2: float
    power_loading_g_per_w: float
    metadata: dict[str, Any] = field(default_factory=dict)


class HoverAnalysis:
    """
    Analysis service for multirotor hover physics.

    Design Principles:
        - Single Responsibility Principle: Hover throttle, disk loading, and power loading physics only.
    """

    def analyze_hover(
        self,
        auw_kg: float,
        hover_thrust_per_motor_g: float,
        max_thrust_per_motor_g: float,
        propeller_diameter_inch: float,
        rotor_count: int
    ) -> HoverAnalysisResult:
        """
        Calculates hover throttle percentage, disk loading, and power loading.

        Args:
            auw_kg (float): AUW mass in kg.
            hover_thrust_per_motor_g (float): Hover thrust per motor in grams.
            max_thrust_per_motor_g (float): Max thrust per motor in grams.
            propeller_diameter_inch (float): Propeller diameter in inches.
            rotor_count (int): Total rotor count.

        Returns:
            HoverAnalysisResult: Computed hover analysis output.
        """
        throttle = (hover_thrust_per_motor_g / max_thrust_per_motor_g) * 100.0 if max_thrust_per_motor_g > 0 else 50.0

        # Calculate total propeller disk area in m^2
        radius_m = (propeller_diameter_inch * 0.0254) / 2.0
        single_area_m2 = math.pi * (radius_m ** 2)
        total_disk_area_m2 = single_area_m2 * rotor_count

        disk_loading = auw_kg / total_disk_area_m2 if total_disk_area_m2 > 0 else 10.0

        # Power loading heuristic based on disk loading: lower disk loading -> higher power loading
        power_loading = 11.5 - (disk_loading * 0.25)
        power_loading = max(4.0, min(14.0, power_loading))

        return HoverAnalysisResult(
            hover_throttle_percent=round(throttle, 1),
            hover_efficiency_g_per_w=round(power_loading, 2),
            disk_loading_kg_m2=round(disk_loading, 2),
            power_loading_g_per_w=round(power_loading, 2)
        )
