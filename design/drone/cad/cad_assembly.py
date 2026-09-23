"""
CADAssembly Subsystem

Purpose:
    Defines the `CADAssembly` domain model representing a hierarchical 3D CAD assembly.

Role in Architecture:
    `CADAssembly` encapsulates assembly name, list of child `CADComponent` items, list of subassemblies,
    total assembly mass in grams, and 3D bounding box bounds.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.cad.cad_component import CADComponent


@dataclass(slots=True)
class CADAssembly:
    """
    Hierarchical 3D CAD assembly definition.

    Attributes:
        assembly_name (str): Assembly identifier name (e.g. 'Master Assembly', 'Frame Assembly', 'Propulsion Assembly').
        components (list[CADComponent]): List of child CAD components.
        subassemblies (list['CADAssembly']): List of nested subassemblies.
        total_mass_g (float): Total assembly mass in grams.
        bounding_box_mm (tuple[float, float, float]): Master assembly bounding box (L, W, H) in mm.
        metadata (dict[str, Any]): Additional assembly metadata.
    """

    assembly_name: str
    components: list[CADComponent] = field(default_factory=list)
    subassemblies: list["CADAssembly"] = field(default_factory=list)
    total_mass_g: float = 0.0
    bounding_box_mm: tuple[float, float, float] = (0.0, 0.0, 0.0)
    metadata: dict[str, Any] = field(default_factory=dict)
