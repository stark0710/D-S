"""
ReportRegistry Subsystem

Purpose:
    Defines the `ReportRegistry` class responsible for registering and managing report templates and exporters.

Role in Architecture:
    `ReportRegistry` provides the plugin registry for report templates and format exporters.
"""

from backend.design.studio.reports.report_template import ReportTemplate
from backend.design.studio.reports.report_exporter import ReportExporter


class ReportRegistry:
    """
    Registry for managing report templates and exporters.

    Design Principles:
        - Registry Pattern: Centralized lookup for templates and format exporters.
        - Open/Closed Principle: Plugin extension mechanism for new templates/exporters.
    """

    def __init__(self) -> None:
        """Initializes the ReportRegistry."""
        self._templates: dict[str, ReportTemplate] = {}
        self._exporters: dict[str, ReportExporter] = {}

    def register_template(self, template: ReportTemplate) -> None:
        """Registers a ReportTemplate."""
        self._templates[template.template_name] = template

    def get_template(self, template_name: str) -> ReportTemplate:
        """Retrieves a ReportTemplate by name."""
        if template_name not in self._templates:
            raise KeyError(f"ReportTemplate '{template_name}' is not registered.")
        return self._templates[template_name]

    def register_exporter(self, exporter: ReportExporter) -> None:
        """Registers a ReportExporter."""
        self._exporters[exporter.format_name.upper()] = exporter

    def get_exporter(self, format_name: str) -> ReportExporter:
        """Retrieves a ReportExporter by format name (JSON, Markdown, HTML)."""
        fmt = format_name.upper()
        if fmt not in self._exporters:
            raise KeyError(f"ReportExporter for format '{format_name}' is not registered.")
        return self._exporters[fmt]
