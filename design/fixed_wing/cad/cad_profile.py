"""
Fixed-Wing CAD Profile Subsystem

Purpose:
    Defines the `CADProfile` class containing default formatting choices.

Role in Architecture:
    `CADProfile` sets defaults like STEP tolerances, OBJ mesh densities, and default backends.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class CADProfile:
    """
    Configuration profile defining format settings and tolerances for CAD generation.

    Attributes:
        default_backend (str): Backend selection ("CadQuery", "OpenCascade", "FreeCAD").
        default_export_format (str): Default export format ("STEP", "IGES", "STL", "GLTF").
        mesh_resolution (str): Tessellation density ("Low", "Medium", "High").
        clearance_tolerance_mm (float): Default joint assembly clearance buffer (default 0.2 mm).
    """

    default_backend: str = "CadQuery"
    default_export_format: str = "STEP"
    mesh_resolution: str = "Medium"
    clearance_tolerance_mm: float = 0.2
