"""
Fixed-Wing Engineering Report Framework Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Engineering Report Framework.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements
from backend.design.fixed_wing.report.report_profile import ReportProfile
from backend.design.fixed_wing.report.report_constraints import ReportConstraints
from backend.design.fixed_wing.report.report_result import ReportResult
from backend.design.fixed_wing.report.report_validator import ReportValidator, ReportValidationError
from backend.design.fixed_wing.report.report_renderer import ReportRenderer
from backend.design.fixed_wing.report.pdf_export import PDFExport
from backend.design.fixed_wing.report.html_export import HTMLExport
from backend.design.fixed_wing.report.markdown_export import MarkdownExport
from backend.design.fixed_wing.report.executive_summary import ExecutiveSummaryCompiler
from backend.design.fixed_wing.report.mission_section import MissionSectionCompiler
from backend.design.fixed_wing.report.configuration_section import ConfigurationSectionCompiler
from backend.design.fixed_wing.report.geometry_section import GeometrySectionCompiler
from backend.design.fixed_wing.report.propulsion_section import PropulsionSectionCompiler
from backend.design.fixed_wing.report.electrical_section import ElectricalSectionCompiler
from backend.design.fixed_wing.report.avionics_section import AvionicsSectionCompiler
from backend.design.fixed_wing.report.payload_section import PayloadSectionCompiler
from backend.design.fixed_wing.report.mass_properties_section import MassPropertiesSectionCompiler
from backend.design.fixed_wing.report.flight_performance_section import FlightPerformanceSectionCompiler
from backend.design.fixed_wing.report.verification_section import VerificationSectionCompiler
from backend.design.fixed_wing.report.optimization_section import OptimizationSectionCompiler
from backend.design.fixed_wing.report.cad_section import CADSectionCompiler
from backend.design.fixed_wing.report.manufacturing_section import ManufacturingSectionCompiler
from backend.design.fixed_wing.report.appendix_section import AppendixSectionCompiler
from backend.design.fixed_wing.report.report_strategy import ReportStrategy
from backend.design.fixed_wing.report.report_registry import ReportStrategyRegistry
from backend.design.fixed_wing.report.report_engine import ReportEngine

__all__ = [
    "ReportRequirements",
    "ReportProfile",
    "ReportConstraints",
    "ReportResult",
    "ReportValidator",
    "ReportValidationError",
    "ReportRenderer",
    "PDFExport",
    "HTMLExport",
    "MarkdownExport",
    "ExecutiveSummaryCompiler",
    "MissionSectionCompiler",
    "ConfigurationSectionCompiler",
    "GeometrySectionCompiler",
    "PropulsionSectionCompiler",
    "ElectricalSectionCompiler",
    "AvionicsSectionCompiler",
    "PayloadSectionCompiler",
    "MassPropertiesSectionCompiler",
    "FlightPerformanceSectionCompiler",
    "VerificationSectionCompiler",
    "OptimizationSectionCompiler",
    "CADSectionCompiler",
    "ManufacturingSectionCompiler",
    "AppendixSectionCompiler",
    "ReportStrategy",
    "ReportStrategyRegistry",
    "ReportEngine",
]
