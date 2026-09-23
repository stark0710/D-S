"""
Fixed-Wing Center of Gravity (CG) Optimization Engine

Subclasses OptimizerBase to orchestrate battery, payload, and avionics layout sweeps
to establish stable longitudinal static margins.
"""

from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.cg.optimization.models import CGSpecification
from backend.design.fixed_wing.cg.optimization.result import CGOptimizationResult
from backend.design.fixed_wing.cg.optimization.candidate_generator import CGCandidateGenerator
from backend.design.fixed_wing.cg.optimization.candidate_evaluator import CGCandidateEvaluator
from backend.design.fixed_wing.cg.optimization.constraints import build_cg_constraints
from backend.design.fixed_wing.cg.optimization.objective_function import CGObjectiveFunction


class CGOptimizer(OptimizerBase):
    """
    Optimizes avionics, actuator, and payload packaging coordinates to balance the center
    of gravity within stable static margin envelopes.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        super().__init__("CGOptimizer")
        # Define objective scoring
        self.cg_objective = CGObjectiveFunction(weights)

        # Register constraints
        for check in build_cg_constraints():
            self.constraints.add_constraint(check.__name__, check)

        # Register aggregate objective in base class
        self.objective.add_objective(
            name="cg_score",
            score_fn=lambda cand, ctx: self.cg_objective.evaluate(cand, ctx),
            weight=1.0,
            minimize=False  # We want to maximize the fitness score
        )

    def optimize(self, context: OptimizationContext) -> CGOptimizationResult:
        """Runs the optimization search and returns a typed result."""
        res = super().optimize(context)

        # Build diagnostics
        diagnostics = res.diagnostics or {}
        if res.winning_candidate:
            derived = res.winning_candidate.derived_variables
            dv = res.winning_candidate.design_variables
            
            # Find moved components (deviation from initial default layout fractions)
            moved_components = []
            if abs(dv["battery_pos_fraction"] - 0.35) > 0.01:
                moved_components.append("Battery")
            if abs(dv["payload_pos_fraction"] - 0.28) > 0.01:
                moved_components.append("Payload")
            if abs(dv["avionics_pos_fraction"] - 0.38) > 0.01:
                moved_components.append("Avionics")

            diagnostics.update({
                "initial_cg": (round(0.35 * context.requirements.fuselage_result.fuselage_geometry.length_m, 3), 0.0, 0.0),
                "final_cg": derived.get("cg_position"),
                "static_margin": derived.get("static_margin"),
                "moved_components": moved_components,
                "optimization_score": res.winning_candidate.overall_score,
                "execution_time": res.execution_time_seconds,
                "constraint_summary": res.rejected_summary,
            })

        return CGOptimizationResult(
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
            self.cg_objective.weights = OptimizationPriorityPolicy.get_cg_weights(priority)

    def generate_candidates(
        self, context: OptimizationContext
    ) -> List[OptimizationCandidate]:
        generator = CGCandidateGenerator()
        return generator.generate_candidates(context)

    def evaluate_candidate(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> None:
        evaluator = CGCandidateEvaluator()
        evaluator.evaluate(candidate, context)

    def build_specification(
        self, candidate: OptimizationCandidate, context: OptimizationContext
    ) -> CGSpecification:
        derived = candidate.derived_variables
        pos_score = candidate.objective_scores.get("cg_score", 0.0)

        reasoning = (
            f"Optimized packaging layout selected: CG coordinate X={derived.get('cg_position')[0]:.3f}m, "
            f"neutral point={derived.get('neutral_point'):.3f}m, "
            f"longitudinal static stability margin={derived.get('static_margin')*100.0:.1f}%. "
            f"Packaging feasibility preserved, moments balanced. "
            f"Optimization Score: {pos_score:.4f}."
        )

        return CGSpecification(
            cg_position=derived["cg_position"],
            neutral_point=derived["neutral_point"],
            static_margin=derived["static_margin"],
            component_positions=derived["component_positions"],
            moment_summary=derived["moment_summary"],
            cg_envelope=derived["cg_envelope"],
            optimization_score=pos_score,
            reasoning=reasoning,
        )
