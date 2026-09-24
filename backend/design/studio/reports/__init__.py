"""
Reports package for Torq Wings Design Studio Phase 5.3 Universal Engineering Design Report Framework.
"""

from backend.design.studio.reports.report_section import ReportSection
from backend.design.studio.reports.report import EngineeringReport
from backend.design.studio.reports.report_template import (
    ReportTemplate,
    DroneReportTemplate,
    FixedWingReportTemplate,
    VTOLReportTemplate,
    EngineeringSummaryTemplate,
)
from backend.design.studio.reports.report_builder import ReportBuilder
from backend.design.studio.reports.report_validator import ReportValidator, ReportValidationError
from backend.design.studio.reports.report_exporter import (
    ReportExporter,
    JSONReportExporter,
    MarkdownReportExporter,
    HTMLReportExporter,
)
from backend.design.studio.reports.report_registry import ReportRegistry
from backend.design.studio.reports.report_pipeline import ReportPipeline
from backend.design.studio.reports.report_generator import ReportGenerator

__all__ = [
    "ReportSection",
    "EngineeringReport",
    "ReportTemplate",
    "DroneReportTemplate",
    "FixedWingReportTemplate",
    "VTOLReportTemplate",
    "EngineeringSummaryTemplate",
    "ReportBuilder",
    "ReportValidator",
    "ReportValidationError",
    "ReportExporter",
    "JSONReportExporter",
    "MarkdownReportExporter",
    "HTMLReportExporter",
    "ReportRegistry",
    "ReportPipeline",
    "ReportGenerator",
]
