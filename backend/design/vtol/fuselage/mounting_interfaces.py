"""
VTOL Fuselage Mounting Interfaces Subsystem

Purpose:
    Defines the `MountingInterface` and `MountingInterfaces` classes locating wingbox,
    tailboom, and battery harness hardpoint attachments.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class MountingInterface:
    """
    Sized mechanical hardpoint on the fuselage bulkhead.

    Attributes:
        name (str): The connection joint identifier (e.g. Wing Main Spar Bolt).
        type (str): Bolt pattern style (e.g. Clevis joint, Boom ring sleeve).
        location_x_m (float): Distance from fuselage nose.
        location_y_m (float): Lateral offset from centerline.
        location_z_m (float): Vertical offset from centerline.
        bolt_circle_diameter_mm (float): Sized diameter of bolt fittings.
        load_limit_n (float): Maximum structural load rating.
    """

    name: str
    type: str
    location_x_m: float
    location_y_m: float
    location_z_m: float
    bolt_circle_diameter_mm: float
    load_limit_n: float


@dataclass(slots=True)
class MountingInterfaces:
    """
    Consolidated hardpoint attachment points.

    Attributes:
        wing_attachment (MountingInterface): Wing attachment joint.
        tail_attachment (MountingInterface | None): Tail connector joint (if present).
        boom_attachment (MountingInterface | None): Quadplane pylon boom connector joint.
        metadata (Dict[str, Any]): Harness details.
    """

    wing_attachment: MountingInterface
    tail_attachment: MountingInterface | None = None
    boom_attachment: MountingInterface | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
