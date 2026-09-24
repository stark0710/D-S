"""
VerificationProfile Subsystem

Purpose:
    Defines the `VerificationProfile` domain model representing aircraft verification metrics summary.

Role in Architecture:
    `VerificationProfile` encapsulates overall status ('PASSED', 'MARGINAL', 'FAILED'), composite score,
    passed requirements list, and failed requirements list.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationProfile:
    """
    Multirotor mission verification profile definition.

    Attributes:
        overall_status (str): Overall verification readiness status ('PASSED', 'MARGINAL', 'FAILED').
        composite_score (float): Composite verification confidence score (0.0 to 100.0).
        passed_requirements (list[str]): List of satisfied requirements.
        failed_requirements (list[str]): List of unsatisfied requirements.
        metadata (dict[str, Any]): Additional profile metadata.
    """

    overall_status: str
    composite_score: float
    passed_requirements: list[str] = field(default_factory=list)
    failed_requirements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
