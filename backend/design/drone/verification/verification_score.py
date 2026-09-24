"""
VerificationScore Subsystem

Purpose:
    Defines the `VerificationScore` domain model and verification confidence scoring service.

Role in Architecture:
    `VerificationScore` aggregates compliance, safety, reliability, and performance scores (0.0 to 100.0)
    and computes an overall weighted verification score.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationScore:
    """
    Multirotor mission verification score model.

    Attributes:
        overall_score (float): Composite verification score (0.0 to 100.0).
        mission_compliance_score (float): Mission objectives compliance score (0.0 to 100.0).
        performance_score (float): Flight performance compliance score (0.0 to 100.0).
        safety_score (float): Structural, electrical, and thrust safety margin score (0.0 to 100.0).
        reliability_score (float): Subsystem redundancy and fault tolerance score (0.0 to 100.0).
        metadata (dict[str, Any]): Additional scoring diagnostic metadata.
    """

    overall_score: float
    mission_compliance_score: float
    performance_score: float
    safety_score: float
    reliability_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VerificationScoreCalculator:
    """
    Scoring service for overall mission verification.

    Design Principles:
        - Single Responsibility Principle: Weighted composite verification score calculation only.
    """

    def calculate_score(
        self,
        mission_score: float,
        performance_score: float,
        safety_score: float,
        reliability_score: float
    ) -> VerificationScore:
        """
        Calculates weighted composite verification score.

        Weights:
            - Mission Compliance: 35%
            - Performance: 25%
            - Safety Margins: 25%
            - Reliability & Redundancy: 15%

        Args:
            mission_score (float): Mission score (0-100).
            performance_score (float): Performance score (0-100).
            safety_score (float): Safety score (0-100).
            reliability_score (float): Reliability score (0-100).

        Returns:
            VerificationScore: Computed score model.
        """
        overall = (
            (mission_score * 0.35) +
            (performance_score * 0.25) +
            (safety_score * 0.25) +
            (reliability_score * 0.15)
        )

        return VerificationScore(
            overall_score=round(overall, 1),
            mission_compliance_score=round(mission_score, 1),
            performance_score=round(performance_score, 1),
            safety_score=round(safety_score, 1),
            reliability_score=round(reliability_score, 1)
        )
