"""
RankingCandidate Subsystem

Purpose:
    Defines the `RankingCandidate` domain model representing a candidate design option being ranked.

Role in Architecture:
    `RankingCandidate` encapsulates a `DesignContext`, its evaluated `EngineeringScore`, assigned `rank` integer,
    ranking notes, and diagnostic metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.components.scoring.engineering_score import EngineeringScore


@dataclass(slots=True)
class RankingCandidate:
    """
    Feasible aircraft design candidate for ranking.

    Attributes:
        design_context (DesignContext | None): DesignContext carrying design data and requirements.
        engineering_score (EngineeringScore | float | None): Evaluated engineering score model or numeric overall score.
        rank (int): Assigned ordinal rank position (1-based index).
        ranking_notes (list[str]): Explanatory technical notes regarding ranking placement.
        metadata (dict[str, Any]): Additional candidate design metadata (e.g. estimated_cost, MTOW).
    """

    design_context: DesignContext | None = None
    engineering_score: EngineeringScore | float | None = None
    rank: int = 0
    ranking_notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
