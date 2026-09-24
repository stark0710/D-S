"""
Fixed-Wing Propulsion Cruise Analysis Subsystem

Purpose:
    Defines the `CruiseAnalysis` class and sizing calculations.

Role in Architecture:
    `CruiseAnalysis` evaluates cruise speed profiles, required thruster slip, and cruise range capability.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CruiseAnalysis:
    """
    Cruise flight regime propulsion metrics.

    Attributes:
        cruise_speed_kmh (float): Cruise speed target.
        required_cruise_thrust_n (float): Drag force opposing motion.
        prop_rpm_cruise (float): Required propeller RPM to maintain cruise speed.
        throttle_setting_pct (float): Estimated throttle percentage at cruise (typically 40-60%).
        metadata (Dict[str, Any]): Intermediate drag and advance ratio calculations.
    """

    cruise_speed_kmh: float
    required_cruise_thrust_n: float
    prop_rpm_cruise: float
    throttle_setting_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
