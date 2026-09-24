"""
EngineeringScore Subsystem

Purpose:
    Defines the `EngineeringScore` domain model representing the aggregated quantitative score of an aircraft design.

Role in Architecture:
    `EngineeringScore` encapsulates the overall normalized engineering score (0.0 to 1.0), category breakdowns,
    identified design strengths, weaknesses, and improvement recommendations.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.scoring.score_breakdown import ScoreBreakdown


@dataclass(slots=True)
class EngineeringScore:
    """
    Aggregated quantitative engineering score summary.

    Attributes:
        overall_score (float): Normalized overall engineering quality score from 0.0 (poor) to 1.0 (optimal).
        score_breakdown (list[ScoreBreakdown]): List of category score breakdown objects.
        strengths (list[str]): Key high-performing engineering aspects.
        weaknesses (list[str]): Sub-optimal engineering trade-offs.
        recommendations (list[str]): Corrective design optimization recommendations.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    overall_score: float
    score_breakdown: list[ScoreBreakdown] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
