"""
VerificationRequirements Subsystem

Purpose:
    Defines the `VerificationRequirements` domain model representing input requirements for verification engineering.

Role in Architecture:
    `VerificationRequirements` specifies target verification confidence score (default 80.0), required safety factor,
    and required reliability rating score.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationRequirements:
    """
    Multirotor mission verification requirements model.

    Attributes:
        min_verification_score (float): Minimum composite score threshold for flight approval (default 80.0).
        min_safety_factor (float): Minimum structural safety factor requirement (default 1.5).
        min_reliability_score (float): Minimum subsystem reliability rating score (default 70.0).
        metadata (dict[str, Any]): Additional requirements metadata.
    """

    min_verification_score: float = 80.0
    min_safety_factor: float = 1.5
    min_reliability_score: float = 70.0
    metadata: dict[str, Any] = field(default_factory=dict)
