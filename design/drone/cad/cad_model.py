"""
CADModel Subsystem

Purpose:
    Defines the `CADModel` domain model representing overall parametric 3D CAD model parameters.

Role in Architecture:
    `CADModel` encapsulates model name, `CADAssembly`, format capability list, and CAD backend strategy identifier.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.cad.cad_assembly import CADAssembly


@dataclass(slots=True)
class CADModel:
    """
    Multirotor overall parametric 3D CAD model definition.

    Attributes:
        model_name (str): Aircraft CAD model name.
        assembly (CADAssembly): Master CAD assembly tree.
        backend_strategy (str): CAD backend identifier ('FreeCADStrategy', 'OpenVSPStrategy', 'NeutralCADStrategy').
        supported_formats (list[str]): List of supported export formats.
        metadata (dict[str, Any]): Additional CAD model metadata.
    """

    model_name: str
    assembly: CADAssembly
    backend_strategy: str = "NeutralCADStrategy"
    supported_formats: list[str] = field(default_factory=lambda: ["STEP", "IGES", "STL", "OBJ", "JSON_PARAMETRIC"])
    metadata: dict[str, Any] = field(default_factory=dict)
