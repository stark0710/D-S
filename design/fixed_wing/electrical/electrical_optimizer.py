"""
Electrical System Optimization Engine

Subclasses OptimizerBase to orchestrate avionics, actuator, power module, PDB,BEC,
connector, and wiring selection.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.electrical.models import ElectricalSystemSpecification
from backend.design.fixed_wing.electrical.result import ElectricalOptimizationResult
from backend.design.fixed_wing.electrical.candidate_generator import ElectricalCandidateGenerator
from backend.design.fixed_wing.electrical.constraints import build_electrical_constraints
from backend.design.fixed_wing.electrical.objective_function import ElectricalObjectiveFunction


class ElectricalOptimizer(OptimizerBase):
    """
    Orchestrates the selection and compatibility checks for complete fixed-wing electrical designs.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        super().__init__("ElectricalOptimizer")
        # Define objective scoring
        self.electrical_objective = ElectricalObjectiveFunction(weights)

        # Register constraints
        for check in build_electrical_constraints():
            self.constraints.add_constraint(check.__name__, check)

        # Register aggregate objective in base class
        self.objective.add_objective(
            name="electrical_score",
            score_fn=lambda cand, ctx: self.electrical_objective.evaluate(cand, ctx),
            weight=1.0,
            minimize=False  # We want to maximize fitness score
        )

    def optimize(self, context: OptimizationContext) -> ElectricalOptimizationResult:
        """Runs the optimization search and returns a typed result."""
        res = super().optimize(context)
        return ElectricalOptimizationResult(
            winning_candidate=res.winning_candidate,
            generated_specification=res.generated_specification,
            success=res.success,
            message=res.message,
            evaluated_count=res.evaluated_count,
            feasible_count=res.feasible_count,
            history=res.history,
            rejected_summary=res.rejected_summary,
            execution_time_seconds=res.execution_time_seconds,
            iteration_count=res.iteration_count,
            diagnostics=res.diagnostics,
        )

    # ------------------------------------------------------------------
    #  OptimizerBase lifecycle hooks
    # ------------------------------------------------------------------

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            self.electrical_objective.weights = OptimizationPriorityPolicy.get_electrical_weights(priority)

    def generate_candidates(
        self, context: OptimizationContext
    ) -> List[OptimizationCandidate]:
        generator = ElectricalCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> None:
        # Evaluated dynamically on-demand during constraint checks
        pass

    def build_specification(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> ElectricalSystemSpecification:
        dv = candidate.design_variables
        derived = candidate.derived_variables

        pos_score = candidate.objective_scores.get("electrical_score", 0.0)

        reasoning = (
            f"Selected optimal electrical system: Flight Controller={dv['flight_controller_name']}, "
            f"GPS={dv['gps_name']}, Telemetry={dv['telemetry_name']}, Receiver={dv['receiver_name']}, "
            f"Actuators={dv['servo_count']}x {dv['servo_name']}, BEC={dv['bec_name']}, "
            f"Power Module={dv['power_module_name']}, layout={dv['power_distribution_layout']}. "
            f"Sized power budget: {derived.get('total_continuous_power_w', 0.0):.1f} W (peak: {derived.get('total_peak_power_w', 0.0):.1f} W). "
            f"Wiring: {derived.get('wire_gauge_awg')} AWG, Connector: {derived.get('connector_name')}. "
            f"Estimated mass: {derived.get('estimated_electrical_mass_g', 0.0):.1f} g. "
            f"Redundancy level: {derived.get('redundancy_level')}. "
            f"Optimization Score: {pos_score:.4f}."
        )

        return ElectricalSystemSpecification(
            flight_controller_name=dv["flight_controller_name"],
            gps_name=dv["gps_name"],
            compass_name="Matek CAN Compass",  # default standard compass
            telemetry_name=dv["telemetry_name"],
            receiver_name=dv["receiver_name"],
            servo_name=dv["servo_name"],
            servo_count=dv["servo_count"],
            power_module_name=dv["power_module_name"],
            bec_name=dv["bec_name"],
            power_distribution_layout=dv["power_distribution_layout"],
            wire_gauge_awg=derived["wire_gauge_awg"],
            connector_type=derived["connector_name"],
            mission_equipment_name=dv["mission_equipment_name"],
            electrical_power_budget_w=derived["total_continuous_power_w"],
            estimated_electrical_mass_g=derived["estimated_electrical_mass_g"],
            redundancy_level=derived["redundancy_level"],
            optimization_score=pos_score,
            reasoning=reasoning,
        )
