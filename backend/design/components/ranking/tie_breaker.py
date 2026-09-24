"""
TieBreaker Subsystem

Purpose:
    Defines the `TieBreaker` class for resolving score ties between candidate design options.

Role in Architecture:
    `TieBreaker` provides configurable secondary sorting criteria (lower cost, lower weight, higher reliability, higher power margin)
    when primary engineering scores are identical.
"""

from typing import Any
from backend.design.components.ranking.ranking_candidate import RankingCandidate


class TieBreaker:
    """
    Configurable tie breaker for resolving score ties.

    Design Principles:
        - Deterministic Tie Resolution: Uses secondary metrics (Cost, MTOW, Power Margin) to break ties.
    """

    def __init__(self, secondary_criteria: str = "LOWER_COST") -> None:
        """
        Initializes the TieBreaker.

        Args:
            secondary_criteria (str): Criteria name ('LOWER_COST', 'LOWER_WEIGHT', 'HIGHER_POWER_MARGIN', 'ALPHABETICAL').
        """
        self._criteria: str = secondary_criteria.upper()

    def compare(self, c1: RankingCandidate, c2: RankingCandidate) -> int:
        """
        Compares two candidates using secondary criteria.

        Returns:
            int: Negative if c1 is preferred over c2, positive if c2 is preferred over c1, 0 if equal.
        """
        if self._criteria == "LOWER_COST":
            cost1 = self._extract_metric(c1, "estimated_cost", 1e9)
            cost2 = self._extract_metric(c2, "estimated_cost", 1e9)
            if cost1 != cost2:
                return -1 if cost1 < cost2 else 1

        elif self._criteria == "LOWER_WEIGHT":
            w1 = self._extract_metric(c1, "mtow_kg", 1e9)
            w2 = self._extract_metric(c2, "mtow_kg", 1e9)
            if w1 != w2:
                return -1 if w1 < w2 else 1

        elif self._criteria == "HIGHER_POWER_MARGIN":
            p1 = self._extract_metric(c1, "thrust_to_weight_ratio", 0.0)
            p2 = self._extract_metric(c2, "thrust_to_weight_ratio", 0.0)
            if p1 != p2:
                return -1 if p1 > p2 else 1

        # Fallback to metadata ID / summary comparison
        id1 = str(c1.metadata.get("id", ""))
        id2 = str(c2.metadata.get("id", ""))
        if id1 != id2:
            return -1 if id1 < id2 else 1

        return 0

    def _extract_metric(self, candidate: RankingCandidate, key: str, default: float) -> float:
        """Extracts numerical metric from candidate metadata or design_context design_data."""
        if key in candidate.metadata:
            return float(candidate.metadata[key])

        if candidate.design_context and hasattr(candidate.design_context, "design_data"):
            if key in candidate.design_context.design_data:
                return float(candidate.design_context.design_data[key])

        return default
