"""
Fixed-Wing Engineering Report Result Subsystem

Purpose:
    Defines the `ReportResult` class representing the output of the Engineering Report Framework.

Role in Architecture:
    `ReportResult` carries maps of sections, rendered content strings, exported PDF/Markdown paths, and engineering stats.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(slots=True)
class ReportResult:
    """
    Consolidated output of the engineering report generation workflow.

    Attributes:
        executive_summary (str): Sized overall executive summary.
        report_sections (Dict[str, str]): Map of chapter names to text contents.
        generated_reports (Dict[str, Any]): Rendered layout data.
        exported_files (Dict[str, str]): Map of document formats to absolute local file paths.
        engineering_statistics (Dict[str, Any]): Sizing summary stats (aspect ratios, static margin, MTOW).
        recommendations (List[str]): Sizing recommendations.
        warnings (List[str]): Sizing warnings.
        metadata (Dict[str, Any]): Authorship and timestamps.
    """

    executive_summary: str
    report_sections: Dict[str, str]
    generated_reports: Dict[str, Any]
    exported_files: Dict[str, str]
    engineering_statistics: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Engineering Report Result model.
"""
