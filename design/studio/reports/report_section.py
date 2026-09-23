"""
ReportSection Subsystem

Purpose:
    Defines the `ReportSection` domain model representing a structured section within an engineering report.

Role in Architecture:
    `ReportSection` encapsulates section title, display order integer, text content, attached artifacts, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReportSection:
    """
    Structured section within an EngineeringReport.

    Attributes:
        title (str): Section title string (e.g. '1. Mission & Requirements Summary').
        order (int): Display order index (1-based).
        content (str): Text / Markdown content string.
        artifacts (list[Any]): List of attached engineering artifacts or artifact IDs.
        metadata (dict[str, Any]): Additional section metadata.
    """

    title: str
    order: int
    content: str = ""
    artifacts: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
