"""
Fixed-Wing CAD Coordinate System Subsystem

Purpose:
    Defines local and global coordinate systems and transforms for the aircraft CAD model.

Role in Architecture:
    `CoordinateSystem` provides 3D rotation and translation helpers.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(slots=True)
class CoordinateSystem:
    """
    Physical 3D Coordinate System frame.

    Attributes:
        origin (Tuple[float, float, float]): (x, y, z) translation from global origin (nose).
        orientation (Tuple[float, float, float]): (roll, pitch, yaw) rotation angles in degrees.
    """

    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    orientation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
