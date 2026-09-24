# backend/design/drone/report/__init__.py
"""Top-level package for the Drone Engineering Report Framework.

Exports the main public API:
- ReportEngine: orchestrates report generation.
- ReportResult: dataclass representing a generated report.
- ReportStrategyRegistry: registry for report strategies.
"""

from .report_engine import ReportEngine
from .report_result import ReportResult
from .report_registry import ReportStrategyRegistry

__all__ = [
    "ReportEngine",
    "ReportResult",
    "ReportStrategyRegistry",
]
