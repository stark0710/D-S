"""
VTOL Tail Control Surfaces Subsystem

Purpose:
    Defines the `TailControls` class sizing control flaps and mixing algorithms.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailControls:
    """
    Sizing parameters for active elevator and rudder flaps.

    Attributes:
        elevator_area_m2 (float): Surface area of elevator flaps.
        elevator_span_m (float): Total span of elevator flaps.
        rudder_area_m2 (float): Surface area of rudder flaps.
        rudder_span_m (float): Total vertical span of rudder flaps.
        control_mixing_type (str): Mixing style (e.g., V-tail Mixer, Conventional).
        metadata (Dict[str, Any]): Servo torque requirements.
    """

    elevator_area_m2: float
    elevator_span_m: float
    rudder_area_m2: float
    rudder_span_m: float
    control_mixing_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
