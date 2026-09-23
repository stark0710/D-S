"""
MountingLayout Subsystem

Purpose:
    Defines the `MountingLayout` domain model representing equipment and subsystem mounting interface specifications.

Role in Architecture:
    `MountingLayout` specifies mounting hole patterns for flight controllers, battery tray systems,
    payload rail interfaces, center plate dimensions, and internal volumetric clearance.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MountingLayout:
    """
    Multirotor equipment mounting layout model.

    Attributes:
        flight_controller_pattern_mm (str): FC mounting pattern string ('30.5x30.5', '20x20', '45x45').
        battery_mount_type (str): Battery attachment mechanism ('SLIDING_TRAY', 'BOTTOM_STRAP', 'TOP_RAIL').
        payload_mount_type (str): Payload attachment mechanism ('QUICK_RELEASE_RAIL', 'BOTTOM_PLATE_BOLTS', 'GIMBAL_DAMPED').
        center_plate_dimensions_mm (tuple[float, float]): Width and length of main central frame plate in mm.
        available_volume_cm3 (float): Total internal center frame enclosure volume in cm^3.
        metadata (dict[str, Any]): Additional mounting layout metadata.
    """

    flight_controller_pattern_mm: str = "30.5x30.5"
    battery_mount_type: str = "SLIDING_TRAY"
    payload_mount_type: str = "QUICK_RELEASE_RAIL"
    center_plate_dimensions_mm: tuple[float, float] = (200.0, 200.0)
    available_volume_cm3: float = 800.0
    metadata: dict[str, Any] = field(default_factory=dict)
