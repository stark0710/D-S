"""
VTOL Landing Gear Interfaces Subsystem

Purpose:
    Defines the `GearAttachmentPoint` and `LandingGearInterfaces` classes
    determining wheel tracks, skids, and fuselage load reinforcements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class GearAttachmentPoint:
    """
    Landing gear connection point coordinates.

    Attributes:
        name (str): Joint identifier (e.g. Nose Gear, Left Skid Plate).
        location_x_m (float): Distance from nose.
        location_y_m (float): Lateral offset from centerline.
        location_z_m (float): Vertical offset from centerline.
        structural_reinforcement_needed (bool): True if bulkheads need composite stiffeners.
    """

    name: str
    location_x_m: float
    location_y_m: float
    location_z_m: float
    structural_reinforcement_needed: bool


@dataclass(slots=True)
class LandingGearInterfaces:
    """
    Sized landing gears track specifications.

    Attributes:
        attachment_points (List[GearAttachmentPoint]): Mount locations.
        landing_gear_type (str): Sized style (e.g., Skid, Tricycle, Belly Skid pads).
        track_width_m (float): Sized lateral wheel distance.
        wheelbase_m (float): Sized longitudinal nose-to-rear gear distance.
        metadata (Dict[str, Any]): Retract servo channels.
    """

    attachment_points: List[GearAttachmentPoint]
    landing_gear_type: str
    track_width_m: float
    wheelbase_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
