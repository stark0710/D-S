"""
WindAnalysis Subsystem

Purpose:
    Defines the `WindAnalysis` class and `WindAnalysisResult` dataclass for wind resistance and headwind performance evaluation.

Role in Architecture:
    `WindAnalysis` calculates maximum wind speed capability in m/s, pitch tilt angle in wind, and effective ground speed in headwind.
"""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WindAnalysisResult:
    """
    Multirotor wind resistance evaluation output model.

    Attributes:
        max_wind_tolerance_m_s (float): Maximum sustained wind speed tolerance in m/s.
        max_pitch_tilt_in_wind_deg (float): Forward/upwind tilt pitch angle in degrees.
        ground_speed_headwind_kmh (float): Effective net ground speed when flying against max wind in km/h.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    max_wind_tolerance_m_s: float
    max_pitch_tilt_in_wind_deg: float
    ground_speed_headwind_kmh: float
    metadata: dict[str, Any] = field(default_factory=dict)


class WindAnalysis:
    """
    Analysis service for wind tolerance and headwind ground speed.

    Design Principles:
        - Single Responsibility Principle: Wind resistance and headwind performance physics only.
    """

    def analyze_wind(
        self,
        actual_tw_ratio: float,
        cruise_speed_kmh: float,
        max_wind_speed_m_s: float = 10.0
    ) -> WindAnalysisResult:
        """
        Calculates maximum wind tolerance and ground speed.

        Args:
            actual_tw_ratio (float): Available T/W ratio.
            cruise_speed_kmh (float): Cruise speed in km/h.
            max_wind_speed_m_s (float): Specified wind tolerance requirement.

        Returns:
            WindAnalysisResult: Computed wind analysis output.
        """
        # Max wind capability is limited by T/W ratio (pitch tilt angle limit theta_max = arccos(1 / T/W))
        # e.g., T/W = 2.0 -> theta_max = 60 deg -> max_v_wind ~ 18 m/s
        max_tilt_rad = math.acos(1.0 / max(1.05, actual_tw_ratio))
        max_tilt_deg = math.degrees(max_tilt_rad)

        max_wind_capable = min(20.0, round(actual_tw_ratio * 7.5, 1))

        # Ground speed in headwind = Cruise Speed - Wind Speed
        headwind_kmh = max_wind_speed_m_s * 3.6
        net_ground_speed = max(5.0, round(cruise_speed_kmh - headwind_kmh, 1))

        return WindAnalysisResult(
            max_wind_tolerance_m_s=max_wind_capable,
            max_pitch_tilt_in_wind_deg=round(max_tilt_deg, 1),
            ground_speed_headwind_kmh=net_ground_speed
        )
