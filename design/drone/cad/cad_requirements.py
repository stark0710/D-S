"""
CADRequirements Subsystem

Purpose:
    Defines the `CADRequirements` domain model representing input requirements for CAD model generation.

Role in Architecture:
    `CADRequirements` specifies required CAD backend, export format, collision check requirement, and minimum clearance limit in mm.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CADRequirements:
    """
    Multirotor CAD generation requirements model.

    Attributes:
        preferred_cad_backend (str): Preferred CAD backend ('FreeCADStrategy', 'OpenVSPStrategy', 'NeutralCADStrategy').
        export_format (str): Target file export format ('STEP', 'IGES', 'STL', 'OBJ', 'JSON_PARAMETRIC').
        collision_free_required (bool): True if zero 3D AABB collisions are strictly required.
        min_clearance_mm (float): Minimum component clearance requirement in mm (default 10.0 mm).
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    preferred_cad_backend: str = "NeutralCADStrategy"
    export_format: str = "STEP"
    collision_free_required: bool = True
    min_clearance_mm: float = 10.0
    metadata: dict[str, Any] = field(default_factory=dict)
