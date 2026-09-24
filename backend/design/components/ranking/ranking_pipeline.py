"""
RankingPipeline Subsystem

Purpose:
    Defines the `RankingPipeline` class responsible for executing candidate ranking strategies and building ranking results.

Role in Architecture:
    `RankingPipeline` coordinates candidate sorting via `RankingStrategy`, applies `TieBreaker` rules, assigns 1-based ordinal ranks,
    and constructs a `RankingResult`.
"""

from backend.design.components.ranking.ranking_candidate import RankingCandidate
from backend.design.components.ranking.ranking_result import RankingResult
from backend.design.components.ranking.tie_breaker import TieBreaker
from backend.design.components.ranking.ranking_strategy import RankingStrategy, HighestScoreStrategy


class RankingPipeline:
    """
    Pipeline for executing candidate design ranking workflows.

    Design Principles:
        - Pipeline Pattern: Orchestrates candidate sorting, tie-breaking, and ordinal rank assignment.
        - Strategy Pattern: Delegates candidate sorting to injected RankingStrategy.
    """

    def __init__(
        self,
        strategy: RankingStrategy | None = None,
        tie_breaker: TieBreaker | None = None
    ) -> None:
        """
        Initializes the RankingPipeline.

        Args:
            strategy (RankingStrategy | None): Injected ranking strategy. Defaults to HighestScoreStrategy if None.
            tie_breaker (TieBreaker | None): Injected tie breaker. Defaults to TieBreaker('LOWER_COST') if None.
        """
        self._strategy: RankingStrategy = strategy if strategy else HighestScoreStrategy()
        self._tie_breaker: TieBreaker = tie_breaker if tie_breaker else TieBreaker("LOWER_COST")

    def execute(self, candidates: list[RankingCandidate]) -> RankingResult:
        """
        Executes candidate design ranking.

        Args:
            candidates (list[RankingCandidate]): Candidate designs to rank.

        Returns:
            RankingResult: Aggregated ranked result with ordinal ranks assigned.
        """
        if not candidates:
            return RankingResult(
                ranked_candidates=[],
                best_candidate=None,
                ranking_summary="Zero candidates provided for ranking.",
                metadata={"strategy": self._strategy.strategy_name}
            )

        sorted_candidates = self._strategy.rank(candidates, tie_breaker=self._tie_breaker)

        # Assign 1-based ordinal rank indices
        for idx, cand in enumerate(sorted_candidates, start=1):
            cand.rank = idx
            cand.ranking_notes.append(f"Assigned Rank {idx} by {self._strategy.strategy_name}.")

        best = sorted_candidates[0]
        summary = (
            f"Candidate ranking complete using {self._strategy.strategy_name} (Evaluated {len(sorted_candidates)} candidates). "
            f"Top Rank-1 candidate selected."
        )

        return RankingResult(
            ranked_candidates=sorted_candidates,
            best_candidate=best,
            ranking_summary=summary,
            metadata={"strategy": self._strategy.strategy_name, "total_candidates": len(sorted_candidates)}
        )
