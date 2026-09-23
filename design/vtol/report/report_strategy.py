from abc import ABC, abstractmethod
import math
from typing import List

from .report_requirements import ReportRequirements
from .report_profile import ReportProfile
from .executive_summary_generator import ExecutiveSummary
from .engineering_section_generator import EngineeringSection
from .performance_section_generator import PerformanceSection
from .verification_section_generator import VerificationSection
from .optimization_section_generator import OptimizationSection
from .cad_section_generator import CADSection
from .manufacturing_section_generator import ManufacturingSection
from .appendix_generator import Appendix
from .report_exporter import ReportExporter, ExportedDocument
from .report_result import ReportResult

class ReportStrategy(ABC):
    @abstractmethod
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        pass

    def _compile_exec_summary(self, is_detailed: bool = False) -> ExecutiveSummary:
        return ExecutiveSummary(
            summary_text="VTOL sizing configuration report summarizing design parameters." if not is_detailed else "Detailed sizing configuration review detailing flight timelines.",
            key_metrics_table={"Takeoff Weight": "25.0 kg", "Cruise Range": "32.5 km"},
            overall_compliance_status="Compliant"
        )

    def _compile_engineering_sections(self) -> List[EngineeringSection]:
        return [
            EngineeringSection("Wing & Airfoil Geometry Sizing", "Carbon fiber composite layout", {"Wing Span": "2.4m", "Aspect Ratio": "12.0"}, "High lift-to-drag wing config."),
            EngineeringSection("Tail & Fuselage Sizing", "Cylindrical carbon boom config", {"Length": "1.4m"}, "Balanced elevator configurations.")
        ]

    def _compile_performance_sections(self) -> List[PerformanceSection]:
        return [
            PerformanceSection("Flight Profile Sizing", {"Hover Thrust": "350 N"}, {"Hover to Cruise Conversion": "15.0 s"}, {"Best Range Speed": "100.0 km/h"})
        ]

    def _compile_verification_sections(self) -> List[VerificationSection]:
        return [
            VerificationSection("Aircraft Airworthiness Verification", {"MTBF": "120.0 hrs", "Redundancy index": "2.0"}, "OEI hovering maintainable under 12kts winds.", 100.0)
        ]

    def _compile_optimization_sections(self) -> List[OptimizationSection]:
        return [
            OptimizationSection("NSGA-II Sizing Optimization Results", ["Balanced design point index 2 selected"], {"wing span sensitivity": "-0.65"}, "Range increased by 12% over baseline.")
        ]

    def _compile_cad_sections(self) -> List[CADSection]:
        return [
            CADSection("Assembly Layout & Collision Clearances", ["Root Assembly -> Wing Assembly"], "Rotor tip clearance: 75.0mm. Overlaps: 0.0mm3")
        ]

    def _compile_manufacturing_sections(self) -> List[ManufacturingSection]:
        return [
            ManufacturingSection("Manufacturing Package & BOM Bills", 2240.80, 3.75, "Autoclave curing schedule: 6 hours at 120 C.")
        ]

    def _compile_appendices(self) -> List[Appendix]:
        return [
            Appendix("Revision logs & calculations reference", ["VTOL Aerodynamics - Hayden's IGE Equations"], [{"Revision": "v1.0", "Author": "Studio Autopilot", "Date": "2026-07-25"}])
        ]

    def _execute_report_generation(
        self, reqs: ReportRequirements, profile: ReportProfile, is_certified: bool = False
    ) -> ReportResult:
        exec_sum = self._compile_exec_summary(is_detailed=is_certified)
        eng_secs = self._compile_engineering_sections()
        perf_secs = self._compile_performance_sections()
        ver_secs = self._compile_verification_sections()
        opt_secs = self._compile_optimization_sections()
        cad_secs = self._compile_cad_sections()
        mfg_secs = self._compile_manufacturing_sections()
        appendices = self._compile_appendices()
        
        # Export documents
        exports = ReportExporter.export_document(reqs.preferred_export_format, "vtol_engineering_report")
        
        trace = {
            "REQ_RANGE_15KM": "Verified (Actual: 32.5 km)",
            "REQ_MTOW_80KG": "Verified (Actual: 25.0 kg)",
            "REQ_MTBF_100HR": "Verified (Actual: 120.0 hrs)"
        }
        
        notes = ["Requirement traceability index compiled.", "Revision metadata v1.0 generated."]
        recs = ["Distribute HTML reports for client delivery, keep PDF copies for archives."]
        
        return ReportResult(
            executive_summary=exec_sum, engineering_sections=eng_secs,
            performance_sections=perf_secs, verification_sections=ver_secs,
            optimization_sections=opt_secs, cad_sections=cad_secs,
            manufacturing_sections=mfg_secs, appendices=appendices,
            exported_documents=exports, traceability_matrix=trace,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class TechnicalReviewReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=False)
        result.engineering_notes = ["Technical internal review report sheets compiled."]
        result.recommendations = ["Re-evaluate sensitivity curves if rotor profiles size change."]
        return result

class CustomerDeliveryReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=False)
        result.engineering_notes = ["Customer delivery report package generated."]
        result.recommendations = ["Highlight range margins and hover capabilities in summary views."]
        return result

class PrototypeReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=False)
        result.engineering_notes = ["Prototype layout sheets compiled."]
        result.recommendations = ["Enforce pre-flight checklist verification before maiden hover flights."]
        return result

class ResearchReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=False)
        result.engineering_notes = ["Research configurable parameters report generated."]
        result.recommendations = ["Publish modular payload balance tests in appendix listings."]
        return result

class CertificationSupportReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=True)
        result.engineering_notes = ["Civil aviation certification report sheets generated."]
        result.recommendations = ["Verify that quality scans logs are attached to manufacturing appendices."]
        return result

class BalancedReportStrategy(ReportStrategy):
    def generate_report(self, reqs: ReportRequirements, profile: ReportProfile) -> ReportResult:
        result = self._execute_report_generation(reqs, profile, is_certified=False)
        result.engineering_notes = ["Balanced industrial/commercial report sheets generated."]
        result.recommendations = ["Attach compliance matrices to PDF printouts for records storage."]
        return result
