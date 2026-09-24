"""
ReportPipeline Subsystem

Purpose:
    Defines the `ReportPipeline` class responsible for orchestrating report building, validation, and export execution.

Role in Architecture:
    `ReportPipeline` coordinates `ReportBuilder`, `ReportValidator`, and `ReportExporter` to produce a validated exported report.
"""

from typing import Any
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.reports.report import EngineeringReport
from backend.design.studio.reports.report_builder import ReportBuilder
from backend.design.studio.reports.report_validator import ReportValidator
from backend.design.studio.reports.report_template import ReportTemplate
from backend.design.studio.reports.report_exporter import (
    ReportExporter,
    MarkdownReportExporter,
    JSONReportExporter,
    HTMLReportExporter,
)


class ReportPipeline:
    """
    Pipeline for orchestrating report generation, validation, and export.

    Design Principles:
        - Pipeline Pattern: Sequential execution of report building, validation, and formatting.
    """

    def __init__(
        self,
        validator: ReportValidator | None = None,
        exporters: dict[str, ReportExporter] | None = None
    ) -> None:
        """
        Initializes the ReportPipeline.

        Args:
            validator (ReportValidator | None): Injected report validator.
            exporters (dict[str, ReportExporter] | None): Map of format_name -> exporter.
        """
        self._validator: ReportValidator = validator if validator else ReportValidator()
        self._exporters: dict[str, ReportExporter] = exporters if exporters else {
            "MARKDOWN": MarkdownReportExporter(),
            "JSON": JSONReportExporter(),
            "HTML": HTMLReportExporter(),
        }

    def execute(
        self,
        artifacts: list[EngineeringArtifact],
        template: ReportTemplate | None = None,
        title: str = "Aircraft Engineering Design Report",
        summary: str = "",
        export_format: str = "MARKDOWN"
    ) -> tuple[EngineeringReport, str]:
        """
        Executes report pipeline workflow.

        Args:
            artifacts (list[EngineeringArtifact]): Input engineering artifacts.
            template (ReportTemplate | None): Optional layout template.
            title (str): Main report title.
            summary (str): Executive summary string.
            export_format (str): Desired export format ('MARKDOWN', 'JSON', 'HTML').

        Returns:
            tuple[EngineeringReport, str]: Tuple of (built & validated EngineeringReport, exported formatted string).
        """
        builder = ReportBuilder()
        builder.set_title(title)
        builder.set_summary(summary)
        builder.add_artifacts(artifacts)

        if template:
            builder.apply_template(template)

        report = builder.build()

        # Validate
        self._validator.validate(report)

        # Export
        fmt_key = export_format.upper()
        exporter = self._exporters.get(fmt_key, MarkdownReportExporter())
        exported_str = exporter.export(report)

        return report, exported_str
