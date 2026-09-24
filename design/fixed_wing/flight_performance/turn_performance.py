"""
Fixed-Wing Turn Performance Subsystem

Purpose:
    Defines the `TurnAnalysis` class.

Role in Architecture:
    `TurnAnalysis` holds bank angles, structural load factors, and turn radiuses.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class TurnAnalysis:
    """
    Steep banking turn performance metrics.

    Attributes:
        turn_radius_m (float): Sized radius of turn at steady bank.
        load_factor (float): Sized structural load factor (n = L/W).
        bank_angle_deg (float): Bank angle.
        turn_rate_deg_s (float): Yaw turn rate.
        metadata (Dict[str, Any]): Lift coefficients during banking.
    """

    turn_radius_m: float
    load_factor: float
    bank_angle_deg: float
    turn_rate_deg_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
