"""
Unit tests for Universal Candidate Ranking Framework.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder
from backend.design.components.ranking import (
    RankingCandidate,
    RankingResult,
    TieBreaker,
    HighestScoreStrategy,
    LowestCostStrategy,
    MaximumEnduranceStrategy,
    RankingRegistry,
    RankingPipeline,
    RankingEngine,
)


def test_highest_score_strategy():
    """Verify HighestScoreStrategy ranks candidates by engineering score descending."""
    c1 = RankingCandidate(engineering_score=0.75, metadata={"id": "C1"})
    c2 = RankingCandidate(engineering_score=0.92, metadata={"id": "C2"})
    c3 = RankingCandidate(engineering_score=0.85, metadata={"id": "C3"})

    strategy = HighestScoreStrategy()
    ranked = strategy.rank([c1, c2, c3])

    assert [c.metadata["id"] for c in ranked] == ["C2", "C3", "C1"]


def test_lowest_cost_strategy():
    """Verify LowestCostStrategy ranks candidates by estimated cost ascending."""
    c1 = RankingCandidate(engineering_score=0.80, metadata={"id": "C1", "estimated_cost": 3000})
    c2 = RankingCandidate(engineering_score=0.80, metadata={"id": "C2", "estimated_cost": 1500})
    c3 = RankingCandidate(engineering_score=0.80, metadata={"id": "C3", "estimated_cost": 2200})

    strategy = LowestCostStrategy()
    ranked = strategy.rank([c1, c2, c3])

    assert [c.metadata["id"] for c in ranked] == ["C2", "C3", "C1"]


def test_maximum_endurance_strategy():
    """Verify MaximumEnduranceStrategy ranks candidates by endurance_min descending."""
    c1 = RankingCandidate(metadata={"id": "C1", "endurance_min": 30.0})
    c2 = RankingCandidate(metadata={"id": "C2", "endurance_min": 60.0})
    c3 = RankingCandidate(metadata={"id": "C3", "endurance_min": 45.0})

    strategy = MaximumEnduranceStrategy()
    ranked = strategy.rank([c1, c2, c3])

    assert [c.metadata["id"] for c in ranked] == ["C2", "C3", "C1"]


def test_tie_breaker_resolution():
    """Verify TieBreaker breaks identical score ties using lower cost secondary criteria."""
    # Identical score 0.85
    c1 = RankingCandidate(engineering_score=0.85, metadata={"id": "C1", "estimated_cost": 4000})
    c2 = RankingCandidate(engineering_score=0.85, metadata={"id": "C2", "estimated_cost": 2500})

    tb = TieBreaker(secondary_criteria="LOWER_COST")
    strategy = HighestScoreStrategy()

    ranked = strategy.rank([c1, c2], tie_breaker=tb)

    assert ranked[0].metadata["id"] == "C2"  # C2 is cheaper


def test_ranking_engine_execution():
    """Verify RankingEngine assigns ordinal ranks 1..N and returns valid RankingResult."""
    engine = RankingEngine()

    c1 = RankingCandidate(engineering_score=0.70, metadata={"id": "C1"})
    c2 = RankingCandidate(engineering_score=0.95, metadata={"id": "C2"})
    c3 = RankingCandidate(engineering_score=0.88, metadata={"id": "C3"})

    result = engine.rank_candidates([c1, c2, c3], strategy_name="HighestScoreStrategy")

    assert isinstance(result, RankingResult)
    assert result.best_candidate is not None
    assert result.best_candidate.metadata["id"] == "C2"
    assert [c.rank for c in result.ranked_candidates] == [1, 2, 3]
    assert [c.metadata["id"] for c in result.ranked_candidates] == ["C2", "C3", "C1"]
