"""
VTOL Fuselage Boom Interfaces Subsystem

Purpose:
    Defines the `BoomAttachmentPoint` and `BoomInterfaces` classes detailing pylon
    attachments, structural sleeves, and tube clamping locations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class BoomAttachmentPoint:
    """
    Sized joint location for a propulsion boom.

    Attributes:
        name (str): Pylon mount name.
        location_x_m (float): Distance from fuselage nose.
        location_y_m (float): Lateral offset from centerline.
        location_z_m (float): Vertical offset from centerline.
        structural_support_concept (str): Collar joint description (e.g. Ring clamp).
    """

    name: str
    location_x_m: float
    location_y_m: float
    location_z_m: float
    structural_support_concept: str


@dataclass(slots=True)
class BoomInterfaces:
    """
    Sized boom sleeve layout.

    Attributes:
        attachment_points (List[BoomAttachmentPoint]): Sleeve attachment joints.
        number_of_booms (int): Sized count of booms linking to fuselage.
        boom_diameter_mm (float): Outer diameter of booms.
        metadata (Dict[str, Any]): Boom wiring channels.
    """

    attachment_points: List[BoomAttachmentPoint]
    number_of_booms: int
    boom_diameter_mm: float
    metadata: Dict[str, Any] = field(default_factory=dict)
