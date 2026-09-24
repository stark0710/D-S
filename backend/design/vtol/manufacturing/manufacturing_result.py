from dataclasses import dataclass, field
from typing import Any, Dict, List

from .bom_generator import BillOfMaterials
from .assembly_instruction_generator import AssemblyInstructions
from .process_plan_generator import ManufacturingProcessPlan
from .tooling_generator import ToolingPlan
from .fixture_generator import FixturePlan
from .quality_plan_generator import QualityPlan
from .inspection_plan_generator import InspectionPlan
from .cost_estimation import ProductionCostEstimate
from .production_analysis import ManufacturabilityAssessment

@dataclass(slots=True)
class ManufacturingResult:
    """
    Consolidated outputs of the VTOL Manufacturing Package Framework.
    """
    bill_of_materials: BillOfMaterials
    assembly_instructions: AssemblyInstructions
    process_plan: ManufacturingProcessPlan
    tooling_plan: ToolingPlan
    fixture_plan: FixturePlan
    quality_plan: QualityPlan
    inspection_plan: InspectionPlan
    production_cost: ProductionCostEstimate
    production_timeline: Dict[str, float]
    manufacturability_assessment: ManufacturabilityAssessment

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
