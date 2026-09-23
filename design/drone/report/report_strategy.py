# backend/design/drone/report/report_strategy.py
"""Abstract base class for report generation strategies.

Each strategy knows how to assemble a full ReportResult given the various
engineering result objects.  Concrete strategies (executive, technical, …)
will implement the `build_report` method.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .report_result import ReportResult


class ReportStrategy(ABC):
    """Strategy interface for building a drone engineering report.

    Implementations should gather the required data from the snapshot and
    populate a :class:`ReportResult` instance.
    """

    @abstractmethod
    def build_report(self, snapshot: Any) -> ReportResult:
        """Construct a :class:`ReportResult` from the supplied snapshot.

        Parameters
        ----------
        snapshot: Any
            An object that aggregates all engineering results (see architecture).
        """
        raise NotImplementedError
