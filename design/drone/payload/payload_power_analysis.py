"""
PayloadPowerAnalysis Subsystem

Purpose:
    Defines the `PayloadPowerAnalysis` class and `PayloadPowerAnalysisResult` dataclass for payload power consumption calculations.

Role in Architecture:
    `PayloadPowerAnalysis` calculates payload power draw in Watts, operating voltage, electrical current draw in Amperes,
    and payload percentage share of total system power.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadPowerAnalysisResult:
    """
    Multirotor payload electrical power analysis output model.

    Attributes:
        payload_power_w (float): Payload power consumption in Watts.
        operating_voltage_v (float): Operating voltage in Volts.
        current_draw_a (float): Payload electrical current draw in Amperes.
        percentage_of_total_power (float): Payload share of total drone hover power percentage.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    payload_power_w: float
    operating_voltage_v: float
    current_draw_a: float
    percentage_of_total_power: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PayloadPowerAnalysis:
    """
    Analysis service for payload electrical power requirements.

    Design Principles:
        - Single Responsibility Principle: Payload electrical power consumption calculations only.
    """

    def analyze_power(
        self,
        payload_power_w: float,
        voltage_v: float = 12.0,
        total_hover_power_w: float = 350.0
    ) -> PayloadPowerAnalysisResult:
        """
        Calculates payload current draw and power percentage.

        Args:
            payload_power_w (float): Payload power in Watts.
            voltage_v (float): Supply voltage in Volts.
            total_hover_power_w (float): Total drone hover power in Watts.

        Returns:
            PayloadPowerAnalysisResult: Computed payload power analysis output.
        """
        current_a = payload_power_w / voltage_v if voltage_v > 0 else 0.0
        pct = (payload_power_w / total_hover_power_w) * 100.0 if total_hover_power_w > 0 else 0.0

        return PayloadPowerAnalysisResult(
            payload_power_w=payload_power_w,
            operating_voltage_v=voltage_v,
            current_draw_a=round(current_a, 2),
            percentage_of_total_power=round(pct, 2)
        )
