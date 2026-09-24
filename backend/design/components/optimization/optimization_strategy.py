"""
OptimizationStrategy Subsystem

Purpose:
    Defines the abstract `OptimizationStrategy` interface and concrete design candidate modification strategies.

Role in Architecture:
    Implements the Strategy Pattern to generate modified candidate design variants (Greedy, Hill Climbing, Beam Search)
    without performing engineering calculations or bypass evaluations.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any
from backend.design.components.optimization.optimization_candidate import OptimizationCandidate


class OptimizationStrategy(ABC):
    """
    Abstract interface for design candidate optimization strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the optimization strategy."""
        pass

    @abstractmethod
    def generate_modifications(
        self,
        candidate: OptimizationCandidate,
        iteration: int
    ) -> list[OptimizationCandidate]:
        """
        Generates modified candidate design variants derived from input candidate.

        Args:
            candidate (OptimizationCandidate): Baseline candidate design.
            iteration (int): Current iteration step number.

        Returns:
            list[OptimizationCandidate]: List of generated candidate variants.
        """
        pass


class GreedyOptimizationStrategy(OptimizationStrategy):
    """Generates discrete parameter tweaks (battery capacity, weight, efficiency) greedy variations."""

    @property
    def strategy_name(self) -> str:
        return "GreedyOptimizationStrategy"

    def generate_modifications(
        self,
        candidate: OptimizationCandidate,
        iteration: int
    ) -> list[OptimizationCandidate]:
        variants: list[OptimizationCandidate] = []
        base_data = candidate.design_context.design_data

        # Variation 1: Increase endurance / battery capacity by +10%
        v1_context = deepcopy(candidate.design_context)
        curr_endurance = float(base_data.get("endurance_min", 30.0))
        curr_cost = float(base_data.get("estimated_cost", 2000.0))
        curr_mtow = float(base_data.get("mtow_kg", 5.0))

        v1_context.design_data["endurance_min"] = round(curr_endurance * 1.10, 1)
        v1_context.design_data["estimated_cost"] = round(curr_cost * 1.05, 2)
        v1_context.design_data["mtow_kg"] = round(curr_mtow * 1.04, 2)

        variants.append(
            OptimizationCandidate(
                design_context=v1_context,
                iteration=iteration,
                parent_candidate=candidate,
                modifications={"endurance_scale": 1.10, "cost_scale": 1.05}
            )
        )

        # Variation 2: Decrease system cost by -8% (slight payload/endurance trade-off)
        v2_context = deepcopy(candidate.design_context)
        v2_context.design_data["estimated_cost"] = round(curr_cost * 0.92, 2)
        v2_context.design_data["mtow_kg"] = round(curr_mtow * 0.96, 2)

        variants.append(
            OptimizationCandidate(
                design_context=v2_context,
                iteration=iteration,
                parent_candidate=candidate,
                modifications={"cost_scale": 0.92, "mtow_scale": 0.96}
            )
        )

        # Variation 3: Increase thrust-to-weight ratio / power safety margin
        v3_context = deepcopy(candidate.design_context)
        curr_tw = float(base_data.get("thrust_to_weight_ratio", 2.0))
        v3_context.design_data["thrust_to_weight_ratio"] = round(curr_tw + 0.20, 2)
        v3_context.design_data["estimated_cost"] = round(curr_cost * 1.03, 2)

        variants.append(
            OptimizationCandidate(
                design_context=v3_context,
                iteration=iteration,
                parent_candidate=candidate,
                modifications={"tw_bump": +0.20}
            )
        )

        return variants


class HillClimbingStrategy(OptimizationStrategy):
    """Generates fine-grained local neighbor parameter perturbations."""

    @property
    def strategy_name(self) -> str:
        return "HillClimbingStrategy"

    def generate_modifications(
        self,
        candidate: OptimizationCandidate,
        iteration: int
    ) -> list[OptimizationCandidate]:
        variants: list[OptimizationCandidate] = []
        base_data = candidate.design_context.design_data

        # Perturbation step scale decreases slightly with iteration
        step = max(0.02, 0.10 - (iteration * 0.01))

        curr_endurance = float(base_data.get("endurance_min", 30.0))
        curr_cost = float(base_data.get("estimated_cost", 2000.0))
        curr_range = float(base_data.get("range_km", 20.0))

        # Positive step
        context_pos = deepcopy(candidate.design_context)
        context_pos.design_data["endurance_min"] = round(curr_endurance * (1.0 + step), 1)
        context_pos.design_data["range_km"] = round(curr_range * (1.0 + step), 1)

        variants.append(
            OptimizationCandidate(
                design_context=context_pos,
                iteration=iteration,
                parent_candidate=candidate,
                modifications={"endurance_step": +step}
            )
        )

        # Cost optimization step
        context_cost = deepcopy(candidate.design_context)
        context_cost.design_data["estimated_cost"] = round(curr_cost * (1.0 - step), 2)

        variants.append(
            OptimizationCandidate(
                design_context=context_cost,
                iteration=iteration,
                parent_candidate=candidate,
                modifications={"cost_step": -step}
            )
        )

        return variants
