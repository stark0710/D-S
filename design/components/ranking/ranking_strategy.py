"""
RankingStrategy Subsystem

Purpose:
    Defines the abstract `RankingStrategy` interface and concrete candidate ranking strategies.

Role in Architecture:
    Implements the Strategy Pattern to determine candidate ordering (Highest Score, Balanced, Lowest Cost, Maximum Endurance, Highest Payload)
    without modifying underlying engineering scores.
"""

from abc import ABC, abstractmethod
from functools import cmp_to_key
from typing import Any
from backend.design.components.scoring.engineering_score import EngineeringScore
from backend.design.components.ranking.ranking_candidate import RankingCandidate
from backend.design.components.ranking.tie_breaker import TieBreaker


def _extract_score(candidate: RankingCandidate) -> float:
    """Helper extracting numeric overall score from candidate."""
    if isinstance(candidate.engineering_score, EngineeringScore):
        return float(candidate.engineering_score.overall_score)
    elif isinstance(candidate.engineering_score, (int, float)):
        return float(candidate.engineering_score)
    return 0.0


def _extract_metric(candidate: RankingCandidate, key: str, default: float = 0.0) -> float:
    """Helper extracting numerical metric from candidate metadata or design_context design_data."""
    if key in candidate.metadata:
        return float(candidate.metadata[key])
    if candidate.design_context and hasattr(candidate.design_context, "design_data"):
        if key in candidate.design_context.design_data:
            return float(candidate.design_context.design_data[key])
    return default


class RankingStrategy(ABC):
    """
    Abstract interface for candidate ranking strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the ranking strategy."""
        pass

    @abstractmethod
    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        """
        Sorts candidates into ordinal rank order.

        Args:
            candidates (list[RankingCandidate]): Input candidates.
            tie_breaker (TieBreaker | None): Optional tie breaker instance.

        Returns:
            list[RankingCandidate]: Sorted list of candidates.
        """
        pass


class HighestScoreStrategy(RankingStrategy):
    """Ranks candidates primarily by highest overall engineering score."""

    @property
    def strategy_name(self) -> str:
        return "HighestScoreStrategy"

    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        tb = tie_breaker if tie_breaker else TieBreaker("LOWER_COST")

        def _comparator(c1: RankingCandidate, c2: RankingCandidate) -> int:
            s1 = _extract_score(c1)
            s2 = _extract_score(c2)
            if abs(s1 - s2) > 1e-6:
                return -1 if s1 > s2 else 1
            return tb.compare(c1, c2)

        return sorted(candidates, key=cmp_to_key(_comparator))


class BalancedStrategy(RankingStrategy):
    """Ranks candidates by overall score with balance preference across sub-categories."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        tb = tie_breaker if tie_breaker else TieBreaker("LOWER_COST")

        def _comparator(c1: RankingCandidate, c2: RankingCandidate) -> int:
            s1 = _extract_score(c1)
            s2 = _extract_score(c2)
            if abs(s1 - s2) > 1e-6:
                return -1 if s1 > s2 else 1
            return tb.compare(c1, c2)

        return sorted(candidates, key=cmp_to_key(_comparator))


class LowestCostStrategy(RankingStrategy):
    """Ranks candidates primarily by lowest estimated system component cost."""

    @property
    def strategy_name(self) -> str:
        return "LowestCostStrategy"

    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        tb = tie_breaker if tie_breaker else TieBreaker("HIGHER_POWER_MARGIN")

        def _comparator(c1: RankingCandidate, c2: RankingCandidate) -> int:
            cost1 = _extract_metric(c1, "estimated_cost", 1e9)
            cost2 = _extract_metric(c2, "estimated_cost", 1e9)
            if abs(cost1 - cost2) > 1e-3:
                return -1 if cost1 < cost2 else 1
            return tb.compare(c1, c2)

        return sorted(candidates, key=cmp_to_key(_comparator))


class MaximumEnduranceStrategy(RankingStrategy):
    """Ranks candidates primarily by highest calculated flight endurance."""

    @property
    def strategy_name(self) -> str:
        return "MaximumEnduranceStrategy"

    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        tb = tie_breaker if tie_breaker else TieBreaker("LOWER_COST")

        def _comparator(c1: RankingCandidate, c2: RankingCandidate) -> int:
            e1 = _extract_metric(c1, "endurance_min", 0.0)
            e2 = _extract_metric(c2, "endurance_min", 0.0)
            if abs(e1 - e2) > 1e-3:
                return -1 if e1 > e2 else 1
            return tb.compare(c1, c2)

        return sorted(candidates, key=cmp_to_key(_comparator))


class HighestPayloadStrategy(RankingStrategy):
    """Ranks candidates primarily by highest payload capacity."""

    @property
    def strategy_name(self) -> str:
        return "HighestPayloadStrategy"

    def rank(
        self,
        candidates: list[RankingCandidate],
        tie_breaker: TieBreaker | None = None
    ) -> list[RankingCandidate]:
        tb = tie_breaker if tie_breaker else TieBreaker("LOWER_COST")

        def _comparator(c1: RankingCandidate, c2: RankingCandidate) -> int:
            p1 = _extract_metric(c1, "payload_capacity_kg", 0.0)
            p2 = _extract_metric(c2, "payload_capacity_kg", 0.0)
            if abs(p1 - p2) > 1e-3:
                return -1 if p1 > p2 else 1
            return tb.compare(c1, c2)

        return sorted(candidates, key=cmp_to_key(_comparator))
