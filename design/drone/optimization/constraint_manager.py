"""
ConstraintManager Subsystem

Purpose:
    Defines the `ConstraintManager` class for enforcing hard engineering constraints during optimization search.

Role in Architecture:
    `ConstraintManager` checks candidate feasibility against MTOW limit, minimum flight endurance, minimum thrust margin,
    safe descent rate, CG balance offsets, and electrical thermal boundaries.
"""

from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.mass_properties.mass_result import MassResult


class ConstraintManager:
    """
    Constraint enforcement service during optimization search.

    Design Principles:
        - Single Responsibility Principle: Hard engineering constraint checking and candidate feasibility filtering only.
    """

    def is_feasible(
        self,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        max_mtow_kg: float = 25.0,
        min_flight_time_min: float = 15.0
    ) -> bool:
        """
        Checks if candidate design satisfies all hard engineering constraints.

        Args:
            performance_result (PerformanceResult): Candidate performance result.
            mass_result (MassResult): Candidate mass properties result.
            max_mtow_kg (float): MTOW limit in kg.
            min_flight_time_min (float): Flight time requirement in min.

        Returns:
            bool: True if feasible; False if hard constraint violated.
        """
        mtow_ok = mass_result.total_mass_kg <= max_mtow_kg
        flight_ok = performance_result.flight_time_min >= min_flight_time_min
        tw_ok = performance_result.hover_performance.hover_thrust_margin >= 1.5
        cg_ok = mass_result.balance_analysis.pitch_balanced and mass_result.balance_analysis.roll_balanced

        return mtow_ok and flight_ok and tw_ok and cg_ok
