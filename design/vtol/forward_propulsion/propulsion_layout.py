"""
VTOL Forward Propulsion Layout Subsystem

Purpose:
    Defines the `ForwardPlacement` and `ForwardPropulsionLayout` classes capturing
    cruise motor positions and vector paths.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ForwardPlacement:
    """
    Coordinates and details of an individual forward propulsion motor.

    Attributes:
        name (str): Motor placement identifier (e.g. Center Rear Pusher).
        motor_model (str): Selected brushless motor model.
        propeller_model (str): Selected propeller model.
        esc_model (str): Selected ESC rating.
        x_m (float): Longitudinal distance from CG.
        y_m (float): Lateral offset from centerline.
        z_m (float): Vertical offset from centerline.
        thrust_vector (List[float]): Normalized vector direction of thrust (usually [1.0, 0.0, 0.0]).
    """

    name: str
    motor_model: str
    propeller_model: str
    esc_model: str
    x_m: float
    y_m: float
    z_m: float
    thrust_vector: List[float]


@dataclass(slots=True)
class ForwardPropulsionLayout:
    """
    Consolidated forward propulsion installation configuration.

    Attributes:
        placements (List[ForwardPlacement]): Individual motor placement coordinate details.
        architecture (str): Layout style (e.g., Single Pusher, Twin Tractor).
        metadata (Dict[str, Any]): Structural firewalls or pod references.
    """

    placements: List[ForwardPlacement]
    architecture: str
    metadata: Dict[str, Any] = field(default_factory=dict)
