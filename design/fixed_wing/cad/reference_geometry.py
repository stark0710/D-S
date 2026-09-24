"""
Fixed-Wing CAD Reference Geometry Subsystem

Purpose:
    Defines reference planes, axes, and construction coordinates for the aircraft.

Role in Architecture:
    `ReferenceGeometry` holds datum systems to position parts relative to symmetry lines.
"""

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass(slots=True)
class ReferenceGeometry:
    """
    Reference geometry system for CAD modeling.

    Attributes:
        symmetry_plane_normal (Tuple[float, float, float]): (x, y, z) normal vector for symmetry.
        thrust_axis (Tuple[float, float, float]): (x, y, z) direction vector of propulsion line.
        datum_points (List[Tuple[str, Tuple[float, float, float]]]): Key positions (e.g. Aerodynamic Center).
    """

    symmetry_plane_normal: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    thrust_axis: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    datum_points: List[Tuple[str, Tuple[float, float, float]]] = field(default_factory=list)
