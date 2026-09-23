"""
VerificationConstraints Subsystem

Purpose:
    Defines the `VerificationConstraints` domain model representing verification design constraints.

Role in Architecture:
    `VerificationConstraints` specifies maximum allowed failed requirements limit (default 0),
    max allowable risk rating, and strict safety limits.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationConstraints:
    """
    Multirotor mission verification design constraints.

    Attributes:
        max_failed_requirements (int): Maximum number of failed requirements allowed for marginal status (default 0).
        require_zero_critical_failures (bool): True if zero critical safety/power failures are strictly required.
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_failed_requirements: int = 0
    require_zero_critical_failures: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
