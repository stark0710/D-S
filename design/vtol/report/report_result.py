from dataclasses import dataclass, field
from typing import Any, Dict, List

from .executive_summary_generator import ExecutiveSummary
from .engineering_section_generator import EngineeringSection
from .performance_section_generator import PerformanceSection
from .verification_section_generator import VerificationSection
from .optimization_section_generator import OptimizationSection
from .cad_section_generator import CADSection
from .manufacturing_section_generator import ManufacturingSection
from .appendix_generator import Appendix
from .report_exporter import ExportedDocument

@dataclass(slots=True)
class ReportResult:
    """
    Consolidated outputs of the VTOL Engineering Report Framework.
    """
    executive_summary: ExecutiveSummary
    engineering_sections: List[EngineeringSection]
    performance_sections: List[PerformanceSection]
    verification_sections: List[VerificationSection]
    optimization_sections: List[OptimizationSection]
    cad_sections: List[CADSection]
    manufacturing_sections: List[ManufacturingSection]
    appendices: List[Appendix]
    exported_documents: List[ExportedDocument]

    traceability_matrix: Dict[str, str] = field(default_factory=dict)
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
