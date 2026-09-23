"""
VTOL Wing Motor Mounts Subsystem

Purpose:
    Defines the `MotorMount` and `MotorMounts` classes positioning propulsion clamps,
    pylons, and tilt mechanism servos on the wing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class MotorMount:
    """
    Spatially located motor mount on the wing structure.

    Attributes:
        name (str): The identifier of the mount (e.g. Lift Motor 1).
        motor_index (int): Motor reference identifier.
        position_x_m (float): Longitudinal distance from CG.
        position_y_m (float): Spanwise distance from centerline (left is negative).
        position_z_m (float): Vertical distance from wing chord line.
        mount_type (str): Clamp/sleeve structure style.
        estimated_mass_kg (float): Mass of mounts, wiring, and collars in kg.
        max_thrust_n_limit (float): Maximum thrust load support limit.
    """

    name: str
    motor_index: int
    position_x_m: float
    position_y_m: float
    position_z_m: float
    mount_type: str
    estimated_mass_kg: float
    max_thrust_n_limit: float


@dataclass(slots=True)
class MotorMounts:
    """
    Consolidated list of wing-mounted propulsion interfaces.

    Attributes:
        mounts (List[MotorMount]): Sized list of mounts.
        has_tilt_mechanism (bool): True if wing has vectoring servos.
        tilt_servo_torque_nm (float): Required servo torque for tilt vectoring.
        metadata (Dict[str, Any]): Additional boom tubing specifications.
    """

    mounts: List[MotorMount]
    has_tilt_mechanism: bool
    tilt_servo_torque_nm: float
    metadata: Dict[str, Any] = field(default_factory=dict)
