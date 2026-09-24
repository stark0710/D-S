"""
Fixed-Wing Mass Properties Optimization Engine

Subclasses OptimizerBase to orchestrate weight build-up sizing, OEW/MTOW verification,
and 3D mass/inertia tensor specification generation.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.mass_properties.optimization.models import MassPropertiesSpecification
from backend.design.fixed_wing.mass_properties.optimization.result import MassPropertiesOptimizationResult
from backend.design.fixed_wing.mass_properties.optimization.candidate_generator import MassCandidateGenerator
from backend.design.fixed_wing.mass_properties.optimization.candidate_evaluator import MassCandidateEvaluator
from backend.design.fixed_wing.mass_properties.optimization.constraints import build_mass_constraints
from backend.design.fixed_wing.mass_properties.optimization.objective_function import MassObjectiveFunction


class MassPropertiesOptimizer(OptimizerBase):
    """
    Sizes the complete 22-item weight breakdown, OEW, useful loads, inertias,
    and returns a structured MassPropertiesSpecification.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        super().__init__("MassPropertiesOptimizer")
        # Define objective scoring
        self.mass_objective = MassObjectiveFunction(weights)

        # Register constraints
        for check in build_mass_constraints():
            self.constraints.add_constraint(check.__name__, check)

        # Register aggregate objective in base class
        self.objective.add_objective(
            name="mass_score",
            score_fn=lambda cand, ctx: self.mass_objective.evaluate(cand, ctx),
            weight=1.0,
            minimize=False  # We want to maximize the fitness score
        )

    def optimize(self, context: OptimizationContext) -> MassPropertiesOptimizationResult:
        """Runs the optimization search and returns a typed result."""
        res = super().optimize(context)

        # Build diagnostics
        diagnostics = res.diagnostics or {}
        if res.winning_candidate:
            derived = res.winning_candidate.derived_variables
            diagnostics.update({
                "weight_breakdown": derived.get("weight_breakdown"),
                "subsystem_summary": derived.get("subsystem_masses"),
                "constraint_summary": res.rejected_summary,
                "optimization_score": res.winning_candidate.overall_score,
                "execution_time": res.execution_time_seconds,
            })

        return MassPropertiesOptimizationResult(
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
            diagnostics=diagnostics,
        )

    # ------------------------------------------------------------------
    #  OptimizerBase lifecycle hooks
    # ------------------------------------------------------------------

    def initialize(self, context: OptimizationContext) -> None:
        priority = getattr(context, "optimization_priority", None)
        if priority is not None:
            from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
            self.mass_objective.weights = OptimizationPriorityPolicy.get_mass_weights(priority)

    def generate_candidates(
        self, context: OptimizationContext
    ) -> List[OptimizationCandidate]:
        generator = MassCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> None:
        evaluator = MassCandidateEvaluator()
        evaluator.evaluate(candidate, context)

    def build_specification(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> MassPropertiesSpecification:
        dv = candidate.design_variables
        derived = candidate.derived_variables

        pos_score = candidate.objective_scores.get("mass_score", 0.0)

        reasoning = (
            f"Selected optimal mass property configuration: structural margin={dv['structural_margin']}, "
            f"fastener allowance={dv['fastener_allowance']*100.0:.1f}%, paint finish={dv['paint_finish_type']}, "
            f"safety growth margin={dv['safety_growth_margin']*100.0:.1f}%. "
            f"Sized MTOW: {derived.get('mtow_kg', 0.0):.2f} kg (OEW: {derived.get('operating_weight_kg', 0.0):.2f} kg, Empty: {derived.get('empty_weight_kg', 0.0):.2f} kg). "
            f"Fractions: battery={derived.get('battery_fraction', 0.0)*100.0:.1f}%, payload={derived.get('payload_fraction', 0.0)*100.0:.1f}%. "
            f"Inertia Diagonal: Ixx={derived.get('moments_of_inertia')[0]:.4f}, Iyy={derived.get('moments_of_inertia')[1]:.4f}, Izz={derived.get('moments_of_inertia')[2]:.4f} kg*m^2. "
            f"Fitness score: {pos_score:.4f}."
        )

        return MassPropertiesSpecification(
            weight_breakdown=derived["weight_breakdown"],
            empty_weight_kg=derived["empty_weight_kg"],
            operating_weight_kg=derived["operating_weight_kg"],
            maximum_takeoff_weight_kg=derived["mtow_kg"],
            payload_fraction=derived["payload_fraction"],
            battery_fraction=derived["battery_fraction"],
            subsystem_masses=derived["subsystem_masses"],
            moments_of_inertia=derived["moments_of_inertia"],
            optimization_score=pos_score,
            reasoning=reasoning,
            component_masses=derived.get("components", []),
            center_of_gravity=derived.get("center_of_gravity", (0.0, 0.0, 0.0)),
            static_margin=derived.get("static_margin", 0.15),
        )

