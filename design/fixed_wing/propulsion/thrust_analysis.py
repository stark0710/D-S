"""
Fixed-Wing Propulsion Thrust Analysis Subsystem

Purpose:
    Defines the `ThrustAnalysis` class and sizing calculations.

Role in Architecture:
    `ThrustAnalysis` evaluates static thrust, cruise drag forces, and thrust-to-weight margins.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ThrustAnalysis:
    """
    Thrust metrics across cruise and takeoff phases.

    Attributes:
        required_cruise_thrust_n (float): Drag thrust required to sustain cruise.
        required_takeoff_thrust_n (float): Sized takeoff thrust target.
        estimated_static_thrust_n (float): Static thrust delivered by propeller at maximum power.
        thrust_to_weight_ratio (float): Sized takeoff thrust-to-weight ratio (T/W).
        power_loading_w_kg (float): Power loading coefficient (Watts per kg of MTOW).
        metadata (Dict[str, Any]): Intermediate forces and settings.
    """

    required_cruise_thrust_n: float
    required_takeoff_thrust_n: float
    estimated_static_thrust_n: float
    thrust_to_weight_ratio: float
    power_loading_w_kg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
