"""
ConfigurationStrategy Subsystem

Purpose:
    Defines the abstract `ConfigurationStrategy` interface and concrete multirotor configuration ranking strategies.

Role in Architecture:
    `ConfigurationStrategy` implements the Strategy Pattern to score and rank multirotor frame candidates
    based on targeted trade-off priorities (Lowest Cost, Max Payload, Max Reliability, Long Endurance, Heavy Lift, Balanced).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_candidate import ConfigurationCandidate


class ConfigurationStrategy(ABC):
    """
    Abstract interface for multirotor configuration ranking strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        """
        Scores and ranks configuration candidates.

        Args:
            candidates (list[ConfigurationCandidate]): Input candidates.
            mission (DroneMissionProfile): Target multirotor mission profile.

        Returns:
            list[ConfigurationCandidate]: Ranked candidate list (Rank 1 first).
        """
        pass


class BalancedStrategy(ConfigurationStrategy):
    """Balanced trade-off strategy across cost, payload, endurance, and reliability."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            score = 0.70
            p = c.profile
            if p.rotor_count == 4:
                score += 0.15  # Good efficiency & low cost
            elif p.rotor_count == 6:
                score += 0.20  # Excellent balance of redundancy & cost
            elif p.rotor_count == 8:
                score += 0.10  # High reliability but higher cost
            if p.coaxial:
                score -= 0.05  # Slight coaxial efficiency penalty (~15% loss)
            c.suitability_score = round(min(1.0, max(0.0, score)), 3)

        return _sort_and_rank(candidates, "Balanced trade-off across payload, efficiency, and cost.")


class LowestCostConfigurationStrategy(ConfigurationStrategy):
    """Prioritizes lowest component count (Quad-rotors)."""

    @property
    def strategy_name(self) -> str:
        return "LowestCostConfigurationStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            p = c.profile
            if p.rotor_count == 4:
                score = 0.95
            elif p.rotor_count == 6:
                score = 0.75
            else:
                score = 0.50
            c.suitability_score = score

        return _sort_and_rank(candidates, "Lowest BOM component cost (4 motors/ESCs vs 6/8).")


class MaximumPayloadStrategy(ConfigurationStrategy):
    """Prioritizes maximum total thrust capacity for heavy payloads."""

    @property
    def strategy_name(self) -> str:
        return "MaximumPayloadStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            p = c.profile
            if p.rotor_count == 8:
                score = 0.95
            elif p.rotor_count == 6:
                score = 0.80
            else:
                score = 0.60
            c.suitability_score = score

        return _sort_and_rank(candidates, "Highest total thrust capacity for heavy payload transport.")


class MaximumReliabilityStrategy(ConfigurationStrategy):
    """Prioritizes motor failure redundancy (Octocopter & Hexacopter)."""

    @property
    def strategy_name(self) -> str:
        return "MaximumReliabilityStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            p = c.profile
            if p.rotor_count == 8:
                score = 0.98  # Dual motor loss capability
            elif p.rotor_count == 6:
                score = 0.85  # Single motor loss capability
            else:
                score = 0.30  # Zero motor failure tolerance
            c.suitability_score = score

        return _sort_and_rank(candidates, "Highest motor loss redundancy and mission safety.")


class LongEnduranceStrategy(ConfigurationStrategy):
    """Prioritizes planar non-coaxial frames for maximum hover propulsion efficiency."""

    @property
    def strategy_name(self) -> str:
        return "LongEnduranceStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            p = c.profile
            score = 0.70
            if not p.coaxial:
                score += 0.20  # Avoid coaxial efficiency penalty
            if p.rotor_count == 4:
                score += 0.08  # Lower structural weight
            c.suitability_score = round(min(1.0, max(0.0, score)), 3)

        return _sort_and_rank(candidates, "Planar propeller layout maximizing aerodynamic hover efficiency.")


class HeavyLiftStrategy(ConfigurationStrategy):
    """Prioritizes compact coaxial heavy lift (X8, Y6)."""

    @property
    def strategy_name(self) -> str:
        return "HeavyLiftStrategy"

    def rank_candidates(
        self,
        candidates: list[ConfigurationCandidate],
        mission: DroneMissionProfile
    ) -> list[ConfigurationCandidate]:
        for c in candidates:
            p = c.profile
            if p.config_type in ("X8", "OCTOCOPTER"):
                score = 0.95
            elif p.config_type in ("Y6", "HEXACOPTER"):
                score = 0.80
            else:
                score = 0.50
            c.suitability_score = score

        return _sort_and_rank(candidates, "Heavy lift thrust density in a compact frame envelope.")


def _sort_and_rank(candidates: list[ConfigurationCandidate], note: str) -> list[ConfigurationCandidate]:
    """Helper sorting candidates descending by suitability_score and assigning ordinal ranks."""
    sorted_cands = sorted(candidates, key=lambda c: c.suitability_score, reverse=True)
    for idx, cand in enumerate(sorted_cands, start=1):
        cand.rank = idx
        cand.justification = f"Rank {idx}: {note} (Score: {cand.suitability_score:.2f})"
    return sorted_cands
