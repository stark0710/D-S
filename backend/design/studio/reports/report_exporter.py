"""
ReportExporter Subsystem

Purpose:
    Defines the abstract `ReportExporter` interface and concrete exporters (JSON, Markdown, HTML).

Role in Architecture:
    `ReportExporter` converts an `EngineeringReport` into external publication format strings (JSON, Markdown, HTML).
"""

import json
from abc import ABC, abstractmethod
from typing import Any
from backend.design.studio.reports.report import EngineeringReport


class ReportExporter(ABC):
    """
    Abstract interface for report format exporters.
    """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Name of the export format (e.g. 'JSON', 'Markdown', 'HTML')."""
        pass

    @abstractmethod
    def export(self, report: EngineeringReport) -> str:
        """
        Exports the EngineeringReport into format string.

        Args:
            report (EngineeringReport): Input report instance.

        Returns:
            str: Exported format string content.
        """
        pass


class JSONReportExporter(ReportExporter):
    """JSON format exporter."""

    @property
    def format_name(self) -> str:
        return "JSON"

    def export(self, report: EngineeringReport) -> str:
        d = {
            "report_id": report.report_id,
            "title": report.title,
            "generated_at": report.generated_at,
            "version": report.version,
            "summary": report.summary,
            "sections": [
                {
                    "title": s.title,
                    "order": s.order,
                    "content": s.content,
                    "artifact_count": len(s.artifacts),
                }
                for s in report.sections
            ],
            "metadata": report.metadata,
        }
        return json.dumps(d, indent=2)


class MarkdownReportExporter(ReportExporter):
    """Markdown format exporter."""

    @property
    def format_name(self) -> str:
        return "Markdown"

    def export(self, report: EngineeringReport) -> str:
        lines: list[str] = []
        lines.append(f"# {report.title}")
        lines.append(f"**Report ID:** {report.report_id} | **Generated At:** {report.generated_at} | **Version:** {report.version}\n")
        lines.append(f"## Executive Summary\n{report.summary}\n")

        for sec in report.sections:
            lines.append(f"## {sec.title}\n")
            lines.append(f"{sec.content}\n")
            if sec.artifacts:
                lines.append(f"*Attached Artifacts:* {len(sec.artifacts)} artifact(s) attached.\n")

        return "\n".join(lines)


class HTMLReportExporter(ReportExporter):
    """HTML format exporter."""

    @property
    def format_name(self) -> str:
        return "HTML"

    def export(self, report: EngineeringReport) -> str:
        lines: list[str] = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"  <title>{report.title}</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }",
            "    h1 { color: #1a365d; }",
            "    h2 { color: #2b6cb0; margin-top: 24px; }",
            "    .meta { font-size: 0.9em; color: #718096; margin-bottom: 20px; }",
            "    .summary { background: #edf2f7; padding: 15px; border-radius: 6px; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{report.title}</h1>",
            f'  <div class="meta">Report ID: {report.report_id} | Generated: {report.generated_at}</div>',
            f'  <div class="summary"><h3>Executive Summary</h3><p>{report.summary}</p></div>',
        ]

        for sec in report.sections:
            lines.append(f"  <h2>{sec.title}</h2>")
            lines.append(f"  <p>{sec.content}</p>")

        lines.append("</body>")
        lines.append("</html>")
        return "\n".join(lines)
