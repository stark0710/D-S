"""
CADProfile Subsystem

Purpose:
    Defines the `CADProfile` domain model representing CAD generation settings and parameters.

Role in Architecture:
    `CADProfile` specifies mesh resolution level ('LOW', 'MEDIUM', 'HIGH', 'MANUFACTURING'), coordinate system convention, and CAD backend choice.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CADProfile:
    """
    Multirotor CAD generation specification profile.

    Attributes:
        mesh_resolution (str): Mesh geometry resolution ('LOW', 'MEDIUM', 'HIGH', 'MANUFACTURING').
        coordinate_system (str): Coordinate frame convention ('NED', 'ENU', 'AIRCRAFT_STANDARD').
        export_format (str): Desired CAD export format ('STEP', 'IGES', 'STL', 'OBJ', 'JSON_PARAMETRIC').
        metadata (dict[str, Any]): Additional CAD profile metadata.
    """

    mesh_resolution: str = "HIGH"
    coordinate_system: str = "AIRCRAFT_STANDARD"
    export_format: str = "STEP"
    metadata: dict[str, Any] = field(default_factory=dict)
