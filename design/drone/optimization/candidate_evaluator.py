"""
CandidateEvaluator Subsystem

Purpose:
    Defines the `CandidateEvaluator` class for re-running discipline physics models on perturbation candidates.

Role in Architecture:
    `CandidateEvaluator` evaluates performance, mass properties, and objective scores for a candidate `DesignVariables` vector.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.optimization.design_variables import DesignVariables
from backend.design.drone.optimization.objective_function import ObjectiveFunction, ObjectiveScores
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.mass_properties.mass_result import MassResult


class CandidateEvaluator:
    """
    Evaluator service for perturbed candidate designs.

    Design Principles:
        - Single Responsibility Principle: Candidate performance, mass properties, and objective score computation.
    """

    def evaluate_candidate(
        self,
        candidate_vars: DesignVariables,
        base_performance: PerformanceResult,
        base_mass: MassResult,
        objective_function: ObjectiveFunction
    ) -> tuple[PerformanceResult, MassResult, ObjectiveScores]:
        """
        Evaluates candidate physics and returns updated PerformanceResult, MassResult, and ObjectiveScores.

        Args:
            candidate_vars (DesignVariables): Target candidate design variables.
            base_performance (PerformanceResult): Base performance result.
            base_mass (MassResult): Base mass result.
            objective_function (ObjectiveFunction): Objective function service.

        Returns:
            tuple[PerformanceResult, MassResult, ObjectiveScores]: Evaluated result triad.
        """
        # Perturb mass based on battery capacity delta
        cap_delta_ratio = candidate_vars.battery_capacity_mah / 5000.0
        new_total_mass_kg = round(base_mass.total_mass_kg * (0.70 + (0.30 * cap_delta_ratio)), 2)

        # Perturb endurance proportional to battery energy vs mass ratio
        energy_ratio = cap_delta_ratio / (new_total_mass_kg / base_mass.total_mass_kg)
        new_flight_time_min = round(base_performance.flight_time_min * energy_ratio, 1)
        new_range_km = round(base_performance.range_km * energy_ratio, 1)

        # Construct updated MassResult and PerformanceResult
        new_mass = MassResult(
            total_mass_kg=new_total_mass_kg,
            empty_mass_kg=base_mass.empty_mass_kg,
            payload_mass_kg=base_mass.payload_mass_kg,
            mass_breakdown=base_mass.mass_breakdown,
            center_of_gravity=base_mass.center_of_gravity,
            moment_of_inertia=base_mass.moment_of_inertia,
            balance_analysis=base_mass.balance_analysis,
            engineering_notes="Perturbed candidate mass properties."
        )

        new_perf = PerformanceResult(
            flight_time_min=new_flight_time_min,
            max_hover_time_min=round(new_flight_time_min * 1.05, 1),
            range_km=new_range_km,
            cruise_speed_kmh=base_performance.cruise_speed_kmh,
            maximum_speed_kmh=base_performance.maximum_speed_kmh,
            hover_performance=base_performance.hover_performance,
            climb_performance=base_performance.climb_performance,
            descent_performance=base_performance.descent_performance,
            cruise_performance=base_performance.cruise_performance,
            stability_analysis=base_performance.stability_analysis,
            wind_analysis=base_performance.wind_analysis,
            energy_analysis=base_performance.energy_analysis,
            engineering_notes="Perturbed candidate performance."
        )

        scores = objective_function.evaluate_objectives(new_perf, new_mass)
        return new_perf, new_mass, scores
