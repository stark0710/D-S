"""
Torq Wings VTOL Phase 7 - Pareto Dominance and Front Extraction.

Implements mathematically rigorous Pareto dominance comparisons and non-dominated
front extraction without synthetic interpolation or weighted-sum approximations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional

from .optimization_models import DesignEvaluation, EvaluationStatus
from .objective_model import ObjectiveDefinition, ObjectiveDirection


def dominates(
    candidate_a: DesignEvaluation,
    candidate_b: DesignEvaluation,
    objectives: List[ObjectiveDefinition],
) -> bool:
    """
    Determine if candidate A Pareto-dominates candidate B.

    Candidate A dominates Candidate B if and only if:
    1. A is at least as good as B in ALL objectives.
    2. A is strictly better than B in at least ONE objective.

    For MINIMIZE: val_A <= val_B (strictly better if val_A < val_B)
    For MAXIMIZE: val_A >= val_B (strictly better if val_A > val_B)
    """
    if not objectives:
        return False

    at_least_as_good_all = True
    strictly_better_any = False

    for obj in objectives:
        val_a = candidate_a.objective_values.get(obj.name)
        val_b = candidate_b.objective_values.get(obj.name)

        if val_a is None or val_b is None:
            # Cannot compare if an objective value is missing
            return False

        if obj.direction == ObjectiveDirection.MINIMIZE:
            if val_a > val_b:
                at_least_as_good_all = False
                break
            if val_a < val_b:
                strictly_better_any = True
        elif obj.direction == ObjectiveDirection.MAXIMIZE:
            if val_a < val_b:
                at_least_as_good_all = False
                break
            if val_a > val_b:
                strictly_better_any = True

    return at_least_as_good_all and strictly_better_any


@dataclass(slots=True)
class ParetoPartition:
    """Categorized partition of evaluated design candidates."""
    pareto_front: List[DesignEvaluation] = field(default_factory=list)
    dominated_candidates: List[DesignEvaluation] = field(default_factory=list)
    infeasible_candidates: List[DesignEvaluation] = field(default_factory=list)
    error_candidates: List[DesignEvaluation] = field(default_factory=list)

    @property
    def pareto_count(self) -> int:
        return len(self.pareto_front)

    @property
    def dominated_count(self) -> int:
        return len(self.dominated_candidates)

    @property
    def infeasible_count(self) -> int:
        return len(self.infeasible_candidates)

    @property
    def error_count(self) -> int:
        return len(self.error_candidates)


def extract_pareto_front(
    evaluations: List[DesignEvaluation],
    objectives: List[ObjectiveDefinition],
) -> ParetoPartition:
    """
    Extract the non-dominated Pareto front from a list of evaluations.

    Rules:
    - Only FEASIBLE candidates can enter the Pareto front.
    - INFEASIBLE and EVALUATION_ERROR candidates are partitioned separately.
    - Candidate A is on the Pareto front if no other feasible candidate dominates A.
    - If multiple identical non-dominated candidates exist, they may both reside on the front.
    - No synthetic or interpolated points are ever created.
    """
    partition = ParetoPartition()

    feasible_candidates: List[DesignEvaluation] = []

    for ev in evaluations:
        if ev.status == EvaluationStatus.EVALUATION_ERROR:
            partition.error_candidates.append(ev)
        elif not ev.is_feasible or ev.status == EvaluationStatus.INFEASIBLE:
            partition.infeasible_candidates.append(ev)
        elif ev.status == EvaluationStatus.FEASIBLE and ev.is_feasible:
            feasible_candidates.append(ev)
        else:
            # Fallback for unexpected status
            partition.infeasible_candidates.append(ev)

    if not feasible_candidates:
        return partition

    if not objectives:
        # Without objectives, all feasible candidates are non-dominated
        partition.pareto_front = list(feasible_candidates)
        return partition

    n = len(feasible_candidates)
    is_dominated = [False] * n

    for i in range(n):
        cand_i = feasible_candidates[i]
        for j in range(n):
            if i == j:
                continue
            cand_j = feasible_candidates[j]
            # Does candidate j dominate candidate i?
            if dominates(cand_j, cand_i, objectives):
                is_dominated[i] = True
                break

    for i in range(n):
        cand = feasible_candidates[i]
        if is_dominated[i]:
            partition.dominated_candidates.append(cand)
        else:
            partition.pareto_front.append(cand)

    return partition


def extract_best_by_objective(
    pareto_front: List[DesignEvaluation],
    objectives: List[ObjectiveDefinition],
) -> Dict[str, DesignEvaluation]:
    """
    Identify the single best candidate along each defined objective axis.
    Provides a descriptive view without imposing a weighted-sum ranking.
    """
    best_map: Dict[str, DesignEvaluation] = {}

    if not pareto_front or not objectives:
        return best_map

    for obj in objectives:
        best_cand: Optional[DesignEvaluation] = None
        best_score: Optional[float] = None

        for cand in pareto_front:
            val = cand.objective_values.get(obj.name)
            if val is None:
                continue

            score = obj.standardized_score(val)
            if best_score is None or score < best_score:
                best_score = score
                best_cand = cand

        if best_cand is not None:
            best_map[obj.name] = best_cand

    return best_map
