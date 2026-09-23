"""
Fixed-Wing Endurance Performance Analysis Subsystem

Purpose:
    Defines the `EnduranceAnalysis` class.

Role in Architecture:
    `EnduranceAnalysis` holds maximum flight time predictions and continuous power draws.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class EnduranceAnalysis:
    """
    Flight endurance time metrics.

    Attributes:
        maximum_endurance_min (float): Sized max flight duration.
        cruise_endurance_min (float): Safe operational flight duration.
        average_power_draw_w (float): continuous power draw.
        metadata (Dict[str, Any]): Battery/fuel capacities.
    """

    maximum_endurance_min: float
    cruise_endurance_min: float
    average_power_draw_w: float
    metadata: Dict[str, Any] = field(default_factory=dict)
