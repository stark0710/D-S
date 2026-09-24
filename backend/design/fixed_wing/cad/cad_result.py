"""
Fixed-Wing CAD Result Subsystem

Purpose:
    Defines the `CADResult` class representing the output of the CAD Generation Framework.

Role in Architecture:
    `CADResult` carries paths of generated STEP/STL files, feature history tree, and volume diagnostics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.cad.cad_metadata import CADMetadata


@dataclass(slots=True)
class CADResult:
    """
    Consolidated output of the parametric CAD generation workflow.

    Attributes:
        cad_model (Any): Parametric CAD solid description (or backend specific shape object).
        assembly (Any): Sized assembly containing coordinate transformation placements.
        parts (Dict[str, Any]): Dictionary of generated individual part solids.
        feature_tree (Any): chronological feature build operations list.
        reference_geometry (Any): Reference coordinate datums, planes, and axes.
        engineering_parameters (Dict[str, Any]): mapped engineering parameters used during modeling.
        exported_files (Dict[str, str]): Map of file formats (e.g. STEP, STL) to absolute local paths.
        cad_metadata (CADMetadata): diagnostics metadata summarizing volume and sizes.
        engineering_notes: List[str] = field(default_factory=list)
        recommendations: List[str] = field(default_factory=list)
        warnings: List[str] = field(default_factory=list)
        metadata: Dict[str, Any] = field(default_factory=dict)
    """

    cad_model: Any
    assembly: Any
    parts: Dict[str, Any]
    feature_tree: Any
    reference_geometry: Any
    engineering_parameters: Dict[str, Any]
    exported_files: Dict[str, str]
    cad_metadata: CADMetadata
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing CAD Result model.
"""
