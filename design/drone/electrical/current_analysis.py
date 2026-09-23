"""
CurrentAnalysis Subsystem

Purpose:
    Defines the `CurrentAnalysis` class and `CurrentAnalysisResult` dataclass for electrical current calculations.

Role in Architecture:
    `CurrentAnalysis` calculates hover current in Amperes, peak current in Amperes, per-ESC current loading,
    and battery discharge C-rate requirement.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CurrentAnalysisResult:
    """
    Multirotor current draw analysis output model.

    Attributes:
        hover_current_total_a (float): Total electrical current draw in Amperes during hover.
        peak_current_total_a (float): Total electrical current draw in Amperes at peak power.
        current_per_esc_hover_a (float): Per-ESC current draw in Amperes during hover.
        current_per_esc_peak_a (float): Per-ESC current draw in Amperes at peak power.
        required_discharge_c (float): Calculated battery discharge C-rate requirement.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    hover_current_total_a: float
    peak_current_total_a: float
    current_per_esc_hover_a: float
    current_per_esc_peak_a: float
    required_discharge_c: float
    metadata: dict[str, Any] = field(default_factory=dict)


class CurrentAnalysis:
    """
    Analysis service for multirotor electrical current draw.

    Design Principles:
        - Single Responsibility Principle: Electrical current analysis physics only.
    """

    def analyze_current(
        self,
        total_hover_power_w: float,
        total_peak_power_w: float,
        voltage_v: float,
        rotor_count: int,
        battery_capacity_mah: float
    ) -> CurrentAnalysisResult:
        """
        Calculates hover current, peak current, per-ESC current loading, and C-rate.

        Args:
            total_hover_power_w (float): Total hover power in Watts.
            total_peak_power_w (float): Total peak power in Watts.
            voltage_v (float): Operating voltage in Volts.
            rotor_count (int): Total rotor count.
            battery_capacity_mah (float): Battery capacity in mAh.

        Returns:
            CurrentAnalysisResult: Computed current analysis output.
        """
        hover_i = total_hover_power_w / voltage_v
        peak_i = total_peak_power_w / voltage_v

        esc_hover_i = hover_i / rotor_count
        esc_peak_i = peak_i / rotor_count

        # C-rate = Peak Current (A) / (Capacity (mAh) / 1000)
        battery_ah = battery_capacity_mah / 1000.0 if battery_capacity_mah > 0 else 5.0
        req_c = peak_i / battery_ah if battery_ah > 0 else 20.0

        return CurrentAnalysisResult(
            hover_current_total_a=round(hover_i, 1),
            peak_current_total_a=round(peak_i, 1),
            current_per_esc_hover_a=round(esc_hover_i, 1),
            current_per_esc_peak_a=round(esc_peak_i, 1),
            required_discharge_c=round(req_c, 1)
        )
