"""
RankingEngine Subsystem

Purpose:
    Defines the `RankingEngine` class, which serves as the public entry point for candidate design ranking.

Role in Architecture:
    `RankingEngine` receives a list of evaluated `RankingCandidate` objects, resolves the target strategy from `RankingRegistry`,
    executes a `RankingPipeline` with configurable tie-breaking, and returns a `RankingResult`.
"""

from backend.design.components.ranking.ranking_candidate import RankingCandidate
from backend.design.components.ranking.ranking_result import RankingResult
from backend.design.components.ranking.tie_breaker import TieBreaker
from backend.design.components.ranking.ranking_registry import RankingRegistry
from backend.design.components.ranking.ranking_pipeline import RankingPipeline
from backend.design.components.ranking.ranking_strategy import (
    HighestScoreStrategy,
    BalancedStrategy,
    LowestCostStrategy,
    MaximumEnduranceStrategy,
    HighestPayloadStrategy,
)


class RankingEngine:
    """
    Public entry point service for candidate design ranking.

    Design Principles:
        - Single Responsibility Principle: Candidate ranking orchestration only.
        - Dependency Injection: Injects `RankingRegistry` collaborator.
        - Non-Modifying: Never alters or recalculates engineering scores.
    """

    def __init__(
        self,
        registry: RankingRegistry | None = None,
        pipeline: RankingPipeline | None = None
    ) -> None:
        """
        Initializes the RankingEngine.

        Args:
            registry (RankingRegistry | None): Injected registry instance. If None, populates default strategies.
            pipeline (RankingPipeline | None): Optional injected pipeline instance.
        """
        if registry is None:
            registry = RankingRegistry()
            registry.register_strategy(HighestScoreStrategy())
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(LowestCostStrategy())
            registry.register_strategy(MaximumEnduranceStrategy())
            registry.register_strategy(HighestPayloadStrategy())

        self._registry: RankingRegistry = registry
        self._default_pipeline: RankingPipeline | None = pipeline

    def rank_candidates(
        self,
        candidates: list[RankingCandidate],
        strategy_name: str = "HighestScoreStrategy",
        tie_breaker_criteria: str = "LOWER_COST"
    ) -> RankingResult:
        """
        Ranks candidate designs using the specified strategy and tie breaker.

        Args:
            candidates (list[RankingCandidate]): Input candidates to rank.
            strategy_name (str): Identifier name of the strategy to execute.
            tie_breaker_criteria (str): Secondary tie breaker criteria.

        Returns:
            RankingResult: Final ranked candidate summary.
        """
        strategy = self._registry.get_strategy(strategy_name)
        tie_breaker = TieBreaker(secondary_criteria=tie_breaker_criteria)

        pipeline = RankingPipeline(strategy=strategy, tie_breaker=tie_breaker)
        return pipeline.execute(candidates)
