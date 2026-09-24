"""
LandingGear Subsystem

Purpose:
    Defines the `LandingGear` domain model representing multirotor landing gear structural specifications.

Role in Architecture:
    `LandingGear` encapsulates gear type classification ('FIXED_SKID', 'RETRACTABLE', 'INTEGRATED_LEG'),
    ground clearance height in mm, overall height in mm, mass in grams, and structural material.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LandingGear:
    """
    Multirotor landing gear structural specification model.

    Attributes:
        gear_type (str): Landing gear type ('FIXED_SKID', 'RETRACTABLE', 'INTEGRATED_LEG').
        ground_clearance_mm (float): Vertical distance between lowest payload/center-plate point and ground in mm.
        height_mm (float): Total vertical landing gear height in mm.
        weight_g (float): Total landing gear assembly weight in grams.
        material (str): Structural material description (e.g. 'Carbon Fiber & CNC Aluminum').
        metadata (dict[str, Any]): Additional landing gear metadata.
    """

    gear_type: str = "FIXED_SKID"
    ground_clearance_mm: float = 150.0
    height_mm: float = 200.0
    weight_g: float = 180.0
    material: str = "Carbon Fiber & CNC Aluminum"
    metadata: dict[str, Any] = field(default_factory=dict)
