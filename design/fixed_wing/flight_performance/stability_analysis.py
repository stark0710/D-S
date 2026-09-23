"""
Fixed-Wing Stability Analysis Subsystem

Purpose:
    Defines the `StabilityAnalysis` class.

Role in Architecture:
    `StabilityAnalysis` holds stability margin, pitch, yaw, and roll levels.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class StabilityAnalysis:
    """
    Flight static stability metrics.

    Attributes:
        static_margin (float): Sized static margin fraction of MAC.
        pitch_stability_level (str): pitch stability rating (Stable, Marginal).
        yaw_stability_level (str): Yaw stability rating.
        roll_stability_level (str): Roll stability rating.
        neutral_point_x_m (float): Longitudinal coordinate of neutral point.
        metadata (Dict[str, Any]): Tail volume coefficients.
    """

    static_margin: float
    pitch_stability_level: str
    yaw_stability_level: str
    roll_stability_level: str
    neutral_point_x_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
