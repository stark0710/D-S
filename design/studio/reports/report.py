"""
EngineeringReport Subsystem

Purpose:
    Defines the `EngineeringReport` domain model representing a compiled engineering report.

Role in Architecture:
    `EngineeringReport` encapsulates report ID, title, ISO 8601 generation timestamp, version,
    ordered `ReportSection` list, summary text, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.studio.reports.report_section import ReportSection


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class EngineeringReport:
    """
    Compiled engineering report summary.

    Attributes:
        report_id (str): Unique report identifier.
        title (str): Main report title string.
        generated_at (str): ISO 8601 generation timestamp string.
        version (str): Report format version string.
        sections (list[ReportSection]): Ordered list of report sections.
        summary (str): High-level executive summary text.
        metadata (dict[str, Any]): Additional report diagnostic metadata.
    """

    report_id: str
    title: str
    generated_at: str = field(default_factory=_current_timestamp)
    version: str = "v1.0.0"
    sections: list[ReportSection] = field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
