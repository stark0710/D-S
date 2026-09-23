# backend/design/drone/report/report_result.py
"""Data model representing the final engineering report.

The model follows the specification in the architecture documents and uses
`@dataclass(slots=True)` for memory efficiency and immutability where possible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass(slots=True)
class ReportResult:
    """Container for all generated report artifacts.

    Attributes
    ----------
    report: str
        The full report content in the primary format (e.g., Markdown).
    executive_summary: str
        Executive summary section.
    technical_sections: Dict[str, str]
        Mapping of technical section names to their rendered content.
    appendices: List[str]
        List of appendix contents.
    generated_files: Dict[str, str]
        Mapping of file format to file path of the exported report.
    report_metadata: Dict[str, Any]
        Metadata such as version, timestamp, revision, and source traceability.
    engineering_notes: List[str]
        Free‑form notes collected during generation.
    warnings: List[str]
        Any non‑critical warnings raised during generation/validation.
    """

    report: str = ""
    executive_summary: str = ""
    technical_sections: Dict[str, str] = field(default_factory=dict)
    appendices: List[str] = field(default_factory=list)
    generated_files: Dict[str, str] = field(default_factory=dict)
    report_metadata: Dict[str, Any] = field(default_factory=dict)
    engineering_notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_section(self, name: str, content: str) -> None:
        """Add a technical section to the report.

        Parameters
        ----------
        name: str
            Section identifier, e.g., "Structural Engineering".
        content: str
            Rendered markdown/HTML for the section.
        """
        self.technical_sections[name] = content

    def add_appendix(self, content: str) -> None:
        self.appendices.append(content)

    def add_generated_file(self, fmt: str, path: str) -> None:
        self.generated_files[fmt] = path

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def add_note(self, note: str) -> None:
        self.engineering_notes.append(note)

    def set_metadata(self, **kwargs: Any) -> None:
        """Update the metadata dictionary with provided key/value pairs."""
        self.report_metadata.update(kwargs)
