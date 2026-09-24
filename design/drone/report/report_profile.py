# backend/design/drone/report/report_profile.py
"""Configuration profile for report generation.

In a full implementation this would hold settings such as which sections to
include, formatting options, and versioning details.  For now we provide a
lightweight dataclass that can be extended later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class ReportProfile:
    """Simple profile describing report generation preferences.

    Attributes
    ----------
    include_sections: List[str]
        Names of sections to be generated (e.g., "Executive Summary").
    version: str
        Report version string.
    revision: str
        Revision identifier (e.g., "A", "B").
    """

    include_sections: List[str] = field(default_factory=list)
    version: str = "1.0"
    revision: str = "A"
}
