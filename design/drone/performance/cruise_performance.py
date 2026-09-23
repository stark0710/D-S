"""
CruisePerformance Subsystem

Purpose:
    Defines the `CruisePerformance` class and `CruisePerformanceResult` dataclass for forward cruise flight evaluation.

Role in Architecture:
    `CruisePerformance` calculates optimal cruise velocity in km/h, maximum horizontal velocity in km/h,
    cruise power consumption in Watts, and tilt pitch angle in degrees.
"""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CruisePerformanceResult:
    """
    Multirotor cruise performance evaluation output model.

    Attributes:
        optimal_cruise_speed_kmh (float): Optimal energy-efficient cruise velocity in km/h.
        max_horizontal_speed_kmh (float): Maximum forward horizontal speed in km/h.
        cruise_power_w (float): Power consumption during forward cruise in Watts.
        pitch_angle_deg (float): Forward tilt pitch angle in degrees at optimal cruise.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    optimal_cruise_speed_kmh: float
    max_horizontal_speed_kmh: float
    cruise_power_w: float
    pitch_angle_deg: float
    metadata: dict[str, Any] = field(default_factory=dict)


class CruisePerformance:
    """
    Analysis service for forward cruise flight physics.

    Design Principles:
        - Single Responsibility Principle: Forward cruise velocity, tilt angle, and aerodynamic power calculation only.
    """

    def analyze_cruise(
        self,
        total_mass_kg: float,
        hover_power_w: float,
        max_power_w: float,
        target_cruise_speed_kmh: float = 50.0
    ) -> CruisePerformanceResult:
        """
        Calculates optimal cruise speed, maximum forward speed, and cruise power.

        Args:
            total_mass_kg (float): AUW mass in kg.
            hover_power_w (float): Hover power in Watts.
            max_power_w (float): Max power in Watts.
            target_cruise_speed_kmh (float): Target cruise speed in km/h.

        Returns:
            CruisePerformanceResult: Computed cruise performance output.
        """
        v_cruise_ms = target_cruise_speed_kmh / 3.6

        # Pitch tilt angle theta = arctan(Drag / Weight) ~ theta = 15 to 25 deg at cruise
        pitch_deg = round(math.degrees(math.atan(0.20 + (v_cruise_ms * 0.015))), 1)

        # Forward translational lift reduces power at moderate speeds, but parasitical drag increases power at high speeds
        # P_cruise ~ P_hover * 0.85 + 0.5 * rho * v^3 * CdA
        parasite_drag_w = 0.5 * 1.225 * (v_cruise_ms ** 3) * 0.12
        cruise_p = round((hover_power_w * 0.82) + parasite_drag_w, 1)

        # Maximum horizontal speed
        max_v_ms = ((max_power_w - (hover_power_w * 0.80)) / (0.5 * 1.225 * 0.12)) ** (1/3) if max_power_w > hover_power_w else v_cruise_ms
        max_speed_kmh = round(min(120.0, max_v_ms * 3.6), 1)

        return CruisePerformanceResult(
            optimal_cruise_speed_kmh=target_cruise_speed_kmh,
            max_horizontal_speed_kmh=max_speed_kmh,
            cruise_power_w=cruise_p,
            pitch_angle_deg=pitch_deg
        )
