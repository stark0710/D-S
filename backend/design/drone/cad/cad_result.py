"""
CADResult Subsystem

Purpose:
    Defines the `CADResult` domain model representing output from the Drone CAD Generation Engineering Framework.

Role in Architecture:
    `CADResult` encapsulates `cad_model` (`CADModel`), `assembly` (`CADAssembly`), `components` list (`CADComponent`),
    `placements` list, `geometry_analysis` dictionary, `collision_report` list, `clearance_report` dictionary,
    `generated_files` dictionary, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.cad.cad_model import CADModel
from backend.design.drone.cad.cad_assembly import CADAssembly
from backend.design.drone.cad.cad_component import CADComponent


@dataclass(slots=True)
class CADResult:
    """
    Multirotor CAD generation engineering output summary.

    Attributes:
        cad_model (CADModel): Parametric 3D CAD model summary object.
        assembly (CADAssembly): Master assembly tree object.
        components (list[CADComponent]): List of all generated CAD components.
        placements (list[dict[str, Any]]): 3D spatial placement coordinates list.
        geometry_analysis (dict[str, Any]): Geometry analysis summary (bounding box, total volume, total mass).
        collision_report (list[str]): List of detected collision error strings.
        clearance_report (dict[str, float]): Clearance analysis dictionary.
        generated_files (dict[str, Any]): Exported CAD file format payloads.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during CAD generation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    cad_model: CADModel
    assembly: CADAssembly
    components: list[CADComponent]
    placements: list[dict[str, Any]]
    geometry_analysis: dict[str, Any]
    collision_report: list[str]
    clearance_report: dict[str, float]
    generated_files: dict[str, Any]
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
