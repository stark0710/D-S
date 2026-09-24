"""
EfficiencyAnalysis Subsystem

Purpose:
    Defines the `EfficiencyAnalysis` class and `EfficiencyAnalysisResult` dataclass for propulsion efficiency evaluation.

Role in Architecture:
    `EfficiencyAnalysis` evaluates propeller tip speed in m/s, motor efficiency percentage, and overall propulsion efficiency score.
"""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EfficiencyAnalysisResult:
    """
    Multirotor propulsion efficiency output model.

    Attributes:
        overall_efficiency_score (float): Normalized overall efficiency score (0.0 to 1.0).
        propeller_tip_speed_m_s (float): Calculated propeller tip speed in m/s (must remain < 220 m/s for noise/efficiency).
        motor_efficiency_percent (float): Estimated motor electrical efficiency percentage (e.g. 82-88%).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    overall_efficiency_score: float
    propeller_tip_speed_m_s: float
    motor_efficiency_percent: float = 85.0
    metadata: dict[str, Any] = field(default_factory=dict)


class EfficiencyAnalysis:
    """
    Analysis service for multirotor propulsion efficiency.

    Design Principles:
        - Single Responsibility Principle: Propeller tip speed and propulsion efficiency physics only.
    """

    def analyze_efficiency(
        self,
        propeller_diameter_inch: float,
        operating_voltage_v: float,
        motor_kv: float,
        hover_throttle_percent: float = 45.0
    ) -> EfficiencyAnalysisResult:
        """
        Calculates propeller tip speed and propulsion efficiency.

        Args:
            propeller_diameter_inch (float): Propeller diameter in inches.
            operating_voltage_v (float): Voltage in Volts.
            motor_kv (float): Motor KV rating (RPM per Volt).
            hover_throttle_percent (float): Hover throttle percentage.

        Returns:
            EfficiencyAnalysisResult: Computed efficiency analysis output.
        """
        # Estimate RPM at hover
        max_rpm = motor_kv * operating_voltage_v
        hover_rpm = max_rpm * (hover_throttle_percent / 100.0)

        # Propeller tip speed v_tip = Omega * r = (2 * pi * RPM / 60) * (diameter_m / 2)
        radius_m = (propeller_diameter_inch * 0.0254) / 2.0
        omega_rad_s = (2.0 * math.pi * hover_rpm) / 60.0
        tip_speed_m_s = omega_rad_s * radius_m

        # Optimal tip speed is between 80 m/s and 160 m/s
        eff_score = 0.85
        if tip_speed_m_s > 200.0:
            eff_score -= 0.20  # High noise & compressibility losses
        elif tip_speed_m_s < 50.0:
            eff_score -= 0.10

        return EfficiencyAnalysisResult(
            overall_efficiency_score=round(eff_score, 2),
            propeller_tip_speed_m_s=round(tip_speed_m_s, 1),
            motor_efficiency_percent=85.0
        )
