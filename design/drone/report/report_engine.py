# backend/design/drone/report/report_engine.py
"""High‑level orchestrator for generating drone engineering reports.

The :class:`ReportEngine` selects a strategy, builds the report, validates it
and finally delegates export to :class:`ExportManager`.

Typical usage::

    engine = ReportEngine()
    result = engine.generate(
        snapshot=my_snapshot,
        strategy_name="executive",
        export_formats=["markdown", "pdf"]
    )

"""

from __future__ import annotations

from typing import List, Any

from .report_registry import ReportStrategyRegistry
from .report_builder import ReportBuilder
from .report_validator import ReportValidator
from .export_manager import ExportManager
from .report_result import ReportResult


class ReportEngine:
    """Facade class that drives the report generation pipeline.

    It performs three main steps:
    1. **Strategy selection** – retrieve a concrete ``ReportStrategy``.
    2. **Build** – use :class:`ReportBuilder` to collect all sections.
    3. **Validate** – run :class:`ReportValidator` checks.
    4. **Export** – produce files in the requested formats.
    """

    def __init__(self) -> None:
        self._validator = ReportValidator()
        self._exporter = ExportManager()

    def generate(
        self,
        snapshot: Any,
        strategy_name: str = "executive",
        export_formats: List[str] | None = None,
    ) -> ReportResult:
        """Generate a complete report.

        Parameters
        ----------
        snapshot: Any
            Aggregated engineering results (see architecture docs).
        strategy_name: str, optional
            Name of the registered strategy. Defaults to ``"executive"``.
        export_formats: list[str] | None, optional
            Desired output formats – e.g. ``["markdown", "pdf"]``. If ``None``
            only the in‑memory representation is returned.
        """
        # 1. Strategy selection
        strategy = ReportStrategyRegistry.get(strategy_name)

        # 2. Build the report using a builder helper (handles common sections)
        builder = ReportBuilder(strategy)
        result: ReportResult = builder.build(snapshot)

        # 3. Validation – raise if any critical issue is found
        self._validator.validate(result)

        # 4. Export if formats were requested
        if export_formats:
            self._exporter.export(result, export_formats)

        return result
