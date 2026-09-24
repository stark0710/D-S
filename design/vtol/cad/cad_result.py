from dataclasses import dataclass, field
from typing import Any, Dict, List

from .assembly_generator import AssemblyModel
from .component_generator import PartModel
from .reference_geometry_generator import ReferenceGeometry
from .cad_exporter import ExportedFile
from .cad_analysis import InterferenceReport, ClearanceReport

@dataclass(slots=True)
class CADResult:
    """
    Consolidated outputs of the VTOL CAD Sizing pipeline.
    """
    assembly_model: AssemblyModel
    part_models: List[PartModel]
    assembly_hierarchy: List[str]
    feature_tree: List[str]
    reference_geometry: ReferenceGeometry
    mass_properties: Dict[str, float]
    interference_report: InterferenceReport
    clearance_report: ClearanceReport
    exported_files: List[ExportedFile]

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
