"""
VTOL Mission Hover Requirements Subsystem

Purpose:
    Defines the `HoverRequirements` dataclass capturing parameters specific to the hover phase.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class HoverRequirements:
    """
    Requirements specific to the VTOL hover flight regime.

    Attributes:
        hover_duration_min (float): Target cumulative hover time in minutes.
        hover_altitude_m (float): Altitude for hover operations in meters above sea level.
        wind_limit_hover_kts (float): Maximum wind speed for safe hover operations in knots.
        climb_rate_vertical_m_s (float): Target vertical climb rate in meters per second.
        descent_rate_vertical_m_s (float): Target vertical descent rate in meters per second.
        metadata (Dict[str, Any]): Additional unstructured parameters or settings.
    """

    hover_duration_min: float
    hover_altitude_m: float
    wind_limit_hover_kts: float
    climb_rate_vertical_m_s: float
    descent_rate_vertical_m_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
