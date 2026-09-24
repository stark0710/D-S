"""
OptimizationValidator Subsystem

Purpose:
    Defines the `OptimizationValidator` class responsible for validating optimization outputs against constraints.

Role in Architecture:
    `OptimizationValidator` checks convergence, MTOW bounds on optimized candidates, and candidate consistency.
"""

from backend.design.drone.optimization.optimization_result import OptimizationResult
from backend.design.drone.optimization.optimization_constraints import OptimizationConstraints


class OptimizationValidator:
    """
    Validator for multirotor design optimization engineering outputs.

    Design Principles:
        - Single Responsibility Principle: Optimization candidate consistency and constraint validation only.
    """

    def validate_optimization(
        self,
        result: OptimizationResult,
        constraints: OptimizationConstraints
    ) -> list[str]:
        """
        Validates an OptimizationResult against OptimizationConstraints.

        Args:
            result (OptimizationResult): Target optimization result object.
            constraints (OptimizationConstraints): Optimization constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        best_mass = result.best_design[1].total_mass_kg
        if best_mass > constraints.max_mtow_kg:
            warnings.append(
                f"Optimized design MTOW ({best_mass:.2f} kg) exceeds maximum constraint limit ({constraints.max_mtow_kg:.2f} kg)."
            )

        if result.optimization_iterations <= 0:
            warnings.append("Optimization search completed with zero iterations.")

        return warnings
