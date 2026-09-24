"""
ClimbPerformance Subsystem

Purpose:
    Defines the `ClimbPerformance` class and `ClimbPerformanceResult` dataclass for vertical climb performance evaluation.

Role in Architecture:
    `ClimbPerformance` calculates maximum vertical climb rate in m/s, required climb power in Watts, and climb thrust margin.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ClimbPerformanceResult:
    """
    Multirotor climb performance evaluation output model.

    Attributes:
        max_climb_rate_m_s (float): Maximum vertical climb velocity in m/s.
        climb_power_w (float): Power required during maximum vertical climb in Watts.
        climb_thrust_margin (float): Remaining thrust margin during climb.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    max_climb_rate_m_s: float
    climb_power_w: float
    climb_thrust_margin: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ClimbPerformance:
    """
    Analysis service for vertical climb performance.

    Design Principles:
        - Single Responsibility Principle: Vertical climb velocity, climb power, and thrust margin calculation only.
    """

    def analyze_climb(
        self,
        total_mass_kg: float,
        hover_power_w: float,
        max_power_w: float,
        actual_tw_ratio: float
    ) -> ClimbPerformanceResult:
        """
        Calculates maximum climb rate and climb power consumption.

        Args:
            total_mass_kg (float): AUW mass in kg.
            hover_power_w (float): Hover power in Watts.
            max_power_w (float): Max power in Watts.
            actual_tw_ratio (float): Available T/W ratio.

        Returns:
            ClimbPerformanceResult: Computed climb performance output.
        """
        # Maximum climb rate is proportional to excess thrust margin
        excess_tw = max(0.1, actual_tw_ratio - 1.0)
        max_climb_rate = min(12.0, round(excess_tw * 6.0, 1))

        # Climb power P_climb = P_hover + (m * g * v_climb) / eta_prop
        weight_n = total_mass_kg * 9.80665
        potential_power_w = (weight_n * max_climb_rate) / 0.70
        climb_p = min(max_power_w * 0.90, hover_power_w + potential_power_w)

        return ClimbPerformanceResult(
            max_climb_rate_m_s=max_climb_rate,
            climb_power_w=round(climb_p, 1),
            climb_thrust_margin=round(actual_tw_ratio - 1.0, 2)
        )
