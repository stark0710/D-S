"""
ParetoFront Subsystem

Purpose:
    Defines the `ParetoFront` class for Pareto dominance comparison and non-dominated set filtering.

Role in Architecture:
    `ParetoFront` filters candidate solutions to identify Pareto-optimal non-dominated designs.
"""

from typing import Any
from backend.design.drone.optimization.objective_function import ObjectiveScores


class ParetoFront:
    """
    Pareto dominance evaluation service.

    Design Principles:
        - Single Responsibility Principle: Pareto dominance comparison and non-dominated sorting only.
    """

    def is_dominated(self, score_a: ObjectiveScores, score_b: ObjectiveScores) -> bool:
        """
        Checks if candidate A is strictly dominated by candidate B.

        Candidate B dominates A if B is at least as good in all objectives and strictly better in at least one.

        Args:
            score_a (ObjectiveScores): Candidate A score.
            score_b (ObjectiveScores): Candidate B score.

        Returns:
            bool: True if A is dominated by B; False otherwise.
        """
        b_better_or_equal = (
            score_b.endurance_score >= score_a.endurance_score and
            score_b.range_score >= score_a.range_score and
            score_b.payload_score >= score_a.payload_score and
            score_b.mass_score >= score_a.mass_score
        )

        b_strictly_better = (
            score_b.endurance_score > score_a.endurance_score or
            score_b.range_score > score_a.range_score or
            score_b.payload_score > score_a.payload_score or
            score_b.mass_score > score_a.mass_score
        )

        return b_better_or_equal and b_strictly_better

    def extract_pareto_front(self, candidate_scores: list[tuple[Any, ObjectiveScores]]) -> list[tuple[Any, ObjectiveScores]]:
        """
        Extracts non-dominated candidate designs forming the Pareto front.

        Args:
            candidate_scores (list[tuple[Any, ObjectiveScores]]): List of (candidate, scores) tuples.

        Returns:
            list[tuple[Any, ObjectiveScores]]: Non-dominated Pareto front subset.
        """
        pareto: list[tuple[Any, ObjectiveScores]] = []

        for cand, score in candidate_scores:
            dominated = False
            for other_cand, other_score in candidate_scores:
                if cand == other_cand:
                    continue
                if self.is_dominated(score, other_score):
                    dominated = True
                    break
            if not dominated:
                pareto.append((cand, score))

        return pareto
