"""
RankingResult Subsystem

Purpose:
    Defines the `RankingResult` domain model representing the output of candidate design ranking.

Role in Architecture:
    `RankingResult` encapsulates the ordered list of `RankingCandidate` objects (highest rank first),
    the top best candidate option, summary text, and execution metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.ranking.ranking_candidate import RankingCandidate


@dataclass(slots=True)
class RankingResult:
    """
    Aggregated candidate design ranking output.

    Attributes:
        ranked_candidates (list[RankingCandidate]): Candidates sorted in ordinal rank order (Rank 1 first).
        best_candidate (RankingCandidate | None): Top Rank-1 winning candidate option.
        ranking_summary (str): Transparent human-readable summary of candidate ranking order.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    ranked_candidates: list[RankingCandidate]
    best_candidate: RankingCandidate | None
    ranking_summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
