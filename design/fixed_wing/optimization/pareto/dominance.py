"""
Pareto Dominance and Deduplication Logic.
"""

from typing import List
from backend.design.fixed_wing.optimization.pareto.models import (
    ParetoCandidate,
    ParetoTolerance,
    ObjectiveDirection,
)


def check_dominance(
    a: ParetoCandidate,
    b: ParetoCandidate,
    tolerances: ParetoTolerance | None = None,
) -> bool:
    """
    Returns True iff Candidate A Pareto-dominates Candidate B.
    
    Mathematical Rule:
    A dominates B iff:
    1. A is no worse than B in all objectives (accounting for numerical tolerance).
    2. A is strictly better than B in at least one objective (exceeding numerical tolerance).
    """
    if tolerances is None:
        tolerances = ParetoTolerance()

    # Infeasible candidates cannot dominate feasible ones
    if not a.is_feasible and b.is_feasible:
        return False
    if a.is_feasible and not b.is_feasible:
        return True

    # Identify shared objectives
    shared_keys = set(a.objectives.keys()).intersection(set(b.objectives.keys()))
    if not shared_keys:
        return False

    strictly_better = False

    for key in shared_keys:
        val_a = a.objectives[key].value
        val_b = b.objectives[key].value
        direction = a.objectives[key].direction
        tol = tolerances.get_tolerance(key)

        if direction == ObjectiveDirection.MINIMIZE:
            # For minimization, lower is better.
            # If A is worse than B by more than tolerance, A cannot dominate B.
            if val_a > val_b + tol:
                return False
            # Check if A is strictly better than B
            if val_a < val_b - tol:
                strictly_better = True

        elif direction == ObjectiveDirection.MAXIMIZE:
            # For maximization, higher is better.
            # If A is worse than B by more than tolerance, A cannot dominate B.
            if val_a < val_b - tol:
                return False
            # Check if A is strictly better than B
            if val_a > val_b + tol:
                strictly_better = True

    return strictly_better


def is_duplicate(
    a: ParetoCandidate,
    b: ParetoCandidate,
    tolerances: ParetoTolerance | None = None,
) -> bool:
    """
    Returns True iff Candidate A and Candidate B are within tolerance on all objectives.
    """
    if tolerances is None:
        tolerances = ParetoTolerance()

    shared_keys = set(a.objectives.keys()).intersection(set(b.objectives.keys()))
    if not shared_keys:
        return False

    for key in shared_keys:
        val_a = a.objectives[key].value
        val_b = b.objectives[key].value
        tol = tolerances.get_tolerance(key)
        if abs(val_a - val_b) > tol:
            return False

    return True
