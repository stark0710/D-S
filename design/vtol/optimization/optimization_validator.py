from typing import List
from .optimization_result import OptimizationResult
from .optimization_constraints import OptimizationConstraints

class OptimizationValidator:
    """
    Validates design optimizer outputs.
    """
    @staticmethod
    def validate(result: OptimizationResult, constraints: OptimizationConstraints) -> List[str]:
        warnings = []

        # Check convergence
        if not result.optimization_analysis.is_converged:
            warnings.append("Optimizer loop did not converge within the designated iteration budgets.")

        # Check constraints feasibility
        if not result.constraint_summary.is_feasible:
            warnings.append(
                f"Optimized configuration violates design constraints. "
                f"Total penalty: {result.constraint_summary.total_penalty:.2f}"
            )

        # Check improvement
        if result.optimization_analysis.improvement_pct < 0.0:
            warnings.append("Optimized design has a lower fitness rating than the base configuration.")

        return warnings
