"""
FrameProfile Subsystem

Purpose:
    Defines the `FrameProfile` domain model representing multirotor frame structural parameters.

Role in Architecture:
    `FrameProfile` encapsulates frame name, motor-to-motor wheelbase in mm, frame mass in grams,
    maximum propeller diameter capacity in inches, frame material, and stiffness rating.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FrameProfile:
    """
    Multirotor physical frame specification profile.

    Attributes:
        frame_name (str): Identifier name string (e.g. 'Tarot X6 Hexacopter 960mm').
        wheelbase_mm (float): Motor-to-motor diagonal distance in mm.
        frame_weight_g (float): Total bare frame weight in grams.
        max_propeller_diameter_inch (float): Maximum propeller diameter supported without blade collision.
        material (str): Primary frame composite material description.
        stiffness_rating (str): Structural rigidity rating ('STANDARD', 'HIGH', 'ULTRA_RIGID').
        metadata (dict[str, Any]): Additional frame profile metadata.
    """

    frame_name: str
    wheelbase_mm: float
    frame_weight_g: float
    max_propeller_diameter_inch: float
    material: str = "Carbon Fiber Composite"
    stiffness_rating: str = "HIGH"
    metadata: dict[str, Any] = field(default_factory=dict)
