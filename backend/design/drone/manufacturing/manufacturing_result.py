"""
ManufacturingResult Subsystem

Purpose:
    Defines the `ManufacturingResult` domain model representing output from the Drone Manufacturing Package Engineering Framework.

Role in Architecture:
    `ManufacturingResult` encapsulates `bill_of_materials` (`BillOfMaterials`), `procurement_list` (`ProcurementList`),
    `assembly_plan` (`AssemblyPlan`), `fabrication_plan` (`FabricationPlan`), `quality_plan` (`QualityPlan`),
    `inspection_plan` (`InspectionPlan`), `packaging_plan` (`PackagingPlan`), generated document mapping,
    engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.manufacturing.bill_of_materials import BillOfMaterials
from backend.design.drone.manufacturing.procurement_list import ProcurementList
from backend.design.drone.manufacturing.assembly_plan import AssemblyPlan
from backend.design.drone.manufacturing.fabrication_plan import FabricationPlan
from backend.design.drone.manufacturing.quality_plan import QualityPlan
from backend.design.drone.manufacturing.inspection_plan import InspectionPlan
from backend.design.drone.manufacturing.packaging_plan import PackagingPlan


@dataclass(slots=True)
class ManufacturingResult:
    """
    Multirotor manufacturing package engineering output summary.

    Attributes:
        bill_of_materials (BillOfMaterials): Detailed Bill of Materials catalog model.
        procurement_list (ProcurementList): Sourcing procurement tracking list model.
        assembly_plan (AssemblyPlan): Subassembly sequence and tools guidelines model.
        fabrication_plan (FabricationPlan): Custom fabrication (laser/CNC/3D print) guidelines model.
        quality_plan (QualityPlan): Pre-shipment Quality Assurance testing limits model.
        inspection_plan (InspectionPlan): Assembly verification checklist model.
        packaging_plan (PackagingPlan): Shipping box transport packaging guidelines model.
        generated_documents (dict[str, Any]): Text content mapping of generated manuals/checklists.
        engineering_notes (str): Summary notes and technical rationale.
        warnings (list[str]): Diagnostic warnings generated during manufacturing evaluation.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    bill_of_materials: BillOfMaterials
    procurement_list: ProcurementList
    assembly_plan: AssemblyPlan
    fabrication_plan: FabricationPlan
    quality_plan: QualityPlan
    inspection_plan: InspectionPlan
    packaging_plan: PackagingPlan
    generated_documents: dict[str, Any] = field(default_factory=dict)
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
PostProcessFinished = True
