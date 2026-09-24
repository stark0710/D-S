"""
PowerAnalysis Subsystem

Purpose:
    Defines the `PowerAnalysis` class and `PowerAnalysisResult` dataclass for multirotor power and electrical current draw calculations.

Role in Architecture:
    `PowerAnalysis` calculates total hover power in Watts, peak maximum power in Watts, hover current in Amperes,
    and peak current in Amperes based on battery operating voltage.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PowerAnalysisResult:
    """
    Multirotor electrical power analysis output model.

    Attributes:
        hover_power_w (float): Total electrical power draw in Watts during hover.
        max_power_w (float): Peak total electrical power draw in Watts at 100% throttle.
        hover_current_a (float): Total current draw in Amperes during hover.
        max_current_a (float): Peak total current draw in Amperes at 100% throttle.
        operating_voltage_v (float): Nominal DC battery voltage in Volts (e.g. 22.2V for 6S LiPo).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    hover_power_w: float
    max_power_w: float
    hover_current_a: float
    max_current_a: float
    operating_voltage_v: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PowerAnalysis:
    """
    Analysis service for multirotor electrical power calculations.

    Design Principles:
        - Single Responsibility Principle: Electrical power and current draw calculations only.
    """

    def analyze_power(
        self,
        hover_thrust_per_motor_g: float,
        max_thrust_per_motor_g: float,
        rotor_count: int,
        operating_voltage_v: float = 22.2,
        hover_efficiency_g_w: float = 8.5
    ) -> PowerAnalysisResult:
        """
        Calculates electrical power and current requirements.

        Args:
            hover_thrust_per_motor_g (float): Hover thrust per motor in grams.
            max_thrust_per_motor_g (float): Max thrust per motor in grams.
            rotor_count (int): Total rotor count.
            operating_voltage_v (float): Battery voltage in Volts.
            hover_efficiency_g_w (float): Hover efficiency in grams per Watt.

        Returns:
            PowerAnalysisResult: Computed power analysis results.
        """
        hover_power_total_w = (hover_thrust_per_motor_g * rotor_count) / hover_efficiency_g_w
        hover_current_total_a = hover_power_total_w / operating_voltage_v

        # At max throttle, efficiency drops to ~3.5-4.5 g/W
        max_power_total_w = (max_thrust_per_motor_g * rotor_count) / 4.0
        max_current_total_a = max_power_total_w / operating_voltage_v

        return PowerAnalysisResult(
            hover_power_w=round(hover_power_total_w, 1),
            max_power_w=round(max_power_total_w, 1),
            hover_current_a=round(hover_current_total_a, 1),
            max_current_a=round(max_current_total_a, 1),
            operating_voltage_v=operating_voltage_v
        )
