"""
ReportGenerator Subsystem

Purpose:
    Defines the `ReportGenerator` class, which serves as the public entry point for generating engineering reports from DesignContext.

Role in Architecture:
    `ReportGenerator` receives a `DesignContext` and list of artifacts, resolves layout template from `ReportRegistry`,
    and executes a `ReportPipeline` to return a compiled `EngineeringReport` and formatted document content.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.reports.report import EngineeringReport
from backend.design.studio.reports.report_registry import ReportRegistry
from backend.design.studio.reports.report_pipeline import ReportPipeline
from backend.design.studio.reports.report_template import (
    DroneReportTemplate,
    FixedWingReportTemplate,
    VTOLReportTemplate,
    EngineeringSummaryTemplate,
)


class ReportGenerator:
    """
    Public entry point service for generating engineering design reports.

    Design Principles:
        - Single Responsibility Principle: Report generation orchestration only.
        - Dependency Injection: Injects `ReportRegistry` and `ReportPipeline` collaborators.
        - Non-Calculation: Performs no engineering calculations; only transforms artifacts into reports.
    """

    def __init__(
        self,
        registry: ReportRegistry | None = None,
        pipeline: ReportPipeline | None = None
    ) -> None:
        """
        Initializes the ReportGenerator.

        Args:
            registry (ReportRegistry | None): Injected report registry instance.
            pipeline (ReportPipeline | None): Injected report pipeline instance.
        """
        if registry is None:
            registry = ReportRegistry()
            registry.register_template(DroneReportTemplate())
            registry.register_template(FixedWingReportTemplate())
            registry.register_template(VTOLReportTemplate())
            registry.register_template(EngineeringSummaryTemplate())

        self._registry: ReportRegistry = registry
        self._pipeline: ReportPipeline = pipeline if pipeline else ReportPipeline()

    def generate_report(
        self,
        context: DesignContext,
        artifacts: list[EngineeringArtifact],
        template_name: str = "DroneReportTemplate",
        title: str = "Aircraft Engineering Design Report",
        export_format: str = "MARKDOWN"
    ) -> tuple[EngineeringReport, str]:
        """
        Generates an EngineeringReport from collected artifacts and context.

        Args:
            context (DesignContext): Input design context.
            artifacts (list[EngineeringArtifact]): Input engineering artifacts.
            template_name (str): Identifier name of registered ReportTemplate.
            title (str): Main report title string.
            export_format (str): Desired export format ('MARKDOWN', 'JSON', 'HTML').

        Returns:
            tuple[EngineeringReport, str]: Tuple of (compiled EngineeringReport, exported formatted document string).
        """
        template = self._registry.get_template(template_name)
        summary = f"Compiled engineering design report for {context.requirement_model.mission_type.value} mission."

        return self._pipeline.execute(
            artifacts=artifacts,
            template=template,
            title=title,
            summary=summary,
            export_format=export_format
        )
