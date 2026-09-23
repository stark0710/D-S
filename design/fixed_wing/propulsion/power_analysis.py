"""
Fixed-Wing Propulsion Power Analysis Subsystem

Purpose:
    Defines the `PowerAnalysis` class and sizing calculations.

Role in Architecture:
    `PowerAnalysis` evaluates cruise electrical draw, climb load, and maximum throttle power draw.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class PowerAnalysis:
    """
    Electrical/shaft power metrics.

    Attributes:
        required_cruise_power_w (float): Power required to sustain cruise speed.
        required_climb_power_w (float): Sized power required for steady rate of climb.
        maximum_power_w (float): Maximum structural power limit of selected motor.
        current_draw_cruise_a (float): Sized battery current draw in Amps at cruise.
        metadata (Dict[str, Any]): Voltages and motor efficiency records.
    """

    required_cruise_power_w: float
    required_climb_power_w: float
    maximum_power_w: float
    current_draw_cruise_a: float
    metadata: Dict[str, Any] = field(default_factory=dict)
