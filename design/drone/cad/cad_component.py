"""
CADComponent Subsystem

Purpose:
    Defines the `CADComponent` domain model representing a parametric 3D CAD component geometry.

Role in Architecture:
    `CADComponent` encapsulates component name, category classification ('FRAME', 'ARM', 'LANDING_GEAR', 'MOTOR',
    'PROPELLER', 'ESC', 'BATTERY', 'PDB', 'FLIGHT_CONTROLLER', 'GPS', 'TELEMETRY', 'RECEIVER', 'PAYLOAD', 'MOUNT', 'FASTENER'),
    bounding box dimensions (L, W, H mm), material, mass in g, 3D translation offset (X, Y, Z in mm), and 3D rotation (Pitch, Roll, Yaw in deg).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CADComponent:
    """
    Parametric 3D CAD component geometry definition.

    Attributes:
        name (str): Component identifier name.
        category (str): Subsystem category identifier.
        bounding_box_mm (tuple[float, float, float]): Bounding box dimensions (Length, Width, Height) in mm.
        material (str): Component material description.
        mass_g (float): Component mass in grams.
        position_mm (tuple[float, float, float]): 3D translation position (X, Y, Z) in mm.
        rotation_deg (tuple[float, float, float]): 3D rotation Euler angles (Roll, Pitch, Yaw) in degrees.
        cad_shape_type (str): Geometric primitive type ('BOX', 'CYLINDER', 'SPHERE', 'MESH_STEP').
        metadata (dict[str, Any]): Additional CAD geometry metadata.
    """

    name: str
    category: str
    bounding_box_mm: tuple[float, float, float]
    material: str = "Carbon Fiber / Aluminum"
    mass_g: float = 100.0
    position_mm: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    cad_shape_type: str = "BOX"
    metadata: dict[str, Any] = field(default_factory=dict)
