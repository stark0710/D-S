"""
PayloadProfile Subsystem

Purpose:
    Defines the `PayloadProfile` domain model representing multirotor mission payload specifications.

Role in Architecture:
    `PayloadProfile` encapsulates payload name, payload type ('RGB_CAMERA', 'THERMAL_CAMERA', 'LIDAR', 'SPRAYER', 'DELIVERY_BOX', etc.),
    mass in kg, 3D dimensions in mm, power draw in Watts, data interface, and mounting mechanism.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadProfile:
    """
    Multirotor mission payload specification profile.

    Attributes:
        payload_name (str): Human-readable payload name.
        payload_type (str): Payload classification ('RGB_CAMERA', 'THERMAL_CAMERA', 'LIDAR', 'SPRAYER', 'DELIVERY_BOX', 'MANIPULATOR', 'SCIENTIFIC_SENSOR', 'CUSTOM').
        mass_kg (float): Payload mass in kg.
        dimensions_mm (tuple[float, float, float]): 3D dimensions (Length, Width, Height) in mm.
        power_draw_w (float): Power consumption in Watts.
        data_interface (str): Communication interface specification.
        mounting_type (str): Mechanical mounting mechanism ('QUICK_RELEASE_RAIL', 'BOTTOM_PLATE_BOLTS', 'GIMBAL_DAMPED').
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    payload_name: str
    payload_type: str
    mass_kg: float
    dimensions_mm: tuple[float, float, float]
    power_draw_w: float
    data_interface: str
    mounting_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
