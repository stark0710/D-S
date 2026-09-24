"""
ReportBuilder Subsystem

Purpose:
    Defines the `ReportBuilder` class responsible for constructing `EngineeringReport` instances.

Role in Architecture:
    `ReportBuilder` implements the Builder Pattern to assemble `EngineeringReport` objects from title, summary,
    sections, collected artifacts, and applied templates.
"""

from uuid import uuid4
from datetime import datetime, timezone
from typing import Any
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.reports.report import EngineeringReport
from backend.design.studio.reports.report_section import ReportSection
from backend.design.studio.reports.report_template import ReportTemplate, EngineeringSummaryTemplate


class ReportBuilder:
    """
    Builder for assembling EngineeringReport instances.

    Design Principles:
        - Builder Pattern: Fluent chaining methods for constructing complex report documents.
    """

    def __init__(self) -> None:
        """Initializes the ReportBuilder."""
        self._report_id: str = f"REP-{uuid4().hex[:8].upper()}"
        self._title: str = "Aircraft Engineering Design Report"
        self._summary: str = ""
        self._sections: list[ReportSection] = []
        self._artifacts: list[EngineeringArtifact] = []
        self._template: ReportTemplate | None = None
        self._metadata: dict[str, Any] = {}

    def set_report_id(self, report_id: str) -> "ReportBuilder":
        """Sets explicit report ID."""
        self._report_id = report_id
        return self

    def set_title(self, title: str) -> "ReportBuilder":
        """Sets report main title."""
        self._title = title
        return self

    def set_summary(self, summary: str) -> "ReportBuilder":
        """Sets report executive summary."""
        self._summary = summary
        return self

    def add_section(self, section: ReportSection) -> "ReportBuilder":
        """Adds a individual ReportSection."""
        self._sections.append(section)
        return self

    def add_artifact(self, artifact: EngineeringArtifact) -> "ReportBuilder":
        """Adds an input EngineeringArtifact."""
        self._artifacts.append(artifact)
        return self

    def add_artifacts(self, artifacts: list[EngineeringArtifact]) -> "ReportBuilder":
        """Adds a list of input EngineeringArtifact objects."""
        self._artifacts.extend(artifacts)
        return self

    def apply_template(self, template: ReportTemplate) -> "ReportBuilder":
        """Applies a ReportTemplate to generate sections from collected artifacts."""
        self._template = template
        return self

    def build(self) -> EngineeringReport:
        """
        Builds and returns the final EngineeringReport instance.

        Returns:
            EngineeringReport: Built report instance.
        """
        final_sections: list[ReportSection] = list(self._sections)

        if self._template:
            template_sections = self._template.build_sections(self._artifacts)
            final_sections.extend(template_sections)
        elif not final_sections and self._artifacts:
            default_temp = EngineeringSummaryTemplate()
            final_sections = default_temp.build_sections(self._artifacts)

        # Sort sections by order
        final_sections.sort(key=lambda s: s.order)

        summary_text = self._summary
        if not summary_text:
            summary_text = f"Compiled engineering design report '{self._title}' containing {len(final_sections)} sections."

        return EngineeringReport(
            report_id=self._report_id,
            title=self._title,
            generated_at=datetime.now(timezone.utc).isoformat(),
            version="v1.0.0",
            sections=final_sections,
            summary=summary_text,
            metadata=self._metadata
        )
