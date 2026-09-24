"""
Convergence and Iteration Tracking Subsystem for VTOL Multidisciplinary Design.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import math


@dataclass(slots=True)
class IterationRecord:
    """
    State tracking record for a single sizing loop iteration.
    """
    iteration: int
    old_mtow: float
    calculated_mtow: float
    new_mtow: float
    residual: float
    converged: bool
    relaxation_alpha: float = 0.70
    stagnated: bool = False
    oscillating: bool = False
    notes: str = ""


class VTOLConvergenceManager:
    """
    Evaluator responsible for tracking true MTOW convergence across multidisciplinary design iterations.
    Includes safeguards against oscillation, stagnation, non-finite values, and false zero-residual artifacts.
    """
    def __init__(
        self,
        tolerance: float = 0.015,
        max_iterations: int = 20,
        relaxation_alpha: float = 0.70,
    ) -> None:
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.relaxation_alpha = relaxation_alpha
        self.history: list[IterationRecord] = []

    def evaluate_step(
        self,
        iteration: int,
        old_mtow: float,
        calculated_mtow: float,
        is_independent_calculation: bool = True,
    ) -> IterationRecord:
        """
        Evaluates convergence for the current iteration step, applies under-relaxation,
        and records diagnostics in history.

        Args:
            iteration: Current 1-indexed iteration counter.
            old_mtow: Assumed MTOW used as input for current iteration physics.
            calculated_mtow: Independently synthesized total mass from component ledger.
            is_independent_calculation: Flag asserting calculated_mtow is not an algebraic identity.

        Returns:
            IterationRecord capturing the step evaluation.
        """
        # 1. Non-finite & positive sanity checks
        if not math.isfinite(calculated_mtow) or not math.isfinite(old_mtow):
            raise ValueError(f"Non-finite MTOW detected: old={old_mtow}, calculated={calculated_mtow}")
        if calculated_mtow <= 0.0 or old_mtow <= 0.0:
            raise ValueError(f"Non-positive MTOW detected: old={old_mtow}, calculated={calculated_mtow}")

        # 2. Residual calculation: |calculated - old|
        residual = abs(calculated_mtow - old_mtow)

        # 3. False zero-residual detection: if identical on iteration 1 without independent synthesis
        if iteration == 1 and residual < 1e-12 and not is_independent_calculation:
            raise RuntimeError(
                "Invalid convergence architecture: calculated mass is algebraically identical to initial guess, "
                "bypassing physical feedback."
            )

        # 4. Convergence check against tolerance
        converged = residual <= self.tolerance

        # 5. Under-relaxation update: M_{k+1} = alpha * M_calc + (1 - alpha) * M_old
        new_mtow = self.relaxation_alpha * calculated_mtow + (1.0 - self.relaxation_alpha) * old_mtow

        # 6. Oscillation / Stagnation detection
        oscillating = False
        stagnated = False
        if len(self.history) >= 2:
            prev1 = self.history[-1]
            prev2 = self.history[-2]
            delta1 = calculated_mtow - old_mtow
            delta2 = prev1.calculated_mtow - prev1.old_mtow
            # Sign flip with non-diminishing magnitude indicates oscillation
            if (delta1 * delta2 < 0) and abs(delta1) >= 0.85 * abs(delta2) and not converged:
                oscillating = True

            # Stagnation: 3 iterations with negligible residual change while still not converged
            if abs(residual - prev1.residual) < 1e-4 and abs(prev1.residual - prev2.residual) < 1e-4 and not converged:
                stagnated = True

        notes = "Converged" if converged else "Iterating"
        if oscillating:
            notes += "; Oscillation detected, stabilized via under-relaxation"
        if stagnated:
            notes += "; Warning: slow convergence progress"

        record = IterationRecord(
            iteration=iteration,
            old_mtow=old_mtow,
            calculated_mtow=calculated_mtow,
            new_mtow=new_mtow,
            residual=residual,
            converged=converged,
            relaxation_alpha=self.relaxation_alpha,
            stagnated=stagnated,
            oscillating=oscillating,
            notes=notes,
        )
        self.history.append(record)
        return record
