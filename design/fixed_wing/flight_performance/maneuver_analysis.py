"""
Fixed-Wing Maneuver Performance Analysis Subsystem

Purpose:
    Defines the `ManeuverAnalysis` class.

Role in Architecture:
    `ManeuverAnalysis` holds maneuvering velocities and structural G limits.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ManeuverAnalysis:
    """
    Flight maneuver envelope metrics.

    Attributes:
        max_load_factor (float): Maximum structural G load capacity.
        maneuvering_speed_kmh (float): Safe maneuvering airspeed (Va).
        max_bank_angle_deg (float): Sized bank limit.
        metadata (Dict[str, Any]): Lift coordinates during banking.
    """

    max_load_factor: float
    maneuvering_speed_kmh: float
    max_bank_angle_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
