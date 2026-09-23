"""
PerformanceValidator Subsystem

Purpose:
    Defines the `PerformanceValidator` class responsible for validating multirotor flight performance against constraints.

Role in Architecture:
    `PerformanceValidator` checks flight endurance bounds, thrust margins, energy reserve margins, and descent rate bounds.
"""

from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.performance.performance_constraints import PerformanceConstraints


class PerformanceValidator:
    """
    Validator for multirotor flight performance engineering designs.

    Design Principles:
        - Single Responsibility Principle: Flight performance constraint and safety validation only.
    """

    def validate_performance(
        self,
        result: PerformanceResult,
        constraints: PerformanceConstraints
    ) -> list[str]:
        """
        Validates a PerformanceResult against PerformanceConstraints.

        Args:
            result (PerformanceResult): Target performance result object.
            constraints (PerformanceConstraints): Performance constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        if result.flight_time_min < constraints.min_flight_time_min:
            warnings.append(
                f"Flight time ({result.flight_time_min:.1f} min) is below minimum requirement ({constraints.min_flight_time_min:.1f} min)."
            )

        if result.hover_performance.hover_thrust_margin < constraints.min_thrust_margin:
            warnings.append(
                f"Available thrust margin ({result.hover_performance.hover_thrust_margin:.2f}) is below minimum required ({constraints.min_thrust_margin:.2f})."
            )

        if result.energy_analysis.energy_reserve_percent < constraints.min_energy_reserve_percent:
            warnings.append(
                f"Energy reserve ({result.energy_analysis.energy_reserve_percent:.1f}%) is below safe landing margin ({constraints.min_energy_reserve_percent:.1f}%)."
            )

        return warnings
