"""
ScoreBreakdown Subsystem

Purpose:
    Defines the `ScoreBreakdown` domain model representing evaluation details for a single category score.

Role in Architecture:
    `ScoreBreakdown` carries the raw score, assigned weight, calculated weighted score, maximum achievable score, and comments for a category.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.scoring.score_category import ScoreCategory


@dataclass(slots=True)
class ScoreBreakdown:
    """
    Evaluation breakdown for a single scoring category.

    Attributes:
        category (ScoreCategory): Target scoring category.
        raw_score (float): Unweighted category match score from 0.0 to 1.0.
        weighted_score (float): Calculated weighted score (raw_score * weight).
        maximum_score (float): Maximum achievable score (equal to assigned weight).
        comments (str): Explanatory evaluation comments or notes.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    category: ScoreCategory
    raw_score: float
    weighted_score: float
    maximum_score: float
    comments: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
