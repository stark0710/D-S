"""
VTOL Lift Rotor Layout Subsystem

Purpose:
    Defines the `RotorPlacement` and `LiftRotorLayout` classes capturing
    actuator positions and rotor tip clearances.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class RotorPlacement:
    """
    Coordinates and details of an individual vertical lift rotor.

    Attributes:
        name (str): Rotor placement identifier (e.g. Front Left Rotor).
        motor_model (str): Selected brushless motor model.
        propeller_model (str): Selected carbon fiber propeller.
        x_m (float): Longitudinal distance from CG.
        y_m (float): Lateral offset from centerline.
        z_m (float): Vertical offset from centerline.
        orientation (str): Rotation direction (CW, CCW).
    """

    name: str
    motor_model: str
    propeller_model: str
    x_m: float
    y_m: float
    z_m: float
    orientation: str


@dataclass(slots=True)
class LiftRotorLayout:
    """
    Consolidated physical vertical lift layout.

    Attributes:
        rotors (List[RotorPlacement]): Individual rotor positions.
        rotor_spacing_m (float): Sized spacing between closest rotors.
        distributed_propulsion_active (bool): True if layout utilizes multiple small rotors.
        metadata (Dict[str, Any]): Structural attachment points details.
    """

    rotors: List[RotorPlacement]
    rotor_spacing_m: float
    distributed_propulsion_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
