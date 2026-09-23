"""
Fixed-Wing Engineering Report Constraints Subsystem

Purpose:
    Defines the `ReportConstraints` class.

Role in Architecture:
    `ReportConstraints` restricts reporting output formats.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class ReportConstraints:
    """
    Constraints restricting generated report file types.

    Attributes:
        allowed_formats (List[str]): List of active export formats allowed by user.
        min_required_sections (int): Limit on required core chapters.
    """

    allowed_formats: List[str] = field(
        default_factory=lambda: ["PDF", "HTML", "MARKDOWN", "JSON", "ARCHIVE"]
    )
    min_required_sections: int = 5
