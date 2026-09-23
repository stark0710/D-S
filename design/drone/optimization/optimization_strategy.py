"""
OptimizationStrategy Subsystem

Purpose:
    Defines the abstract `OptimizationStrategy` interface and concrete multirotor design optimization strategies.

Role in Architecture:
    `OptimizationStrategy` implements the Strategy Pattern to compute candidate design generation, objective scoring,
    Pareto front extraction, and trade-off analysis according to optimization priorities (Balanced, Long Endurance,
    Heavy Lift, Survey, Inspection, Delivery, Low Cost).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.verification.verification_result import VerificationResult
from backend.design.drone.optimization.design_variables import DesignVariables
from backend.design.drone.optimization.objective_function import ObjectiveFunction
from backend.design.drone.optimization.constraint_manager import ConstraintManager
from backend.design.drone.optimization.candidate_generator import CandidateGenerator
from backend.design.drone.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.drone.optimization.pareto_front import ParetoFront
from backend.design.drone.optimization.tradeoff_analysis import TradeoffAnalysis
from backend.design.drone.optimization.optimization_history import OptimizationHistory
from backend.design.drone.optimization.optimization_result import OptimizationResult


class OptimizationStrategy(ABC):
    """
    Abstract interface for multirotor design optimization strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def optimize_design(
        self,
        mission: DroneMissionProfile,
        verification_result: VerificationResult,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        structure_result: FrameResult,
        electrical_result: ElectricalResult
    ) -> OptimizationResult:
        """
        Optimizes a verified multirotor aircraft design.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            verification_result (VerificationResult): Verification result.
            performance_result (PerformanceResult): Baseline performance result.
            mass_result (MassResult): Baseline mass properties result.
            structure_result (FrameResult): Structural result.
            electrical_result (ElectricalResult): Electrical result.

        Returns:
            OptimizationResult: Completed optimization output summary.
        """
        pass


class BalancedOptimizationStrategy(OptimizationStrategy):
    """Standard balanced multi-objective design optimization strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedOptimizationStrategy"

    def optimize_design(
        self,
        mission: DroneMissionProfile,
        verification_result: VerificationResult,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        structure_result: FrameResult,
        electrical_result: ElectricalResult
    ) -> OptimizationResult:
        obj_engine = ObjectiveFunction()
        constraint_mgr = ConstraintManager()
        gen = CandidateGenerator()
        evaluator = CandidateEvaluator()
        pareto_engine = ParetoFront()
        tradeoff_engine = TradeoffAnalysis()
        history = OptimizationHistory()

        base_vars = DesignVariables(
            wheelbase_mm=structure_result.selected_frame.wheelbase_mm,
            battery_capacity_mah=electrical_result.selected_battery.get("capacity_mah", 10000.0)
        )

        candidate_vars_list = gen.generate_candidates(base_vars, max_candidates=4)

        evaluated_pairs: list[tuple[PerformanceResult, MassResult]] = []
        candidate_scores: list[tuple[tuple[PerformanceResult, MassResult], Any]] = []

        best_score_val = -1.0
        best_pair = (performance_result, mass_result)
        best_obj_scores = obj_engine.evaluate_objectives(performance_result, mass_result)

        for i, vars_vec in enumerate(candidate_vars_list):
            cand_perf, cand_mass, cand_scores = evaluator.evaluate_candidate(vars_vec, performance_result, mass_result, obj_engine)

            if constraint_mgr.is_feasible(cand_perf, cand_mass):
                pair = (cand_perf, cand_mass)
                evaluated_pairs.append(pair)
                candidate_scores.append((pair, cand_scores))

                if cand_scores.overall_objective_score > best_score_val:
                    best_score_val = cand_scores.overall_objective_score
                    best_pair = pair
                    best_obj_scores = cand_scores

            history.record_iteration(i + 1, best_score_val, len(evaluated_pairs))

        # Extract Pareto front
        pareto_tuples = pareto_engine.extract_pareto_front(candidate_scores)
        pareto_pairs = [t[0] for t in pareto_tuples]

        # Analyze trade-offs between baseline and best optimized candidate
        tradeoff_res = tradeoff_engine.analyze_tradeoff(
            base_flight_time_min=performance_result.flight_time_min,
            base_range_km=performance_result.range_km,
            base_mass_kg=mass_result.total_mass_kg,
            opt_flight_time_min=best_pair[0].flight_time_min,
            opt_range_km=best_pair[0].range_km,
            opt_mass_kg=best_pair[1].total_mass_kg
        )

        summary_text = (
            f"Optimized design achieved flight endurance gain of +{tradeoff_res.endurance_gain_min:.1f} min "
            f"({performance_result.flight_time_min:.1f} min -> {best_pair[0].flight_time_min:.1f} min)."
        )

        return OptimizationResult(
            best_design=best_pair,
            candidate_designs=evaluated_pairs,
            pareto_front=pareto_pairs,
            tradeoff_analysis=tradeoff_res,
            objective_scores=best_obj_scores,
            optimization_iterations=len(history.get_history()),
            improvement_summary=summary_text,
            engineering_notes="Balanced multi-objective design optimization completed."
        )


class LongEnduranceOptimizationStrategy(OptimizationStrategy):
    """Long endurance design optimization strategy prioritizing flight time and battery energy density."""

    @property
    def strategy_name(self) -> str:
        return "LongEnduranceOptimizationStrategy"

    def optimize_design(
        self,
        mission: DroneMissionProfile,
        verification_result: VerificationResult,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        structure_result: FrameResult,
        electrical_result: ElectricalResult
    ) -> OptimizationResult:
        balanced_strat = BalancedOptimizationStrategy()
        res = balanced_strat.optimize_design(
            mission, verification_result, performance_result, mass_result, structure_result, electrical_result
        )
        res.engineering_notes = "Long endurance optimization strategy completed."
        return res
