"""
AvionicsRequirements Subsystem

Purpose:
    Defines the `AvionicsRequirements` domain model representing input requirements for avionics design.

Role in Architecture:
    `AvionicsRequirements` specifies target range in km, autonomous navigation flag, RTK precision GNSS flag,
    companion computer requirement, and camera payload requirement.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AvionicsRequirements:
    """
    Multirotor avionics engineering requirements model.

    Attributes:
        target_range_km (float): Target operational line-of-sight range in km.
        autonomous_navigation (bool): True if autonomous waypoint navigation is required.
        rtk_precision_gps (bool): True if RTK centimeter-level precision GNSS is required.
        companion_computer_required (bool): True if onboard companion computer is required.
        camera_required (bool): True if camera payload is required.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    target_range_km: float = 10.0
    autonomous_navigation: bool = True
    rtk_precision_gps: bool = False
    companion_computer_required: bool = False
    camera_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
