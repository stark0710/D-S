"""
VTOL Actuator Layout Subsystem

Purpose:
    Defines the `ActuatorLayout` dataclass detailing control surface servos,
    ESC wiring channels, and physical coordinates.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ActuatorLayout:
    """
    Mapping of control surfaces, motors, and vectoring mechanisms of the VTOL.

    Attributes:
        control_channels_count (int): Sized total RC output signals required.
        servo_count (int): Number of mechanical servos.
        esc_count (int): Number of motor electronic speed controllers.
        aerodynamic_surface_actuators (List[str]): List of control surface functions.
        propulsion_actuators (List[str]): List of motor signals.
        tilt_actuators (List[str]): List of servo signals for tilt mechanics.
        actuator_placements (List[Dict[str, Any]]): Placements coordinate positions (x, y, z).
        metadata (Dict[str, Any]): Additional wiring specifications.
    """

    control_channels_count: int
    servo_count: int
    esc_count: int
    aerodynamic_surface_actuators: List[str]
    propulsion_actuators: List[str]
    tilt_actuators: List[str]
    actuator_placements: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
