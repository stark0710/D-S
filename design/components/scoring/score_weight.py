"""
ScoreWeight Subsystem

Purpose:
    Defines the `ScoreWeight` domain model representing a category scoring weight assignment.

Role in Architecture:
    `ScoreWeight` attaches a numerical weight (0.0 to 1.0) to a `ScoreCategory` to support configurable optimization priorities.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.scoring.score_category import ScoreCategory


@dataclass(slots=True)
class ScoreWeight:
    """
    Scoring category weighting model.

    Attributes:
        category (ScoreCategory): Target scoring category.
        weight (float): Relative importance weight (normalized 0.0 to 1.0).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    category: ScoreCategory
    weight: float
    metadata: dict[str, Any] = field(default_factory=dict)
